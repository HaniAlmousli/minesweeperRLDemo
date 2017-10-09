import random
from abc import ABCMeta, abstractmethod
import pdb
from minesweeper import *
import pickle
import numpy as np
from sklearn.linear_model import Ridge
from itertools import compress
import cProfile

class Agent(GameAI):

    def __init__(self, config,game,inputDic):

        self.COUNTERMEM = 0
        self.COUNTERWINS = 0
        self.width = config.width
        self.height = config.height
        self.exposed_squares = set()
        self.exposed_squares.clear()
        #
        self.counterUpdates = 0 #How many times the lm was trained
        self.config=config
        self.game=game
        self.rng = np.random.RandomState(123)
        self.actionsId   = np.arange(self.config.width * self.config.height)
        self.W = self.rng.uniform(low=-1e-5,high=1e-5,
                 size=[self.config.width * self.config.height, 
                        self.config.width * self.config.height * self.config.cellsStateCount])
        self.b = np.zeros([self.config.width * self.config.height])
        #Convert the minesweeper into one hot big state vector (every cell has 10 one hot rep)
        cells = np.reshape(np.asarray(self.game.get_state()),-1)
        cells[np.isnan(cells.astype(float))]=9
        self.currentState = np.reshape(np.eye(self.config.cellsStateCount)[np.asarray(cells,'int')],[-1])
        #Extarct Info from inputDic
        self.inputDic = inputDic
        self.discountFactor = inputDic['discountFactor']
        self.epsilonProb    = inputDic['epsilonProb']
        self.memorySize     = inputDic['memorySize']
        self.alpharidge     = inputDic['alpharidge']
        self.savePath     = inputDic['savePath']
        #Add the data for lm
        self.lstState =np.zeros([self.memorySize,self.currentState.shape[0]])
        self.lstAction=np.zeros([self.memorySize])
        self.lstTarget=np.zeros([self.memorySize])



    def MoveToNextState(self):
        """
        Move to the next state from the current
        This returns if there was explosion or not in order to reset the game from the controller.
        """
        self.lstState[self.COUNTERMEM,:] = self.currentState
        #Choose action and play it
        result,selectedAction = self.selectActionUsingEpsilonGreedy(self.currentState)
        # print(selectedAction)
        if not result.explosion:
            self.update(result)
            # pdb.set_trace()
            self.game.set_flags(self.get_flags())
        self.lstAction[self.COUNTERMEM] = selectedAction
        #Get the new state
        cells2 = np.reshape(np.asarray(self.game.get_state()),-1)
        cells2[np.isnan(cells2.astype(float))]=9
        if result.explosion:
            self.lstTarget[self.COUNTERMEM] = result.reward
        else:
            self.currentState = np.reshape(np.eye(self.config.cellsStateCount)[np.asarray(cells2,'int')],[-1])
            maxQ = self.qFunction(self.currentState)
            self.lstTarget[self.COUNTERMEM] = result.reward + self.discountFactor * maxQ
        self.COUNTERMEM += 1
        if self.COUNTERMEM==self.memorySize:
            # print(self.COUNTERMEM)
            self.updateParams()
            #reset memory (**MIGHT KEEP SOME OF THE VALUES LATER**)
            # self.lstTarget=[]
            # self.lstAction=[]
            # self.lstState =[]
            self.COUNTERMEM = 0
        # pdb.set_trace()

        return result.explosion
    def selectActionUsingEpsilonGreedy(self,currentState):
        Q = np.dot(self.W,currentState)+self.b
       
        # zipped = list(zip(Q,self.actionsId))
        # zipped.sort(key = lambda t: t[0],reverse=True)
        # q,aIds = zip(*zipped)
        takeMaxAction = self.rng.binomial(n=1,p=1-self.epsilonProb,size=1)[0]
        # print(takeMaxAction)
        selectedActionId = self.getValidAction(Q,takeMaxAction)
        # pdb.set_trace()
        # print(selectedActionId)
        coords = int(selectedActionId/self.config.width),int(selectedActionId%self.config.width)
        # print(coords)
        result = self.game.select(*coords)
       
        return result,selectedActionId
        # currentState,actionId,reward,nextState,nextStateIndex = self.pickActionFromEnv(aIds,takeMaxAction)

    def getValidAction(self,Q,maxAction):
        expo = np.reshape(np.asarray(self.game.exposed),-1)
        tmp = np.asarray(np.logical_not(expo),'float')
        tmp[tmp==0] = -np.inf
        Q[expo] = np.abs(Q[expo])
        if maxAction:
            validActionsQ = tmp*Q
            # pdb.set_trace()
            return np.argmax(validActionsQ)
        else:
            indices=np.arange(len(self.actionsId))
            self.rng.shuffle(indices)
            counter=0
            while tmp[indices[counter]]==-np.inf:      
                counter += 1
            # pdb.set_trace()
            return indices[counter]

    def qFunction(self,currentState):
        """
        Get The max Q Value using the best action
        """
        # counter=0
        # Q = np.dot(self.W,currentState)+self.b
        # zipped = list(zip(Q,self.actionsId))
        # zipped.sort(key = lambda t: t[0],reverse=True)
        # q,aIds = zip(*zipped)
        # row = int(aIds[counter]/self.config.width)
        # col = int(aIds[counter]%self.config.width)
        # while self.game.IsActionValid(row,col) == False:
        #     counter+=1
        #     row = int(aIds[counter]/self.config.width)
        #     col = int(aIds[counter]%self.config.width)
        # return q[counter]
        Q = np.dot(self.W,currentState)+self.b
        expo = np.reshape(np.asarray(self.game.exposed),-1)
        tmp = np.asarray(np.logical_not(expo),'float')
        tmp[tmp==0] = -np.inf
        Q[expo] = np.abs(Q[expo])
        validActionsQ = tmp*Q
        return np.max(validActionsQ)

    def ResetAgentState(self,game):
        """
        This is called when a game reaches end and we need to start a new game. The new game is passed as a param
        """
        self.game=game
        #Convert the minesweeper into one hot big state vector (every cell has 10 one hot rep)
        cells = np.reshape(np.asarray(self.game.get_state()),-1)
        cells[np.isnan(cells.astype(float))]=9
        self.currentState = np.reshape(np.eye(self.config.cellsStateCount)[np.asarray(cells,'int')],[-1])

    def updateParams(self):
        print("UPDATING Model")
        selectedActions= np.asarray(self.lstAction)
        for k in range(len(self.actionsId)):
            select = selectedActions==k  
            A = self.lstState[select]             
            b = self.lstTarget[select]

            if A.shape[0]>0:
                clf = Ridge(alpha=self.alpharidge)
                try:
                    #pdb.set_trace()
                    res= clf.fit(A, b.flatten())                    
                    self.W[k,:]   = res.coef_
                    self.b[k]     = res.intercept_
                except:
                    pdb.set_trace()
        #print("******************************")
        self.SaveParams()   
        print("MODEL WAS SAVED")   
        # pdb.set_trace()      
        self.counterUpdates += 1
        self.epsilonProb =np.maximum(0,self.epsilonProb-0.02) 
        # self.alpharidge = np.minimum(0.02,self.alpharidge+0.02) 
        print(self.COUNTERWINS)
        self.COUNTERWINS = 0


    def update(self, result):
        for position in result.new_squares:
            self.exposed_squares.add((position.x, position.y))

    def next(self):
        cells = np.reshape(np.asarray(self.game.get_state()),-1)
        cells[np.isnan(cells.astype(float))]=9
        currentState = np.reshape(np.eye(self.config.cellsStateCount)[np.asarray(cells,'int')],[-1])
        counter=0
        Q = np.dot(self.W,currentState)+self.b
        zipped = list(zip(Q,self.actionsId))
        zipped.sort(key = lambda t: t[0],reverse=True)
        q,aIds = zip(*zipped)
        row = int(aIds[counter]/self.config.width)
        col = int(aIds[counter]%self.config.width)
        while self.game.IsActionValid(row,col) == False:
            counter+=1
            row = int(aIds[counter]/self.config.width)
            col = int(aIds[counter]%self.config.width)
        return row,col

    def SaveParams(self):
        pickle.dump([[self.W,self.b],
                      [self.config,self.game,self.inputDic]  ],open(self.savePath+str(self.COUNTERWINS),'wb' ))

    def LoadParams(self, params):
        self.W = params[0]
        self.b = params[1]

def LoadModel(path):
    params, extraParams = pickle.load(open(path,'rb'))
    agent = Agent(extraParams[0],extraParams[1],extraParams[2])
    agent.LoadParams(params)
    return agent