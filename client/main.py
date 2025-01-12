"""
This is a rough draft of the client to call the server with a game.

To test, start the server in `server/v1/app.py`,

Then run: bazel run //client:v1_client

NOTE: Optionally run `python -m websockets ws://127.0.0.1:8000/v1/ws/2`
from another terminal window to watch the messages as another client.
"""

import ast
import sys
import pygame
import asyncio

import requests
from websockets import connect
from websockets.asyncio.client import ClientConnection
from game_assets.interface import get_intro_image_path
from lib.v1.common import PlayerInfo, WS_Message, parse_WS_Message
from lib.v1.config import TEST_DOMAIN, FullPath


async def send_worker(websocket: ClientConnection, send_queue: asyncio.Queue):
    """
    Adapted from here: https://docs.python.org/3/library/asyncio-queue.html#examples
    """
    while True:
        # Get a "work item" out of the queue.
        message: WS_Message = await send_queue.get()
        # Do work
        await websocket.send(message.model_dump_json())

        # Notify the queue that the "work item" has been processed.
        send_queue.task_done()


async def receive_worker(websocket: ClientConnection, processed_queue: asyncio.Queue):
    """
    Adapted from here: https://docs.python.org/3/library/asyncio-queue.html#examples
    """
    while True:
        # Do work
        message = await websocket.recv()
        ws_msg: WS_Message = parse_WS_Message(message)

        # Only put allowed events in the NETWORK_EVENT_QUEUE for game
        if ws_msg.message_type == "ALL_CLIENT_POSITIONS_V1":
            # Add received, valid message to processed_queue
            processed_queue.put_nowait(ws_msg)


async def async_simple_game_function_with_socket_communication():
    """
    This version of a client will get a unique ID from the server and
    use that for the websocket connection.  It allows movement and
    sending over the position of the ball from the client.  This is then
    intepreted on the server.

    The idea is to use some sort of event or command system eventually,
    similar to what is talked about here:

    https://gameprogrammingpatterns.com/command.html

    Not sure exactly what to do for that yet, so just keeping it simple
    by sending over a tuple.  Ideally, I could have several different
    types of events to send over and have them be parsed the same on the
    client/server, but this might take some though.  Not sure what's
    needed exactly.
    """
    pygame.font.init()
    pygame.init()
    pygame.display.set_caption("CLIENT")
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    default_font_name = pygame.font.get_default_font()
    small_font = pygame.font.SysFont(default_font_name, 24)
    font = pygame.font.SysFont(default_font_name, 40)

    ball = pygame.image.load(get_intro_image_path())
    ball_rect = ball.get_rect()

    running = True
    target_fps = 60
    cur_fps = 60
    dt = 0
    frame_count = 0

    # Create queues that we will use to store our "workload".
    send_queue = asyncio.Queue()
    processed_queue = asyncio.Queue()

    ball_rect_player_dict = {}

    # Random Player info:
    r = requests.get(f"http://{TEST_DOMAIN}/{FullPath.JOIN.value}")
    player_info = PlayerInfo(**r.json()["player_info"])
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
                    r = requests.get(
                        f"http://{TEST_DOMAIN}/{FullPath.LEAVE.value}".replace(
                            "{player_session_uuid}", player_info.id
                        )
                    )
                    running = False

            while not processed_queue.empty():
                ws_msg: WS_Message = processed_queue.get_nowait()
                print(ws_msg)
                if ws_msg.message_type == "ALL_CLIENT_POSITIONS_V1":
                    try:
                        ball_rect_player_dict = ast.literal_eval(ws_msg.body)

                    except Exception as e:
                        print(e)

            # UPDATE
            cur_fps = round(clock.get_fps())

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                ball_rect.y -= 300 * dt
            if keys[pygame.K_s]:
                ball_rect.y += 300 * dt
            if keys[pygame.K_a]:
                ball_rect.x -= 300 * dt
            if keys[pygame.K_d]:
                ball_rect.x += 300 * dt

            # Make a call to the server about about 10 TPS
            if frame_count % (target_fps // 10) == 0:
                send_queue.put_nowait(
                    WS_Message(
                        player_session_uuid=player_info.id,
                        message_type="CLIENT_POSITION_V1",
                        body=str((ball_rect.x, ball_rect.y, ball_rect.w, ball_rect.h)),
                    )
                )

            text_surface_fps = font.render(f"FPS: {cur_fps}", False, "yellow")

            screen.fill("purple")

            # RENDER YOUR GAME HERE

            screen.blit(ball, ball_rect)

            for player_session_uuid, client_ball_rect in ball_rect_player_dict.items():
                if player_session_uuid != player_info.id:
                    screen.blit(ball, client_ball_rect)
                    player_id_text_surface = small_font.render(
                        f"{player_session_uuid}", False, "pink"
                    )
                    screen.blit(player_id_text_surface, client_ball_rect)

            screen.blit(text_surface_fps, (0, 0))

            # flip() the display to put your work on screen
            pygame.display.flip()
            frame_count = (frame_count + 1) % 1000

            dt = clock.tick(target_fps) / 1000  # limits FPS to target_fps
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


if __name__ == "__main__":
    asyncio.run(async_simple_game_function_with_socket_communication())
