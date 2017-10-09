import unittest
from minesweeper import Game, GameConfig, Position


class MineSweeperTestCase(unittest.TestCase):

    def flip(self, array):
        # boards are stored [x][y] but easier to visualize as [y][x] so we flip dimensions
        return [list(a) for a in zip(*array)]

    def reinit_game(self, game, board):
        game.board = board
        game.counts = [[0 for y in xrange(game.height)] for x in xrange(game.width)]
        game.exposed = [[False for y in xrange(game.height)] for x in xrange(game.width)]
        game.explosion = False
        game.num_exposed_squares = 0
        game.num_moves = 0
        game._init_counts()

    def test_place_mines(self):
        game = Game(GameConfig(100, 100, 800))
        self.assertEqual(800, sum([row.count(True) for row in game.board]))

    def test_init_counts(self):
        game = Game(GameConfig(5, 4, 4))
        board = self.flip([
            [True,  False, False, False, False],
            [False, False, False, True,  False],
            [False, False, False, True,  False],
            [False, False, True,  False, False]
        ])
        counts = self.flip([
            [0, 1, 1, 1, 1],
            [1, 1, 2, 1, 2],
            [0, 1, 3, 2, 2],
            [0, 1, 1, 2, 1]
        ])
        self.reinit_game(game, board)
        self.assertEqual(counts, game.counts)

    def test_select(self):
        game = Game(GameConfig(3, 3, 2))
        board = self.flip([
            [False, True,  False],
            [False, False, False],
            [False, False, True]
        ])
        self.reinit_game(game, board)

        #expose only same square
        result = game.select(1, 1)
        self.assertFalse(result.explosion)
        self.assertEqual(1, len(result.new_squares))
        self.assertEqual(result.new_squares[0], Position(1, 1, 2))

        #expose neighbors
        result = game.select(0, 2)
        self.assertFalse(result.explosion)
        self.assertEqual(3, len(result.new_squares))
        self.assertTrue(Position(0, 2, 0) in result.new_squares)
        self.assertTrue(Position(0, 1, 1) in result.new_squares)
        self.assertTrue(Position(1, 2, 1) in result.new_squares)

        #select square already selected or exposed
        self.assertIsNone(game.select(0, 2))
        self.assertIsNone(game.select(1, 2))

        #select outside the board
        with self.assertRaises(ValueError):
            game.select(2, 3)

        #boom
        result = game.select(1, 0)
        self.assertTrue(result.explosion)

        #select after game over
        with self.assertRaises(ValueError):
            game.select(2, 0)

    def test_is_game_over(self):
        game = Game(GameConfig(3, 3, 1))
        board = self.flip([
            [False, False, True],
            [False, False, False],
            [False, False, False]
        ])
        self.reinit_game(game, board)

        #not over before we start
        self.assertFalse(game.is_game_over())

        #over after explosion
        result = game.select(2, 0)
        self.assertTrue(result.explosion)
        self.assertTrue(game.is_game_over())

        #over when all the squares have been revealed
        self.reinit_game(game, board)
        result = game.select(0, 0)
        self.assertFalse(result.explosion)
        self.assertEqual(8, len(result.new_squares))
        self.assertTrue(game.is_game_over())

    def test_get_state(self):
        game = Game(GameConfig(3, 3, 3))
        board = self.flip([
            [False, False, True],
            [False, False, False],
            [True,  False, True]
        ])
        self.reinit_game(game, board)

        game.select(0, 0)
        expected = self.flip([
          [0,    1,    None],
          [1,    3,    None],
          [None, None, None]
        ])

        state = game.get_state()
        for x in [0, 1, 2]:
            for y in [0, 1, 2]:
                self.assertEqual(expected[x][y], state[x][y])
