import pygame
from brain import Brain  # This is the decision-making logic which we'll define later
from globals import NPC_REGISTRY
from constants import GRID_SIZE, COLORS

class NPC:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.brain = Brain(self)
        NPC_REGISTRY.append(self)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))


    def move(self, game_map):
        if self.brain.target:
            target_position = self.brain.target['data']
            # Check if we're adjacent to our target NPC
            if self.brain.target['type'] == 'npc':
                target = self.brain.target['npc']
                target_distance = abs(self.x - target.x) + abs(self.y - target.y)
                if target_distance == 1:
                    self.brain.target = None
                    self.brain.path = None
                    print(f"NPC {COLORS[self.color]} has reached its target!")
                    return

        # Check if the next step in the path is blocked by another NPC
        if self.brain.path:
            next_step = self.brain.path[0]
            if (next_step[0], next_step[1]) in [(npc.x, npc.y) for npc in NPC_REGISTRY if npc != self]:
                # If blocked, discard the current path to force a re-evaluation
                self.brain.path = None
                self.brain.determine_path((self.x, self.y), game_map)  # Re-determine the path immediately


        
        if not self.brain.target or not self.brain.path:
            self.brain.choose_target(game_map, NPC_REGISTRY)
            self.brain.determine_path((self.x, self.y), game_map)
        elif self.brain.target_has_moved_significantly(target_position): # could it get to here without target_position being defined?
            self.brain.determine_path((self.x, self.y), game_map)
            self.brain.path.pop(0) # Remove the first step in the path, since it's the current position

        # Take the next step towards the target
        if self.brain.path:
            next_step = self.brain.path.pop(0)
            self.x, self.y = next_step
            if not self.brain.path:
                self.brain.target = None
                print(f"NPC {COLORS[self.color]} has reached its target ({next_step})!")



