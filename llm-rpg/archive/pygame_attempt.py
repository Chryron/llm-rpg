import pygame
import os
from PIL import Image, ImageDraw

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 50
IMAGE_PATH = 'map_image.png'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def create_map_image():
    # Create a new image with white background
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), color=WHITE)
    draw = ImageDraw.Draw(img)

    # Dimensions for the room
    room_top_left = (0, 0)
    room_bottom_right = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3)

    # Draw the black-bordered room in the top-left corner
    draw.rectangle([room_top_left, room_bottom_right], outline=BLACK, width=GRID_SIZE//5, fill=WHITE)

    # Create an opening in the bottom middle of the room
    opening_width = GRID_SIZE * 2
    opening_top_left = (room_bottom_right[0] // 2 - opening_width // 2, room_bottom_right[1] - GRID_SIZE//5)
    draw.rectangle([opening_top_left, (opening_top_left[0] + opening_width, room_bottom_right[1])], fill=WHITE)

    # Draw a light gray grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        draw.line([(x, 0), (x, SCREEN_HEIGHT)], fill=(200, 200, 200))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        draw.line([(0, y), (SCREEN_WIDTH, y)], fill=(200, 200, 200))

    img.save(IMAGE_PATH)





def main():
    pygame.init()
    
    # Check if the image exists, if not create it
    if not os.path.exists(IMAGE_PATH):
        create_map_image()

    # Load the image
    map_image = pygame.image.load(IMAGE_PATH)

    # Create screen and clock objects
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NPC Game")
    clock = pygame.time.Clock()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.blit(map_image, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
