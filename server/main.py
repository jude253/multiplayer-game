# Example file showing a basic pygame "game loop"
import pygame
from lib.data_structures import Point
from game_assets.interface import get_data

# pygame setup
pygame.font.init()
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 40)

POINT = Point(100, 100)
imported_data = get_data()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE
    pygame.draw.circle(screen, "red", (POINT.x, POINT.y), 40)

    text_surface = font.render(imported_data, False, "yellow")
    tw, th = text_surface.get_width(), text_surface.get_height()
    screen.blit(
        text_surface,
        (screen.get_width() // 2 - tw // 2, screen.get_height() // 2 - th // 2),
    )
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
