import random
from pathfinding import a_star_pathfinding
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, COLORS

class Brain:
    def __init__(self, parent_npc):
        self.parent_npc = parent_npc
        self.memory = Memory()
        self.target = None
        self.path = None

        # Dialogue-related attributes  
        
        self.conversation_partner = None
        self.messages = []


    
    def decide_action(self, game_map, all_npcs):
        """Decide on the next action for the NPC."""
        if random.choice([True, False]):
            target_npc = self._choose_npc_target(all_npcs)
            if target_npc:
                print(f"NPC {COLORS[self.parent_npc.color]} is targeting NPC {COLORS[target_npc.color]}")
                message = random.choice(['Hello', 'How are you?', 'Nice to meet you'])
                self.parent_npc.queue_action('converse', target_npc, message=message)
                return  # Exit after queuing a converse action
        target_location = self.choose_location(game_map)
        if target_location:
            self.parent_npc.queue_action('pathfind', target_location)

 
    def _choose_conversation_partner(self, all_npcs):
        """Choose a random NPC to converse with."""
        available_npcs = [npc for npc in all_npcs if npc != self.parent_npc]
        return random.choice(available_npcs) if available_npcs else None

    def _choose_npc_target(self, all_npcs):
        """Choose a random NPC to target."""
        available_npcs = [npc for npc in all_npcs if npc != self.parent_npc]
        return random.choice(available_npcs) if available_npcs else None

    

    def choose_location(self, game_map):
        """Choose a location to target."""
                
        available_locations = game_map.get_available_locations(self.parent_npc.x, self.parent_npc.y)
        if not available_locations:
            return None  # Return None if no locations are available

        chosen_location = random.choice(available_locations)
        print(f"NPC {COLORS[self.parent_npc.color]} is targeting {chosen_location.name}")
        return chosen_location.get_random_point(game_map)
    
    def choose_target(self, game_map, all_npcs):
        if random.choice([True, False]):  # 50% chance to target an NPC
            available_npcs = [npc for npc in all_npcs if npc != self.parent_npc]
            if available_npcs:
                target_npc = random.choice(available_npcs)
                print(f"NPC {COLORS[self.parent_npc.color]} is targeting NPC {COLORS[target_npc.color]}")
                self.parent_npc.queue_action('converse', target_npc)
            else:
                self.choose_location_as_target(game_map)
        else:
            self.choose_location_as_target(game_map)
            
    def choose_location_as_target(self, game_map):
        """Choose a location as the target."""
        target_coords = self.choose_location(game_map)
        if target_coords:
            self.parent_npc.queue_action('pathfind', target_coords)

    # def choose_random_point(self, game_map):
    #     while True:
    #         x = random.randint(0, SCREEN_WIDTH // GRID_SIZE - 1)
    #         y = random.randint(0, SCREEN_HEIGHT // GRID_SIZE - 1)
    #         if not game_map.is_wall(x, y):
    #             self.target = {'type': 'coords', 'data': (x, y)}
    #             print(f"NPC {COLORS[self.parent_npc.color]} is targeting ({x}, {y})")
    #             break
    
    def determine_path(self, current_position, game_map):
        current_action = self.parent_npc.action_queue[0] if self.parent_npc.action_queue else None
        if current_action and current_action.type == 'pathfind':
            if not isinstance(current_action.target, tuple):
                target_position = {'type': 'npc',
                                   'data': (current_action.target.x, current_action.target.y),
                                   'npc': current_action.target}
                pass
            else:
                target_position = {'type': 'coords',
                                   'data': current_action.target,}
                pass
            self.target_position = target_position['data']
            self.path = a_star_pathfinding(current_position, target_position, game_map, {'type': 'npc', 'data': (self.parent_npc.x, self.parent_npc.y), 'npc': self.parent_npc})
            
        else:
            Exception("No pathfinding action in queue")

    
    # def determine_path(self, current_position, game_map):
    #     if self.target:
    #         if self.target['type']=='npc': self.target['data'] = (self.target['npc'].x, self.target['npc'].y)
    #         self.path = a_star_pathfinding(current_position, self.target, game_map, {'type': 'npc', 'data': (self.parent_npc.x, self.parent_npc.y), 'npc': self.parent_npc})

    def target_has_moved_significantly(self, threshold=20):
        """Check if the target has moved significantly since the path was determined."""
        action = self.parent_npc.action_queue[0]
        old_position = self.target_position
        if action.type == 'pathfind':
            if not isinstance(action.target, tuple):
                dx = action.target.x - old_position[0]
                dy = action.target.y - old_position[1]
                return abs(dx) > threshold or abs(dy) > threshold            
            else:
                return False
        else:
            Exception("No pathfinding action in queue")

        if not self.target['type'] == 'npc' or not self.target['npc']:
            return False

    def see_surroundings(self, current_location):
        # For simplicity, let's assume it can see 1 grid square around it
        surroundings = [
            (current_location[0] + 1, current_location[1]),
            (current_location[0] - 1, current_location[1]),
            (current_location[0], current_location[1] + 1),
            (current_location[0], current_location[1] - 1)
        ]
        return surroundings


class Memory:
    def __init__(self):
        self.associations = {}

    def associate(self, entity, location):
        self.associations[entity] = location
