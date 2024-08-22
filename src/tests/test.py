import pygame
import sys

def lerp(a, b, t):
    """Linear interpolation between two points."""
    return a + (b - a) * t

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Smooth Background Movement")

    # Load background image
    background_image = pygame.image.load(r'D:\data\code\python\project_mount_christ\data\imgs\battle_ground.png').convert()

    # Define the target position and the duration of the movement
    target_position = (400, 300)
    duration = 1  # Duration in seconds
    start_time = pygame.time.get_ticks() / 1000.0  # Start time in seconds

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Calculate elapsed time and interpolate the position
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - start_time
        if elapsed_time < duration:
            t = elapsed_time / duration
            position = (lerp(0, target_position[0], t), lerp(0, target_position[1], t))
        else:
            position = target_position

        # Clear the screen
        screen.fill((255, 255, 255))

        # Draw the background at the interpolated position
        screen.blit(background_image, (-position[0], -position[1]))

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
