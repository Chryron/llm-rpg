import pygame
from brain import Brain  # This is the decision-making logic which we'll define later
from globals import NPC_REGISTRY
from constants import GRID_SIZE, COLORS
from collections import deque
import random

class Action:
    def __init__(self, action_type, target=None, message=None, end=False):
        self.type = action_type  # 'pathfind', 'converse'
        self.target = target
        self.message = message
        self.end = end

class NPC:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.brain = Brain(self)
        NPC_REGISTRY.append(self)
        self.hunger = 0
        self.action_queue: deque = deque()  # Queue for actions
        self.paused_action = None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def _execute_pathfind(self, action, game_map):
        target = action.target
        if not self.brain.path:
            self.brain.determine_path((self.x, self.y), game_map)
            if not self.brain.path:
                self.action_queue.popleft()
                self.resume_previous_action()
                return

        if self.brain.target_has_moved_significantly():
            self.brain.determine_path((self.x, self.y), game_map)
        # Check if next step is blocked by another NPC and recompute path if necessary
        
        next_step = self.brain.path.pop(0)
        
        if (next_step[0], next_step[1]) in [(npc.x, npc.y) for npc in NPC_REGISTRY if npc != self]:
            # another npc in next step.
            self.brain.path = None
            self.brain.determine_path((self.x, self.y), game_map)
            next_step = self.brain.path.pop(0)
            
            if (next_step[0], next_step[1]) in [(npc.x, npc.y) for npc in NPC_REGISTRY if npc != self]:
                pass
            else:
                self.x, self.y = next_step
        else:
            self.x, self.y = next_step
        
        if isinstance(target, NPC):
            target_distance = abs(self.x - target.x) + abs(self.y - target.y)
            if target_distance<2:
                self.action_queue.popleft()
                # print(f"NPC {COLORS[self.color]} has reached its target ({next_step})!")
                self.resume_previous_action()
                return
        # Move to the next position in the path
        if not self.brain.path:  
            self.action_queue.popleft()
            # print(f"NPC {COLORS[self.color]} has reached its target ({next_step})!")
            self.resume_previous_action()
            return
        

    def queue_action(self, action_type, target=None, message=None, end=False):
        """Queue an action for the NPC."""
        action = Action(action_type, target=target, message=message, end=end)
        if self.action_queue:
            print("jelp")
        self.action_queue.append(action)

    def resume_previous_action(self):
        if self.paused_action:
            if self.action_queue:
                print('help')
            self.action_queue.append(self.paused_action)
            self.paused_action = None
    def _execute_converse(self, action, game_map):
        target_npc = action.target
        if target_npc:
            target_distance = abs(self.x - target_npc.x) + abs(self.y - target_npc.y)
            if target_distance > 1:
                # Save the converse action temporarily
                self.paused_action = self.action_queue.popleft()
                # If they are not adjacent, pathfind to the target
                self.queue_action('pathfind', target=target_npc)
                return
            else:
                if not self.action_queue[0].end:
                    if not target_npc.paused_action and target_npc.action_queue:
                        target_npc.paused_action = target_npc.action_queue.popleft()  # Pause target's current action
                    target_npc.queue_action('converse', message=random.choice(['Hello', 'How are you?', 'Nice to meet you']), target=self, end=True)  # Force target to converse
                
                print(f"NPC {COLORS[self.color]} says: {action.message}")
                self.action_queue.popleft()  # Dequeue the current action
                # End the conversation for both NPCs
                self.end_conversation(game_map)
                # target_npc.end_conversation(game_map)

    def end_conversation(self, game_map):
        if self.paused_action:
            self.resume_previous_action()
        else:
            if not self.action_queue:
                self.brain.decide_action(game_map, NPC_REGISTRY)

    def move(self, game_map):
        # Prioritize actions in the action queue.
        if not self.action_queue:
            self.brain.decide_action(game_map, NPC_REGISTRY)
        if len(self.action_queue) > 2:
            print("help")
        elif len(self.action_queue) > 1:
            print("help")
        current_action = self.action_queue[0]  # Peek the first action
        
        if current_action.type == 'pathfind':
            self._execute_pathfind(current_action, game_map)
        elif current_action.type == 'converse':
            self._execute_converse(current_action, game_map)
    

    
    # def move(self, game_map):
    #     if self.brain.target:
    #         target_position = self.brain.target['data']
    #         # Check if we're adjacent to our target NPC
    #         if self.brain.target['type'] == 'npc':
    #             target = self.brain.target['npc']
    #             target_distance = abs(self.x - target.x) + abs(self.y - target.y)
    #             if target_distance == 1:
    #                 self.brain.target = None
    #                 self.brain.path = None
    #                 print(f"NPC {COLORS[self.color]} has reached its target!")
    #                 return

    #     # Check if the next step in the path is blocked by another NPC
    #     if self.brain.path:
    #         next_step = self.brain.path[0]
    #         if (next_step[0], next_step[1]) in [(npc.x, npc.y) for npc in NPC_REGISTRY if npc != self]:
    #             # If blocked, discard the current path to force a re-evaluation
    #             self.brain.path = None
    #             self.brain.determine_path((self.x, self.y), game_map)  # Re-determine the path immediately


        
    #     if not self.brain.target or not self.brain.path:
    #         self.brain.choose_target(game_map, NPC_REGISTRY)
    #         self.brain.determine_path((self.x, self.y), game_map)
    #     elif self.brain.target_has_moved_significantly(target_position): # could it get to here without target_position being defined?
    #         self.brain.determine_path((self.x, self.y), game_map)
    #         self.brain.path.pop(0) # Remove the first step in the path, since it's the current position

    #     # Take the next step towards the target
    #     if self.brain.path:
    #         next_step = self.brain.path.pop(0)
    #         self.x, self.y = next_step
    #         if not self.brain.path:
    #             self.brain.target = None
    #             print(f"NPC {COLORS[self.color]} has reached its target ({next_step})!")



