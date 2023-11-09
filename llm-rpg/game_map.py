import pygame
from PIL import Image, ImageDraw
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BLACK, WHITE, IMAGE_PATH
import random
from typing import List, Union, Tuple

class GameMap:
    def __init__(self, image_path: str, init_locations: bool=True):
        self.image_path = image_path
        self.map_image = pygame.image.load(self.image_path)
        if init_locations:
            self.village, self.reds_house, self.blue_house, self.shop = initialize_locations()

    def is_wall(self, x: int, y: int) -> bool:
        # Implement this function to check if a given grid cell is a wall
        # Use pygame's Surface.get_at() to check the pixel color
        pixel_color = self.map_image.get_at((x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2)) #ERROR: IndexError: pixel index out of range 
        return pixel_color == BLACK

    def get_current_location(self, x: int, y: int) -> str:
        """Retrieve the current location as a string based on coordinates."""
        return self.village.get_current_location(x, y)
    
    def get_available_locations(self, x: int, y: int) -> List['Location']:
        """Get a list of available locations the NPC can move to based on its coordinates."""
        current_loc_string = self.get_current_location(x, y)
        most_specific_loc_name = current_loc_string.split(':')[-1]  # Get the most specific location's name
        current_location = self._find_location_by_name(most_specific_loc_name)
        return current_location.get_available_locations()
    
    def _find_location_by_name(self, name: str, location: 'Location' = None) -> Union['Location', None]:
        """Recursively find a location by its name."""
        if location is None:
            location = self.village

        if location.name == name:
            return location

        for sub_location in location.sub_locations:
            found_loc = self._find_location_by_name(name, sub_location)
            if found_loc:
                return found_loc

        return None


class Location:
    def __init__(self, name: str, top_left: Tuple[int, int], bottom_right: Tuple[int, int], parent: 'Location' = None):
        self.name = name
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.sub_locations: List[Location] = []

        self.parent = parent

    def add_sub_location(self, sub_location: 'Location'):
        """Add a sub-location to the current location."""
        if not self.contains_point(sub_location.top_left[0], sub_location.top_left[1]) or \
        not self.contains_point(sub_location.bottom_right[0], sub_location.bottom_right[1]):
            raise ValueError(f"Sub-location {sub_location.name} is not fully contained within {self.name}.")
        sub_location.parent = self  # Set the parent for the sub-location
        self.sub_locations.append(sub_location)

    def get_current_location(self, x: int, y: int) -> str:
        """Retrieve the current location's name or its hierarchy based on coordinates."""
        if not self.contains_point(x, y):
            return ""

        for sub_location in self.sub_locations:
            specific_location = sub_location.get_current_location(x, y)
            if specific_location:
                return f"{self.name}:{specific_location}"

        return self.name
    
    def get_available_locations(self) -> List['Location']:
        """Retrieve available locations the NPC can move to from the current position."""
        available = []

        if self.parent:
            available.extend([loc for loc in self.parent.sub_locations if loc.name != self.name])
            available.append(self.parent)

        available.extend(self.sub_locations)

        return available
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is contained within the location boundaries."""
        return self.top_left[0] <= x <= self.bottom_right[0] and self.top_left[1] <= y <= self.bottom_right[1]

    def get_random_point(self, game_map: 'GameMap') -> Tuple[int, int]:
        """Get a random point within the location boundaries that isn't a wall."""
        while True:
            x = random.randint(self.top_left[0], self.bottom_right[0])
            y = random.randint(self.top_left[1], self.bottom_right[1])
            if not game_map.is_wall(x, y):
                return (x, y)



def draw_room(draw, room_top_left, room_bottom_right, door_wall="bottom"):
    # Draw the black-bordered room
    draw.rectangle([room_top_left, room_bottom_right], fill=BLACK)

    # Fill the inside with white leaving a border of GRID_SIZE
    inner_room_top_left = (room_top_left[0] + GRID_SIZE, room_top_left[1] + GRID_SIZE)
    inner_room_bottom_right = (room_bottom_right[0] - GRID_SIZE, room_bottom_right[1] - GRID_SIZE)
    draw.rectangle([inner_room_top_left, inner_room_bottom_right], fill=WHITE)

    # Define the opening dimensions
    room_width = room_bottom_right[0] - room_top_left[0]
    room_height = room_bottom_right[1] - room_top_left[1]
    opening_width = GRID_SIZE * 3

    # Calculate opening position based on the specified wall
    if door_wall == "bottom":
        opening_start_x = room_top_left[0] + ((room_width - opening_width) // 2)
        opening_end_x = opening_start_x + opening_width
        opening_top_left = (opening_start_x, room_bottom_right[1] - GRID_SIZE)
        opening_bottom_right = (opening_end_x, room_bottom_right[1])
    elif door_wall == "top":
        opening_start_x = room_top_left[0] + ((room_width - opening_width) // 2)
        opening_end_x = opening_start_x + opening_width
        opening_top_left = (opening_start_x, room_top_left[1])
        opening_bottom_right = (opening_end_x, room_top_left[1] + GRID_SIZE)
    # ... Add conditions for "left" and "right" if needed

    # Draw the opening
    draw.rectangle([opening_top_left, opening_bottom_right], fill=WHITE)


def create_map_image():
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), color=WHITE)
    draw = ImageDraw.Draw(img)

    room_width = (SCREEN_WIDTH // 3) // GRID_SIZE * GRID_SIZE
    room_height = (SCREEN_HEIGHT // 3) // GRID_SIZE * GRID_SIZE

    # Top-left room with bottom opening
    draw_room(draw, (0, 0), (room_width, room_height), "bottom")

    # Top-right room with bottom opening
    draw_room(draw, (SCREEN_WIDTH - room_width, 0), (SCREEN_WIDTH, room_height), "bottom")

    # Bottom-left room with top opening
    draw_room(draw, (0, SCREEN_HEIGHT - room_height), (room_width, SCREEN_HEIGHT), "top")

    # Draw the grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        draw.line([(x, 0), (x, SCREEN_HEIGHT)], fill=(200, 200, 200))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        draw.line([(0, y), (SCREEN_WIDTH, y)], fill=(200, 200, 200))

    img.save(IMAGE_PATH)


def initialize_locations():
    # Main location that covers the entire map
    village = Location("Village", (0,0), (SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE))

    # Constants for easy computation
    room_width_units = SCREEN_WIDTH // 3 // GRID_SIZE
    room_height_units = SCREEN_HEIGHT // 3 // GRID_SIZE

    # Red's House (Top-left room)
    reds_house = Location("Red's House", (1, 1), (room_width_units - 1, room_height_units - 1))

    reds_entrance = Location("Entrance to Red's House", (2, room_height_units - 4), (4, room_height_units - 2))
    reds_bedroom = Location("Red's Bedroom", (room_width_units - 4, 1), (room_width_units - 2, 3))

    reds_house.add_sub_location(reds_entrance)
    reds_house.add_sub_location(reds_bedroom)

    # Blue's House (Top-right room)
    blue_house = Location("Blue's House", (room_width_units * 2 + 1, 1), (SCREEN_WIDTH // GRID_SIZE - 1, room_height_units - 1))
    blue_entrance = Location("Entrance to Blue's House", (room_width_units * 3 - 4, room_height_units - 4), (room_width_units * 3 - 2, room_height_units - 2))
    blue_house.add_sub_location(blue_entrance)

    # Shop (Bottom-left room)
    shop = Location("Shop", (1, room_height_units * 2 + 1), (room_width_units - 1, SCREEN_HEIGHT // GRID_SIZE - 1))
    shop_entrance = Location("Entrance to Shop", (2, room_height_units * 2 + 1), (4, room_height_units * 2 + 3))
    shop.add_sub_location(shop_entrance)

    # Add all the main locations as sub-locations to the village
    village.add_sub_location(reds_house)
    village.add_sub_location(blue_house)
    village.add_sub_location(shop)

    return village, reds_house, blue_house, shop
