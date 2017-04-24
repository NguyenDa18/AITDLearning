__author__ = "Navreen Kaur and Danh Nguyen"

import random
import pickle
import sys
sys.path.append("..")  # so other modules can be found in parent dir
import os.path as filePath
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Building import *
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

# Determines if we keep learning states and updating utils
# Agent has been 'learned' so LEARNING is False
LEARNING = False

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        self.flattendList = []

        #A list of utility states
        self.stateList = {}

        #index of where I am in stateList
        self.utilIndex = None

        #Keeps track of states we have discovered
        self.encounteredStates = 0

        #Keeps track of new states we encounter
        self.newStates = 0

        #Keeps track of games played
        self.gameCount = 0

        #Whether or not first move has been made
        self.firstMove = True

        # Discount Factor (Lambda)
        self.discountFactor = .95

        # FIXED alpha learning rate value
        self.alpha = .01

        # Name of file to save utility states to
        self.fileName = 'kaurn19_nguyenda18_td.utilities'

        #loads file
        print "Loading utilities from file...."
        if filePath.isfile(self.fileName):
            self.stateList = self.loadFile()

        super(AIPlayer,self).__init__(inputPlayerId, "DON GIVA NUXXX!")

    ##
    #consolidateState
    #Description: Given state, compress most significant info into a simple state
    #
    #Parameters:
    #   currentState - the state the game is in
    #
    #Return: The consolidated game state
    def consolidateState(self, currentState):
        me = currentState.whoseTurn

        #Init list to store the consolidated state data
        simpleState = []

        #Init references to player queens, inventory, and food
        myInv = None
        foeInv = None
        if currentState.whoseTurn == self.playerId:
            myInv = getCurrPlayerInventory(currentState)
            foeInv = getEnemyInv(self,currentState)
        else:
            myInv = getEnemyInv(self,currentState)
            foeInv = getCurrPlayerInventory(currentState)

        #record queen locations
        myQueen = myInv.getQueen()
        foeQueen = foeInv.getQueen()


        #record the construct locations
        myTunnel = myInv.getTunnels()#getConstrList(currentState, self.playerId, (TUNNEL,))[0]

        myHill = myInv.getAnthill()

        #Ant lists
        myWorkers = getAntList(currentState, self.playerId, (WORKER,))
        myDrones = getAntList(currentState, self.playerId, (DRONE,))

        # Get our food
        foodList = getConstrList(currentState, None, (FOOD,))
        myFood = []
        for food in foodList:
            if food.coords[1] < 4:
                myFood.append(food)

        #if we won or lost, return True and the number to reward (similar to hasWon function)
        if foeQueen is None or myInv.foodCount >= 11 or len(foeInv.ants) <= 1:
            simpleState.append(['1'])
        elif myQueen is None or foeInv.foodCount <= 11 or len(myInv.ants) <= 1:
            simpleState.append(['-1'])
        else:
            #save information about how much food we have, and if we are carrying
            food = len(myFood)
            simpleState.append(['-.01', myInv.foodCount])

            for ant in myInv.ants:
                if ant.type == WORKER:
                    if ant.carrying:

                        #return if should go to tunnel or anthill
                        targetConstr = myTunnel
                        if stepsToReach(currentState, worker.coords, myHill.coords) < stepsToReach(currentState, worker.coords, myTunnel.coords):
                            targetConstr = myHill
                        else:
                            targetConstr = myTunnel
                        simpleState.append(['-.01', str(targetConstr)])
                    else:
                        # Go the whichever food is closest
                        targetFood = foodList[0]
                        for food in foodList:
                            distToTunnel = stepsToReach(currentState, myTunnel, food.coords)
                            distToHill = stepsToReach(currentState, myHill, food.coords)

                            if stepsToReach(currentState, worker.coords, food.coords) < stepsToReach(currentState, worker.coords, targetFood.coords):
                                targetFood = food
                        simpleState.append(['-.01', str(targetFood)])

        return simpleState

    ##
    #totalAntHealth
    #Description: Finds the value of a player's total ant health
    #
    #Parameters:
    #   currentState -the current state the game is in
    #   playerId -which player we are calculating
    #
    #Return: total ant health of a player
    ##
    def totalAntHealth(self, currentState, playerId):
        antHealth = 0
        for ant in state.inventories[playerId].ants:
            antHealth += ant.health
        return antHealth

    ##
    #reward
    #Description: Calculates the reward based on the state. Returns a 1 if
    #             the game has been won, a -1 if the game has been lost, and
    #             -.01 for everything else.
    #
    #Parameters:
    #   currentState - The state of the current game
    #
    #Return: The reward associated with the state
    def reward(self, simpleState):
        if '1' in simpleState:
            return 1.0
        elif '-1' in simpleState:
            return -1.0
        return -0.01

    ##
    #flattenList
    #Description: Takes a 2D list and turns it into a 1D list so we can use it
    #             to make calculations.
    #             NOTE: Used help from StackOverflow so code is similar
    #
    #Parameters:
    #   theList - The list to flatten
    #
    #Return: The flattened list
    ##
    def flattenList(self, theList):
        outString = ""

        for list in theList:
            for item in list:
                outString += str(item)

        return outString

    ##
    #findUtil
    #Description: Gets the utility of a state
    #
    #Parameters:
    #   currentState - The current state in the game
    #   nextState - The potential states that can occur based on our moves
    #
    #Return: The utilities of the states
    ##
    def findUtil(self, state, nextState = None):
        #calc the utility
        currentList = self.consolidateState(state)
        flatCurrentList = self.flattenList(currentList)

        #if first move then see if the state is in out list:
        if nextState is None:
            if flatCurrentList not in self.stateList:
                self.stateList[flatCurrentList] = 0
        else:
            evalNextState = self.consolidateState(nextState)
            flatNextState = self.flattenList(evalNextState)

            #if we have not seen, add to list, and set utility to zero. Else, we calculate the utility.
            if flatNextState not in self.stateList:
                self.stateList[flatNextState] = 0
            else:
                #TD Learning Equation!
                self.stateList[flatCurrentList] += (self.alpha *\
                (self.reward(flatCurrentList) + self.discountFactor* \
                 self.stateList[flatNextState] - self.stateList[flatCurrentList]))

        return self.stateList[flatCurrentList]

    ##
    # getNextState()
    #
    # Parameters:
    #   currentState -The state of the current game
    #   move -The Move action to be processed
    #
    # Return: A GameState object that represents the prediction of the next state after a move has been made
    ##
    def getNextState(self, state, move):
        #make a copy of the current state
        currentState = state.fastclone()

        #set the player inventories
        cloneInv = None
        foeInv = None
        if currentState.whoseTurn == self.playerId:
            cloneInv = getCurrPlayerInventory(currentState)
            foeInv = getEnemyInv(self,currentState)
        else:
            cloneInv = getEnemyInv(self,currentState)
            foeInv = getCurrPlayerInventory(currentState)

        #check through all possible moves
        if move.moveType == MOVE_ANT:

            startPos = move.coordList[0]
            finalPos = move.coordList[-1]

            ant = getAntAt(currentState, startPos)

            #if ant is null, return
            if ant is None:
                return currentState

            # update the ant's location after the move
            ant.coords = finalPos

            #get reference to potential construct at next position
            construct = getConstrAt(currentState, finalPos)

            # predict moves based on location of ant
            if construct:
                # deal with worker behavior
                if ant.type == WORKER:
                    # if ant is under food, freaking pick it up
                    if construct.type == FOOD:
                        if not ant.carrying:
                            ant.carrying = True
                    elif construct.type == TUNNEL or construct.type == ANTHILL:
                        if ant.carrying:
                            ant.carrying = False
                            cloneInv.foodCount += 1

            # A list of enemy ants coords
            foeAntCoords = [foeAnt.coords for foeAnt in foeInv.ants]

            # list of possible attacks against enemy
            possibleAttacks = []

            for coord in foeAntCoords:
                #calculate manhattan distance towards enemy coords
                if UNIT_STATS[ant.type][RANGE] ** 2 >= abs(ant.coords[0] - coord[0]) ** 2 + abs(ant.coords[1] - coord[1]) ** 2:
                    possibleAttacks.append(coord)

            # attack randomly
            if possibleAttacks:
                #attack and update stats
                foeAnt = getAntAt(currentState, random.choice(possibleAttacks))
                attackStrength = UNIT_STATS[ant.type][ATTACK]

                if foeAnt.health <= attackStrength:
                    foeAnt.health = 0
                    foeInv.ants.remove(foeAnt)
                else:
                    foeAnt.health -= attackStrength

        #check if move is a build move
        elif move.moveType == BUILD:
            startPos = move.coordList[0]
            cloneInv = currentState.inventories[currentState.whoseTurn]

            if move.buildType == TUNNEL:
                #add new tunnel to inventory
                cloneInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                tunnel = Building(startPos, TUNNEL, self.playerId)
                cloneInv.constrs.append(tunnel)
            else:
                #add a new ant to our inventory
                cloneInv.foodCount -= UNIT_STATS[move.buildType][COST]
                antToBuild = Ant(startPos, move.buildType, self.playerId)
                antToBuild.hasMoved = True
                cloneInv.ants.append(antToBuild)
        elif move.moveType == END:
            #increment whose turn to indicate next player to move
            currentState.whoseTurn += 1
            currentState.whoseTurn %= 2

        return currentState

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None

        #Depending on my place in the board save my foe's anthill
        #or tunnel positions
        if (self.playerId == 1):
              foePlayerTunnel = getConstrList(currentState, 0, (TUNNEL,))
              foePlayerHill = getConstrList(currentState, 0, (ANTHILL,))

        elif (self.playerId == 0):
              foePlayerTunnel = getConstrList(currentState, 1, (TUNNEL,))
              foePlayerHill = getConstrList(currentState, 1, (ANTHILL,))

        if currentState.phase == SETUP_PHASE_1:
            return [(2,1), (7,1),
                      (0,1), (1,0), (2,0), (3,0), \
                      (9,0), (9,1), (7,0), (8,0), (9,0)]
        elif currentState.phase == SETUP_PHASE_2:
            moves = []
            for i in range(0,2):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)

                    #Set the move if this space is empty and if the move is
                    #going to take multiple turns to reach the food
                    if currentState.board[x][y].constr == None and (x, y) not in moves and \
                    stepsToReach(currentState, foePlayerTunnel[0].coords, (x,y)) > 4 and \
                    stepsToReach(currentState, foePlayerHill[0].coords, (x,y)) > 4:
                        move = (x, y)
                        #Just need to make the space non-empty.
                        currentState.board[x][y].constr == True

                    #if a calculated food placement cannot be found randomly place
                    #the food (resolves game crashes against Random)
                    elif currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x,y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return None  #should never happen


    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        #Calculate all the utilities for the state
        self.findUtil(currentState)

        #Initialize the best move as None and best utility as low number (anything lower than -1)
        bestMove = None
        bestUtil = -1000

        #Collect all the legal moves we can make
        moves = listAllLegalMoves(currentState)

        currentIndex = None
        if self.utilIndex is not None:
            currentIndex = self.utilIndex

        #evaluate all the moves based on the utility and find best move from it
        for move in moves:
            #process the move on simulated state
            nextState = self.getNextState(currentState, move)

            #get the utility of the current state based on next state
            util = -(self.findUtil(currentState, nextState))

            if util > bestUtil:
                bestUtil = util
                bestMove = move

        #introduce 10% chance of making random mov ein order to explore
        if random.random() < 0.1:
            return moves[random.randint(0, len(moves)-1)]

        return bestMove


    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    #
    #Return: random attack
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):

        # during active TD-learning (this will be disabled
        # when learning has been finished)
        if LEARNING:
            # reset the number of states encountered
            self.statesEncountered = 0

            # reset how many new states were discovered
            self.newStatesFound = 0

            # increment the number of games played
            self.gameCount += 1

            # save the utilities to a file every 50 games
            if self.gameCount % 50 == 0:
                self.saveFile()

        #make sure to save the utilities to the file after each win
        if hasWon:
            self.stateList[self.utilIndex] = 1 #We have won and save the utility
        else:
            self.stateList[self.utilIndex] = -1 #We have lost and save the crappy utility
        self.saveFile()

    ##
    #saveFile
    #Description: Saves the current state utilities into a file
    #
    ##
    def saveFile(self):
        with open("AI/" +self.fileName, 'wb') as file:
            pickle.dump(self.stateList, file, 0)
    ##
    #loadFile
    #Description: Loads the file which contains the utilities
    #
    #Return: the loaded file
    ##
    def loadFile(self):
        with open(self.fileName, 'rb') as file:
            return pickle.load(file)
