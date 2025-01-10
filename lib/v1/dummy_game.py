import sys
import pygame
import asyncio
from lib.data_structures import Point
from game_assets.interface import get_data, get_intro_image_path


async def async_simple_game_function(frame_limit=None):
    """
    This function is an simple game that imports and image and writes
    text to the screen with the FPS and text loaded from a file in
    another package.  It is async as well, however it is based on how
    pygbag says to run pygame async here: https://pygame-web.github.io/wiki/pygbag/

    It might be best to follow this approach in the long term:
    https://github.com/AlexElvers/pygame-with-asyncio

    This is so that time lost from sending/receiving data over the wire
    is accounted for in FPS frame delays (because of the GIL).  Not sure
    how exactly to put controls and network events into queues yet, but
    thinking this will be the way to allow them to communicate smoothly
    without blocking rendering.  Thinking I will emit network events
    from the game loop and have them end up in a queue and also check
    the queue in the game loop without waiting responses anywhere in the
    gameloop if possible.

    This function allows for testing that pieces are connected and is
    simple enough to be expanded on/reorganized in several different
    ways as I understand more.

    `frame_limit` is included so this can be included as a unit test to
    ensure all pieces are connected correctly.
    """

    if frame_limit and frame_limit >= 1000:
        raise ValueError("`frame_limit` must be less than 1000!")

    pygame.font.init()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    default_font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(default_font_name, 40)

    ball = pygame.image.load(get_intro_image_path())
    ball_speed = [2, 2]
    ball_rect = ball.get_rect()

    point = Point(100, 100)
    imported_data = get_data()
    running = True
    target_fps = 60
    cur_fps = 60

    frame_count = 0
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # UPDATE
        cur_fps = round(clock.get_fps())
        ball_rect = ball_rect.move(ball_speed)

        if ball_rect.left < 0 or ball_rect.right > screen.get_width():
            ball_speed[0] = -ball_speed[0]

        if ball_rect.top < 0 or ball_rect.bottom > screen.get_height():
            ball_speed[1] = -ball_speed[1]

        text_surface_fps = text_surface = font.render(
            f"FPS: {cur_fps}", False, "yellow"
        )

        text_surface = font.render(imported_data, False, "yellow")
        tw, th = text_surface.get_width(), text_surface.get_height()
        text_surface_rect = (
            screen.get_width() // 2 - tw // 2,
            screen.get_height() // 2 - th // 2,
        )

        screen.fill("purple")

        # RENDER YOUR GAME HERE
        pygame.draw.circle(screen, "red", (point.x, point.y), 40)

        screen.blit(ball, ball_rect)

        screen.blit(
            text_surface_fps,
            (0, 0),
        )

        screen.blit(
            text_surface,
            text_surface_rect,
        )

        # flip() the display to put your work on screen
        pygame.display.flip()
        frame_count = (frame_count + 1) % 1000
        if frame_limit and frame_count >= frame_limit:
            running = False
        clock.tick(target_fps)  # limits FPS to target_fps
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()
