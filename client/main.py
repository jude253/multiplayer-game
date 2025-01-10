"""
This is a rough draft of the client to call the server with a game.

To test, start the server in `server/v1/app.py`,

Then run: bazel run //client:v1_client

NOTE: Optionally run `python -m websockets ws://127.0.0.1:8000/v1/ws/2`
from another terminal window to watch the messages as another client.
"""

import sys
import pygame
import asyncio

from websockets import connect
from lib.data_structures import Point
from game_assets.interface import get_data, get_intro_image_path
from lib.v1.common import PlayerInfo
from lib.v1.config import TEST_DOMAIN, FullPath


async def async_simple_game_function_with_socket_communication(frame_limit=None):
    pygame.font.init()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    default_font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(default_font_name, 40)
    imported_data = get_data()
    print(imported_data)

    ball = pygame.image.load(get_intro_image_path())
    ball_speed = [2, 2]
    ball_rect = ball.get_rect()

    point = Point(100, 100)
    running = True
    target_fps = 60
    cur_fps = 60

    if frame_limit and frame_limit >= target_fps * 10:
        raise ValueError(f"`frame_limit` must be less than {target_fps*10}!")

    frame_count = 0

    # Random Player info:
    player_info = PlayerInfo(
        id="abc123",
        user_name="something",
        last_update_utc_timestamp=1.0,
    )
    url = f"ws://{TEST_DOMAIN}{FullPath.WS.value}".replace(
        "{player_session_uuid}", player_info.id
    )
    async with connect(
        url, close_timeout=0.1  # Didn't implement closing functionality yet on server
    ) as websocket:

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # UPDATE
            cur_fps = round(clock.get_fps())
            ball_rect = ball_rect.move(ball_speed)

            # Make a call to the server about about 1 TPS
            if frame_count % target_fps == 0:
                await websocket.send(f"Hello world! {frame_count}")
                # Currently the server will return 2 messages after sending
                # a message, not sure how to poll and receive all messages
                # I need some sort of message queue, I believe.
                message = await websocket.recv()
                message = await websocket.recv()

            if ball_rect.left < 0 or ball_rect.right > screen.get_width():
                ball_speed[0] = -ball_speed[0]

            if ball_rect.top < 0 or ball_rect.bottom > screen.get_height():
                ball_speed[1] = -ball_speed[1]

            text_surface_fps = text_surface = font.render(
                f"FPS: {cur_fps}", False, "yellow"
            )

            text_surface = font.render(message, False, "yellow")
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


if __name__ == "__main__":
    asyncio.run(async_simple_game_function_with_socket_communication())
