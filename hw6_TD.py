import random
import json # to save and load into a file
import sys
sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

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
        super(AIPlayer,self).__init__(inputPlayerId, "NEWWW")

        self.flattendList = []

        #A list of utility states
        self.stateList = {}

        #Keeps track of new states we encounter
        self.newStates = 0

        # Discount Factor (Lambda)
        self.discountFactor = .8

        # FIXED alpha learning rate value
        self.alpha = .01

        # Name of file to save utility states to (NOT USING CURRENTLY)
        self.fileName = "util.kaurn19_ nguyenda18"

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
        myTunnel = getConstrList(currentState, self.playerId, (TUNNEL,))[0]

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
        else:
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
        #self.flattenedList = []

        outString = ""

        for list in theList:
            for item in list:
                outString += str(item)

        return outString
##        for list in theList:
##            for value in list:
##                self.flattendList.append(value)
##        return self.flattenedList

    ##
    #findUtil
    #Description: Gets the next move from the Player.
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
    def getNextState(self, currentState, move):
        #make a copy of the current state
        currentState = currentState.fastclone()

        #set the player inventories
        clonedInventory = None
        foeInventory = None
        if currentState.whoseTurn == self.playerId:
            clonedInventory = getCurrPlayerInventory(currentState)
            foeInventory = getEnemyInv(self,currentState)
        else:
            clonedInventory = getEnemyInv(self,currentState)
            foeInventory = getCurrPlayerInventory(currentState)

        #check through all possible moves
        #we predict it will move from start to end
        #we predict it will move closer to tunnel ?
        if move.moveType == MOVE_ANT:
            startPos = move.coordList[0]
            finalPos = move.coordList[-1]

            #take ant from start coord
            antToMove = getAntAt(currentState, startPos)

            #if ant is null, return
            if antToMove is None:
                return currentState

            #change the ant's coords and hasMoved status
            antToMove.coords = finalPos
            antToMove.hasMoved = True

        #check if move is a build move
        elif move.moveType == BUILD:
            startPos = move.coordList[0]
            clonedInventory = currentState.inventories[currentState.whoseTurn]

            if move.buildType == TUNNEL:
                #add new tunnel to inventory
                clonedInventory.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                tunnel = Building(startPos, TUNNEL, self.playerId)
                clonedInventory.constrs.append(tunnel)
            else:
                #add a new ant to our inventory
                clonedInventory.foodCount -= UNIT_STATS[move.buildType][COST]
                antToBuild = Ant(startPos, move.buildType, self.playerId)
                antToBuild.hasMoved = True
                clonedInventory.ants.append(antToBuild)
            #calc based on build,
            #predict to not build so not overbuilding

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
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

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
        #Calculate all the utilities for the states
        self.findUtil(currentState)

        #Initialize the best move as None and best utility as low number (anything lower than -1)
        bestMove = None
        bestUtil = -100

        #Collect all the legal moves we can make
        moves = listAllLegalMoves(currentState)

        #evaluate all the moves based on the utility and find best move from it
        for move in moves:
            nextState = self.getNextState(currentState, move)
            util = -(self.findUtil(currentState, nextState))

            if util > bestUtil:
                bestUtil = util
                bestMove = move

        return bestMove


    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
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
        #make sure to save the utilities to the file after each win
        self.saveFile()
    ##
    #saveFile
    #Description: Saves the current state utilities into a file
    #
    ##
    def saveFile(self):
        file = open(self.fileName, 'w+')
        json.dump(self.stateList, file)
    ##
    #loadFile
    #Description: Loads the file which contains the utilities
    #
    ##
    def loadFile(self):
        file = open(self.fileName, 'r')
        json.load(file)
