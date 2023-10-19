import pygame
import os
from game_map import GameMap, create_map_image
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, IMAGE_PATH
from globals import NPC_REGISTRY
from npc import NPC

def main():
    pygame.init()

    # Check if the image exists, if not create it
    if not os.path.exists(IMAGE_PATH):
        create_map_image()

    game_map = GameMap(IMAGE_PATH)

    # Create screen and clock objects
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NPC Game")
    clock = pygame.time.Clock()

    # Main game loop
    # Initialize some NPCs
    npc1 = NPC(2, 2, (255, 0, 0))  # Red NPC
    npc2 = NPC(4, 4, (0, 255, 0))  # Green NPC
    running = True
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.blit(game_map.map_image, (0, 0))

        for npc in NPC_REGISTRY:
            npc.move(game_map)
            npc.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
