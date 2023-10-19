import pygame
from PIL import Image, ImageDraw
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BLACK, WHITE, IMAGE_PATH
import random

class GameMap:
    def __init__(self, image_path):
        self.image_path = image_path
        self.map_image = pygame.image.load(self.image_path)

    def is_wall(self, x, y):
        # Implement this function to check if a given grid cell is a wall
        # Use pygame's Surface.get_at() to check the pixel color
        pixel_color = self.map_image.get_at((x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2))
        return pixel_color == BLACK


class Location:
    def __init__(self, name, top_left, bottom_right):
        self.name = name
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.sub_locations = []

    def add_sub_location(self, sub_location):
        if not self.contains_point(sub_location.top_left[0], sub_location.top_left[1]) or \
        not self.contains_point(sub_location.bottom_right[0], sub_location.bottom_right[1]):
            raise ValueError(f"Sub-location {sub_location.name} is not fully contained within {self.name}.")
        self.sub_locations.append(sub_location)


    def contains_point(self, x, y):
        return self.top_left[0] <= x <= self.bottom_right[0] and self.top_left[1] <= y <= self.bottom_right[1]

    def get_random_point(self):
        return (random.randint(self.top_left[0], self.bottom_right[0]), random.randint(self.top_left[1], self.bottom_right[1]))



def create_map_image():
    # Create a new image with white background
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), color=WHITE)
    draw = ImageDraw.Draw(img)

    # Dimensions for the room: make it a multiple of GRID_SIZE
    room_width = (SCREEN_WIDTH // 3) // GRID_SIZE * GRID_SIZE
    room_height = (SCREEN_HEIGHT // 3) // GRID_SIZE * GRID_SIZE
    room_top_left = (0, 0)
    room_bottom_right = (room_width, room_height)

    # Draw the black-bordered room in the top-left corner
    # Fill the entire room area with black first
    draw.rectangle([room_top_left, room_bottom_right], fill=BLACK)

    # Then fill the inside with white leaving a border of GRID_SIZE
    inner_room_top_left = (room_top_left[0] + GRID_SIZE, room_top_left[1] + GRID_SIZE)
    inner_room_bottom_right = (room_bottom_right[0] - GRID_SIZE, room_bottom_right[1] - GRID_SIZE)
    draw.rectangle([inner_room_top_left, inner_room_bottom_right], fill=WHITE)

    # Create an opening in the bottom middle of the room
    # Adjust opening dimensions to be multiples of GRID_SIZE
    opening_width = GRID_SIZE * 3

    # Calculate starting x-coordinate, rounded to nearest GRID_SIZE
    opening_start_x = ((room_width - opening_width) // 2) // GRID_SIZE * GRID_SIZE
    opening_end_x = opening_start_x + opening_width

    opening_top_left = (opening_start_x, room_bottom_right[1] - GRID_SIZE)
    draw.rectangle([opening_top_left, (opening_end_x, room_bottom_right[1])], fill=WHITE)

    # Draw a light gray grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        draw.line([(x, 0), (x, SCREEN_HEIGHT)], fill=(200, 200, 200))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        draw.line([(0, y), (SCREEN_WIDTH, y)], fill=(200, 200, 200))

    img.save(IMAGE_PATH)
