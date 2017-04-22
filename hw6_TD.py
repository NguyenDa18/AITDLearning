__author__ = "Danh Nguyen and Navreen Kaur"

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
        super(AIPlayer,self).__init__(inputPlayerId, "Don Giva Nux")

        #A list of utility states
        self.stateList = {}

        #Keeps track of new states we encounter
        self.newStates = 0

        # Discount Factor (Lambda)
        self.discountFactor = .8

        # FIXED alpha value
        self.alpha = .01

        # Name of file to save util states to (NOT USING CURRENTLY)
        self.fileName = "util.kaurn19_ nguyenda18"


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
    #consolidateState
    #Description: Given state, compress most significant info into a few states
    #
    #Parameters:
    #   currentState - the state the game is in
    #
    #Return: List containing the consolidated state
    def consolidateState(self, currentState):
        #Define player IDs
        me = PLAYER_ONE
        foe = PLAYER_TWO
        if currentState.whoseTurn == PLAYER_TWO:
            me = PLAYER_TWO
            foe = PLAYER_ONE


        #record the food and construct locations
        myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        myHill = myInv.getAnthill()

        #Ant lists
        myWorkers = getAntList(currentState, me, (WORKER,))
        myDrones = getAntList(currentState, me, (DRONE,))


        #Init list to store the consolidated state data
        simpleState = []

        #Init references to player queens, inventory, and food
        myInv = state.inventories[me]
        foeInv = state.inventories[foe]

        myQueen = myInv.getQueen()
        foeQueen = foeInv.getQueen()

        # Get our food
        foodList = getConstrList(state, None, (FOOD,))
        myFood = []
        for food in foodList:
            if food.coords[1] < 4:
                myFood.append(food)

        #if we won or lost, return True and the number to reward (similar to hasWon function)
        if foeQueen is None or myInv.foodCount >= 11 or len(foeInv.ants) <= 1:
            simpleState.append(['1']) #idk if to add TRUE OR NOT
        elif myQueen is None or foeInv.foodCount <= 11 or len(myInv.ants) <= 1:
            simpleState.append(['-1']) #same here
        else:
            #save information about how much food we have, and if we are carrying
            food = len(myFood)
            simpleState.append(['-.01', food])

            for ant in myInv.ants:
                if ant.type == WORKER:
                    if ant.carrying:
                        #return if should go to tunnel or anthill
                        targetConstr = myTunnel
                        if approxDist(worker.coords, myTunnel.coords) > approxDist(worker.coords, myAnthill.coords):
                            targetConstr = myAnthill
                        simpleState.append(['-.01', str(targetConstr)])
                    else:
                        # Go to whichever food is closest
                        targetFood = foodList[0]
                        for food in foodList:
                            # if approxDist(worker.coords, food.coords) < approxDist(worker.coords, targetFood.coords):
                            #     targetFood = food

                            if (stepsToReach(currentState, worker.coords, food.coords) < stepsToReach(currentState, worker.coords, targetFood.coords)):
                                targetFood = food



                        simpleState.append(['-.01', str(targetFood)])

        return simpleState

    ##
    # rewardFunction
    #
    #
    # Returns: 1.0 = WON, -1.0 = LOST, -0.01 = ANYTHING ELSE
    ##
    def reward(self, simpleState):
        if '1' in simpleState:
            return 1.0
        elif '-1' in simpleState:
            return -1.0
        else:
            return -0.01


    ##
    # flatten list method: we need to flatten our 2d list in order to use
    # for calcuations
    # credit: used code from online on stackoverflow
    # NOT SURE IF HAD TO CONVERT TO STRING,
    ##
    def flattenList(self, theList):
        flattenedList = []

        for list in theList:
            for value in list:
                flattendList.append(val)
        return flattenedList

    ##
    # findUtil
    # adds to the util list (self.stateList)
    # make sure to set nextState to none because that is intializing first state
    # NOT COMPLETE
    ##
    def findUtil(self, state, nextState = None):
        #calc the util
        currentList = self.consolidateState(state)
        flatCurrentList = self.flattenList(evalList)

        #if first move then see if the state is in out list :
        if nextState is None:
            return
        else:
            evalNextState = self.consolidateState(state)
            flatNextState = self.flattenList(evalNextState)

            #if we have not seen, add to list, and set util to zero
            #else calc the util

            if flatNextState not in self.stateList:
                self.stateList[flatNextState] = 0
            else:
                self.stateList[flatCurrentList] += (self.alpha *
                (self.reward(flatCurrentList) + self.discountFactor*
                 self.stateList[flatNextState] - self.stateList[flatCurrentState]))
        return #self.stateList[flatCurrentState)


    ##
    # getNextState()
    #
    # (prediction) - USE OUR EVAL METHOD TO PREDICT WHAT MAY HAPPEN
    #
    #
    #
    def getNextState(self, currentState, move):
        currentState = currentState.fastclone()

        #check through all possible moves
        if move.moveType == MOVE_ANT:
            #we predict it will move from start to end
            #we predict it will move closer to tunnel ?
            nextMoveAnt = getAntAt(currentState, startPos)
            nextMoveAnt.hasMoved = True

        return currentState



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
        moves = listAllLegalMoves(currentState)
        return moves[random.randint(0,len(moves) - 1)]

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
    # saveFile - saves utils into a file
    #
    #
    def saveFile(self):
        file = open(fileName, 'w+')
        json.dump(self.stateList, file)
    ##
    # loadFile - loads the utils from the file
    #
    def loadFile(self):
        file = open(fileName, 'r')
        json.load(file)
