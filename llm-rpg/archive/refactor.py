import arcade
import random

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

COLOR_NAMES = {
    arcade.color.BLUE: "Blue",
    arcade.color.RED: "Red"
}

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = arcade.color.GREEN
NPC_RADIUS = 30
NPC_COUNT = 2
MOVE_INTERVAL = 0.5  # Time (in seconds) for each grid move, adjust as needed


BLOCK_COUNT = 10
BLOCK_SIZE = 50

GRID_SIZE = 50  # or whatever size you want your grid to be

# When initializing the position of an NPC or block:
x = random.choice(range(0, SCREEN_WIDTH, GRID_SIZE))
y = random.choice(range(0, SCREEN_HEIGHT, GRID_SIZE))


class Block(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(BLOCK_SIZE, arcade.color.GRAY, outer_alpha=255)
        self.center_x = x
        self.center_y = y

class Brain:
    DIRECTIONS = [
        (1, 0),  # Right
        (-1, 0),  # Left
        (0, 1),  # Up
        (0, -1),  # Down
        (1, 1),  # Up-Right
        (1, -1),  # Down-Right
        (-1, 1),  # Up-Left
        (-1, -1)  # Down-Left
    ]

    def decide(self):
        direction = random.choice(self.DIRECTIONS)
        action = 'pathfind' if random.random() < 0.2 else 'move'
        return action, direction

    

class NPC(arcade.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.color = color
        self.circle = arcade.draw_circle_filled(x, y, NPC_RADIUS, color)
        self.center_x = x
        self.center_y = y
        self.next_decision_time = MOVE_INTERVAL
        self.following_path = False
        self.path = []

        # Manually set the hit box
        half_side = NPC_RADIUS * (2 ** 0.5) / 2  # half side length of square circumscribing the circle
        self.set_hit_box([
            (-half_side, -half_side),
            (-half_side, half_side),
            (half_side, half_side),
            (half_side, -half_side)
        ])

        self.brain = Brain()
        self.next_decision_time = 0
        self.decision = ('move', (0, 0), 0)

    def move(self, delta_time):
        self.next_decision_time -= delta_time

        # Handle collisions and boundaries
        self.handle_collisions_and_boundaries()

        # Decision-making logic
        if self.next_decision_time <= 0:
            self.make_decision()  # Simplify by extracting decision-making logic
            if self.decision[0] == 'move':
                self.handle_move_decision()
            elif self.decision[0] == 'pathfind' or self.following_path:
                self.handle_pathfind_decision()

            self.next_decision_time = MOVE_INTERVAL

    def handle_collisions_and_boundaries(self):
        # Collision and boundary checks here...
        for other_npc in window.npc_list:
            if other_npc != self and self.collides_with_sprite(other_npc):
                # Make both NPCs get a new decision when they collide
                self.make_decision()
                other_npc.make_decision()

        # Keep NPC within screen boundaries
        if self.left < 0:
            self.center_x += GRID_SIZE
        if self.right > SCREEN_WIDTH:
            self.center_x -= GRID_SIZE
        if self.bottom < 0:
            self.center_y += GRID_SIZE
        if self.top > SCREEN_HEIGHT:
            self.center_y -= GRID_SIZE

    def make_decision(self):
        # Centralize decision-making logic
        if not self.following_path:  # Only make a new decision if not currently pathfinding
            self.decision = self.brain.decide()
            color_name = COLOR_NAMES.get(self.color, "Unknown")
            print(f"{color_name} NPC at ({self.center_x}, {self.center_y}) decision: {self.decision}")

    def handle_move_decision(self):
        new_x = self.center_x + self.decision[1][0] * GRID_SIZE
        new_y = self.center_y + self.decision[1][1] * GRID_SIZE
        if not self.will_collide_at(new_x, new_y):
            self.center_x = new_x
            self.center_y = new_y
        else:
            # Re-decide if there's a collision
            self.make_decision()

    def handle_pathfind_decision(self):
        target_npc = self.find_nearest_npc()
        # Check for proximity to the target
        if self.distance_to_other(target_npc) <= GRID_SIZE:
            self.following_path = False
            self.make_decision()
            return

        # Recalculate path only if not currently following a path
        if not self.following_path:
            self.path = self.find_path_to_target(target_npc)
            self.following_path = True

        if self.path:
            next_step = self.path[0]
            new_x = next_step.x * GRID_SIZE
            new_y = next_step.y * GRID_SIZE
            if not self.will_collide_at(new_x, new_y):
                self.center_x = new_x
                self.center_y = new_y
                self.path.pop(0)
                if not self.path:
                    self.following_path = False
            else:
                # Re-decide if there's a collision
                self.following_path = False
                self.make_decision()

    def will_collide_at(self, x, y):
        for other_npc in window.npc_list:
            if other_npc != self and other_npc.center_x == x and other_npc.center_y == y:
                return True
        return False

    def find_nearest_npc(self):
        nearest = None
        nearest_distance = float('inf')
        for npc in window.npc_list:
            if npc != self:
                distance = self.distance_to_other(npc)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest = npc
        return nearest
    
    def get_target_position(self):
        if isinstance(self.target, NPC):
            return self.target.center_x, self.target.center_y
        return self.target

    def distance_to_other(self, other):
        return ((self.center_x - other.center_x) ** 2 + (self.center_y - other.center_y) ** 2) ** 0.5

    def get_direction_to_target(self, target):
        dx = target.center_x - self.center_x
        dy = target.center_y - self.center_y
        magnitude = (dx ** 2 + dy ** 2) ** 0.5
        return dx / magnitude, dy / magnitude

    def find_path_to_target(self, target):
        matrix = [[True for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    
        # Mark blocks as obstacles
        for block in window.block_list:
            matrix[int(block.center_y // BLOCK_SIZE)][int(block.center_x // BLOCK_SIZE)] = False

        grid = Grid(matrix=matrix)
        
        start = grid.node(int(self.center_x // BLOCK_SIZE), int(self.center_y // BLOCK_SIZE))
        
        # Check if target is an NPC or a tuple
        if isinstance(target, tuple):
            end_x, end_y = target
        else:
            end_x, end_y = target.center_x, target.center_y

        # Clamp end_x and end_y within grid boundaries
        end_x = max(0, min(end_x, SCREEN_WIDTH - GRID_SIZE))
        end_y = max(0, min(end_y, SCREEN_HEIGHT - GRID_SIZE))

        end = grid.node(int(end_x // BLOCK_SIZE), int(end_y // BLOCK_SIZE))

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start, end, grid)
        
        return path



    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, NPC_RADIUS, self.color)



class GameWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "NPC Demo with Arcade")
        arcade.set_background_color(BACKGROUND_COLOR)
        
        self.npc_list = []
        colors = [arcade.color.BLUE, arcade.color.RED]  # Add more colors if NPC_COUNT > 2
        for i in range(NPC_COUNT):
            x = random.choice(range(NPC_RADIUS + GRID_SIZE//2, SCREEN_WIDTH - NPC_RADIUS, GRID_SIZE))
            y = random.choice(range(NPC_RADIUS + GRID_SIZE//2, SCREEN_HEIGHT - NPC_RADIUS, GRID_SIZE))
            npc = NPC(x, y, colors[i])
            self.npc_list.append(npc)

        self.block_list = arcade.SpriteList()
        # Commenting out blocks for now
        # for _ in range(BLOCK_COUNT):
        #     x = random.randint(BLOCK_SIZE / 2, SCREEN_WIDTH - BLOCK_SIZE / 2)
        #     y = random.randint(BLOCK_SIZE / 2, SCREEN_HEIGHT - BLOCK_SIZE / 2)
        #     block = Block(x, y)
        #     self.block_list.append(block)

    def on_draw(self):
        arcade.start_render()
        self.block_list.draw()
        for npc in self.npc_list:
            npc.draw()

    def update(self, delta_time):
        for npc in self.npc_list:
            npc.move(delta_time)

if __name__ == "__main__":
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()