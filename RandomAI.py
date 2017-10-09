import random
from abc import ABCMeta, abstractmethod
import pdb
from minesweeper import *
from bokeh.plotting import figure, show, output_file
import numpy as np
from sklearn.linear_model import Ridge
from itertools import compress
import matplotlib.pyplot as plt

class RandomAI(GameAI):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.exposed_squares = set()

    def init(self, config):
        self.width = config.width
        self.height = config.height
        self.exposed_squares.clear()
    def next(self):
        # pdb.set_trace()
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.exposed_squares:
                break
        # print('selecting point ({0},{1})'.format(x, y))
        return x, y

    def update(self, result):
        for position in result.new_squares:
            self.exposed_squares.add((position.x, position.y))

GAMES_COUNT=2000
WIDTH =10
HEIGHT=10
MINES_COUNT=12

ai = RandomAI()
config = GameConfig(width=WIDTH, height=HEIGHT, num_mines=MINES_COUNT)
game = Game(config)
viz = None#GameVisualizer(10)

counter=0
lstSteps=[]
counterWins=0

while counter <GAMES_COUNT:
    stepsCount=0
    game = Game(config)
    ai.init(config)
    ai.game= gameif viz: viz.start(game)
    
    while not game.is_game_over():
        # pdb.set_trace()
        coords = ai.next()
        result = game.select(*coords)
        if result is None:
            continue
        if not result.explosion:
            stepsCount+=1
            ai.update(result)
            game.set_flags(ai.get_flags())
            if game.num_exposed_squares == game.num_safe_squares:
                print("HORRRRRRRRRRRAAAY")
                if viz: viz.update(game)
                # pdb.set_trace()
                counterWins+=1
        else:
            lstSteps.append(stepsCount)
            # print("EXPLOSION")
        # print(np.asarray(game.get_state()))
        # print("\n")
        if viz: viz.update(game)
    if viz: viz.finish()
    counter+=1


# plt.hist(lstSteps,normed=0,bins=np.max(lstSteps),edgecolor='black')
# plt.show()
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
p1 = figure(tools=TOOLS, toolbar_location="above",
    title="Random AI (GAMES_COUNT: ) "+str(GAMES_COUNT)+" . " +str(counterWins) +" Wins.",
    logo="grey",background_fill_color="#E8DDCB")
hist, edges = np.histogram(np.asarray(lstSteps), density=False, bins=np.max(lstSteps))
p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],fill_color="#036564", line_color="#033649")
p1.legend.location = "center_right"
p1.legend.background_fill_color = "darkgrey"


show(p1)

# pdb.set_trace()