from constants import *
from globals import NPC_REGISTRY

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


def a_star_pathfinding(start, target, game_map, current_npc):
    open_list = []
    closed_list = []
    start_node = Node(start[0], start[1])
    target_node = Node(target['data'][0], target['data'][1])

    open_list.append(start_node)
    if target['type'] == 'npc':
        npc_positions = {(npc.x, npc.y) for npc in NPC_REGISTRY if (npc.x, npc.y) != current_npc['data'] and (npc.x, npc.y) != target['data']}
    else:
        npc_positions = {(npc.x, npc.y) for npc in NPC_REGISTRY if (npc.x, npc.y) != current_npc['data']}
    
    while len(open_list) > 0:
        
        current_node = sorted(open_list, key=lambda x: x.f)[0]
        open_list.remove(current_node)

        closed_list.append(current_node)
        # print(f"Current node: {current_node.x}, {current_node.y}. Target node: {target_node.x}, {target_node.y}. Open list: {len(open_list)}. Closed list: {len(closed_list)}")
        
        # Found the goal
        if current_node.x == target_node.x and current_node.y == target_node.y:
            path = []
            current = current_node
            while current is not None:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]  # Return reversed path

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.x + new_position[0], current_node.y + new_position[1])

            # Ensure within range
            if node_position[0] < 0 or node_position[0] >= SCREEN_WIDTH // GRID_SIZE or \
            node_position[1] < 0 or node_position[1] >= SCREEN_HEIGHT // GRID_SIZE:
                continue

            # Ensure not a wall
            if game_map.is_wall(node_position[0], node_position[1]) or node_position in npc_positions:
                continue


            new_node = Node(node_position[0], node_position[1])
            new_node.parent = current_node
            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = ((child.x - target_node.x) ** 2) + ((child.y - target_node.y) ** 2)
            child.f = child.g + child.h

            # Find if a node with the same coordinates as child exists in the open list
            existing_node = next((node for node in open_list if node.x == child.x and node.y == child.y), None)

            if existing_node:
                # If the existing node's g value is higher, update its values
                if existing_node.g > child.g:
                    existing_node.g = child.g
                    existing_node.h = child.h
                    existing_node.f = child.f
                    existing_node.parent = child.parent
            else:
                open_list.append(child)

    return None  # No path found
