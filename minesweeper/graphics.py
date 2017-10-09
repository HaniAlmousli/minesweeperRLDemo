import pygame
import time
import os


class GameVisualizer(object):
    TILE_SIZE = 16
    COLOR_GRAY = (189, 189, 189)
    TILES_FILENAME = os.path.join(os.path.dirname(__file__), 'tiles.png')
    TILE_HIDDEN = 9
    TILE_EXPLODED = 10
    TILE_BOMB = 11
    TILE_FLAG = 12
    WINDOW_NAME = 'Minesweeper'

    """
    Construct a graphical game visualizer

    pause: how long to pause between moves in seconds or 'key' for pressing enter to continue
    """
    def __init__(self, pause=3):
        self.pause = pause
        self.game_width = 0
        self.game_height = 0
        self.screen = None
        self.tiles = None

    def start(self, game):
        pygame.init()

        self.game_width = game.width
        self.game_height = game.height

        pygame.display.set_caption(self.WINDOW_NAME)
        screen_width = self.TILE_SIZE * self.game_width
        screen_height = self.TILE_SIZE * self.game_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill(self.COLOR_GRAY)
        self.tiles = self._load_tiles()
        self._draw(game)

    def update(self, game):
        self._draw(game)
        if isinstance(self.pause, int):
            time.sleep(self.pause)
        else:
            input()

    def finish(self):
        pygame.quit()

    def _load_tiles(self):
        image = pygame.image.load(self.TILES_FILENAME).convert()
        image_width, image_height = image.get_size()
        tiles = []
        for tile_x in range(0, int(image_width / self.TILE_SIZE)):
            rect = (tile_x * self.TILE_SIZE, 0, self.TILE_SIZE, self.TILE_SIZE)
            tiles.append(image.subsurface(rect))
        return tiles

    def _draw(self, game):
        for x in range(self.game_width):
            for y in range(self.game_height):
                if not game.exposed[y][x]:
                    if (y, x) in game.flags:
                        tile = self.tiles[self.TILE_FLAG]
                    else:
                        tile = self.tiles[self.TILE_HIDDEN]
                else:
                    if game.board[y][x]:
                        tile = self.tiles[self.TILE_EXPLODED]
                    else:
                        tile = self.tiles[game.counts[y][x]]
                self.screen.blit(tile, (16 * x, 16 * y))
        pygame.display.flip()
