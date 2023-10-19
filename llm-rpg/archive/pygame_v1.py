import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
TILES_X = SCREEN_WIDTH // TILE_SIZE
TILES_Y = SCREEN_HEIGHT // TILE_SIZE

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Top Down RPG')

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.occupied = False

class TerrainObject:
    def __init__(self, x, y):
        self.tile = Tile(x, y)
        self.tile.occupied = True

class Movable:
    def __init__(self, x, y):
        self.tile = Tile(x, y)
        self.dx = 0
        self.dy = 0

    def move(self, dx, dy, tiles):
        potential_tile = tiles[self.tile.y + dy][self.tile.x + dx]
        if not potential_tile.occupied:
            self.tile.occupied = False
            self.tile = potential_tile
            self.tile.occupied = True

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.tile.rect)
 
