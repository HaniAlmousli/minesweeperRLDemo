import minesweeper as ms
import random
import pdb

class RandomAI(ms.GameAI):
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
        print('selecting point ({0},{1})'.format(x, y))
        return x, y

    def update(self, result):
        for position in result.new_squares:
            self.exposed_squares.add((position.x, position.y))


num_games = 100
config = ms.GameConfig(width=10, height=10, num_mines=12)
ai = RandomAI()
viz = ms.GameVisualizer(10)
results = ms.run_games(config, 1, ai, viz)
if results[0].success:
    print('Success!')
else:
    print('Boom!')
print('Game lasted {0} moves'.format(results[0].num_moves))



"""
Beginner       9   9   10
Intermediate   16  16  40
Expert         16  30  99
"""