import ast
import sys
import pygame
import asyncio
from game_assets.interface import get_intro_image_path
from lib.v1.common import WS_Message


async def async_simple_game_function_event(network_event_queue: asyncio.Queue):
    """
    This function runs a sumple pygame loop that will draw "ball"s on
    screen from clients using an asyncio.Queue that is updated by what
    is sent to the server.
    """

    pygame.font.init()
    pygame.init()
    pygame.display.set_caption("SERVER")
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    default_font_name = pygame.font.get_default_font()
    font = pygame.font.SysFont(default_font_name, 40)
    small_font = pygame.font.SysFont(default_font_name, 24)

    ball = pygame.image.load(get_intro_image_path())

    ball_rect_player_dict = {}

    running = True
    target_fps = 60
    cur_fps = 60

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while not network_event_queue.empty():
            ws_msg: WS_Message = network_event_queue.get_nowait()
            if ws_msg.message_type == "CLIENT_POSITION_V1":
                try:
                    ball_rect_player_dict[ws_msg.player_session_uuid] = (
                        ast.literal_eval(ws_msg.body)
                    )
                except Exception as e:
                    print(e)

        # UPDATE
        cur_fps = round(clock.get_fps())

        text_surface_fps = font.render(f"FPS: {cur_fps}", False, "yellow")

        screen.fill("lightblue")

        # RENDER YOUR GAME HERE

        for player_session_uuid, ball_rect in ball_rect_player_dict.items():
            screen.blit(ball, ball_rect)
            player_id_text_surface = small_font.render(
                f"{player_session_uuid}", False, "pink"
            )
            screen.blit(player_id_text_surface, ball_rect)

        screen.blit(text_surface_fps, (0, 0))

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(target_fps)  # limits FPS to target_fps
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()
