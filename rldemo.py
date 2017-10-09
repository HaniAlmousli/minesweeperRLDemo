from minesweeper import *
import random
import pdb
from Agent import *

ITERATION_COUNT=int(2e7)
WIDTH =10
HEIGHT=10
MINES_COUNT=12

dictInfo = {
	'discountFactor':0.9,
	'memorySize':1000000,
	'alpharidge':0.001,
	'epsilonProb':0.2,
	'savePath': "C:\\Code\\Python\\minesweeper\\minesweeper-master - Phase1 - Optim\\res\\model.pkl"
}
 
results = []
config = GameConfig(width=WIDTH, height=HEIGHT, num_mines=MINES_COUNT)
game = Game(config)
ai= Agent(config,game,dictInfo)
stop=False

for x in range(ITERATION_COUNT):
    isExplosion = ai.MoveToNextState()
    if isExplosion:
        # print("GAME LOST AFTER "+str(game.num_moves)+" . Iteration: "+str(x))
        game = Game(config)
        ai.ResetAgentState(game)
    else :
    	 if game.num_exposed_squares == game.num_safe_squares:
    	 	ai.COUNTERWINS +=1
         # if np.sum(np.isnan(np.asarray(game.get_state()).astype(float)))== MINES_COUNT:
         	# print("*********** WELL DONE ***************")
         	# pdb.set_trace()

