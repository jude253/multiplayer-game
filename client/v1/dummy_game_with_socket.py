"""
This file is mainly to create a test that work with local client
and server interaction.
"""

import sys
import pygame
import asyncio

from websockets import connect
from websockets.asyncio.client import ClientConnection
from lib.data_structures import Point
from game_assets.interface import get_data, get_intro_image_path
from lib.v1.common import PlayerInfo
from lib.v1.config import TEST_DOMAIN, FullPath


async def send_worker(websocket: ClientConnection, send_queue: asyncio.Queue):
    """
    Adapted from here: https://docs.python.org/3/library/asyncio-queue.html#examples
    """
    while True:
        # Get a "work item" out of the queue.
        frame_count = await send_queue.get()

        # Do work
        await websocket.send(f"Hello world! {frame_count}")

        # Notify the queue that the "work item" has been processed.
        send_queue.task_done()

        print('websocket.send(f"Hello world! {frame_count}")')


async def receive_worker(websocket: ClientConnection, processed_queue: asyncio.Queue):
    """
    Adapted from here: https://docs.python.org/3/library/asyncio-queue.html#examples
    """
    while True:
        # Do work
        message = await websocket.recv()

        # Add received message to processed_queue
        processed_queue.put_nowait(message)

        print("processed_queue.put_nowait(message)")


async def async_simple_game_function_with_socket_communication(frame_limit=None):
    """
    Adapted from here: https://docs.python.org/3/library/asyncio-queue.html#examples
    """
    pygame.font.init()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    default_font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(default_font_name, 40)
    imported_data = get_data()
    message = imported_data

    ball = pygame.image.load(get_intro_image_path())
    ball_speed = [2, 2]
    ball_rect = ball.get_rect()

    point = Point(100, 100)
    running = True
    target_fps = 60
    cur_fps = 60

    # Create queues that we will use to store our "workload".
    send_queue = asyncio.Queue()
    processed_queue = asyncio.Queue()

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

        tasks = [
            asyncio.create_task(send_worker(websocket, send_queue)),
            asyncio.create_task(receive_worker(websocket, processed_queue)),
        ]

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            while not processed_queue.empty():
                message = processed_queue.get_nowait()

            # UPDATE
            cur_fps = round(clock.get_fps())
            ball_rect = ball_rect.move(ball_speed)

            # Make a call to the server about about 1 TPS
            if frame_count % target_fps == 0:
                send_queue.put_nowait(frame_count)

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

        # Cancel all tasks
        for task in tasks:
            task.cancel()

        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

    # Quit pygame
    pygame.quit()

    # Call sys exit
    sys.exit()
