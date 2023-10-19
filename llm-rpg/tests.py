import pytest
from game_map import GameMap
from constants import *

def test_game_map_collisions():
    game_map = GameMap(IMAGE_PATH)
    # input(game_map.collisions)
    # Assert that certain cells are walls
    assert game_map.is_wall(0, 0)  # Top-left corner should be a wall
    assert game_map.is_wall(1, 0)  

    # Assert that certain cells are not walls
    # Inside the opening should not be a wall
    assert not game_map.is_wall(11, 19)  
    assert not game_map.is_wall(12, 19) 
    assert not game_map.is_wall(13, 19) 
    # Inside the main area should not be a wall
    assert not game_map.is_wall(4, 4)  
    assert not game_map.is_wall(5, 5)
