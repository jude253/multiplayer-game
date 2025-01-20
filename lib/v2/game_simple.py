# import basic pygame modules
import asyncio
import os
from typing import Any, Dict, List, Set
from pydantic import BaseModel, ConfigDict
import pygame as pg
from pygame import examples as main_dir
from importlib.resources import as_file, files
import uuid

from lib.v1.common import WS_Message

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def get_file(file):
    examples_dir_files = files(main_dir)
    with as_file(examples_dir_files) as examples_dir:
        data_dir_filepath = examples_dir.joinpath("data")
        file = data_dir_filepath.joinpath(file)
    return file


def load_image(file):
    """loads an image, prepares it for play"""
    file = get_file(file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


def get_rand_player_id():
    """Get from server at some point!"""
    return str(uuid.uuid4())


def get_cur_player_id():
    """Get from server at some point!"""
    return str(uuid.uuid4())


class BaseNetworkClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    out_queue: asyncio.Queue = asyncio.Queue()
    in_queue: asyncio.Queue = asyncio.Queue()

    def has_message_out(self):
        return not self.out_queue.empty()

    def enque_message_out(self, msg):
        print(msg)
        pass

    def has_message_in(self):
        return not self.in_queue.empty()

    def get_message_in(self):
        pass


class NetworkClient(BaseNetworkClient):
    def enque_message_out(self, msg: WS_Message):
        self.out_queue.put_nowait(msg)

    def get_message_in(self) -> WS_Message | None:
        if self.has_message_in():
            ws_msg: WS_Message = self.in_queue.get_nowait()
            return ws_msg


class Game(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Defaults set:
    network_client: BaseNetworkClient | NetworkClient = BaseNetworkClient()
    is_server_mode: bool = False
    screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    running: bool = True
    clock: pg.time.Clock = pg.time.Clock()
    __cur_player_id: str | None = None
    local_game_sprites: pg.sprite.Group = pg.sprite.Group()
    network_game_sprites: pg.sprite.Group = pg.sprite.Group()
    network_sprite_lookup: Dict[str, pg.sprite.Sprite] = dict()
    other_game_sprites: pg.sprite.Group = pg.sprite.Group()
    dt: float = 0.0
    cur_fps: float = 0.0
    frame_count: int = 0

    def update(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
        self.local_game_sprites.update()
        self.other_game_sprites.update()

        self._send_out_data()
        self._receive_data()

        self._render_game()
        self._handle_frame_end()
        return

    def _render_game(self):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("purple")
        # RENDER YOUR GAME HERE
        self.local_game_sprites.draw(self.screen)
        self.network_game_sprites.draw(self.screen)
        self.other_game_sprites.draw(self.screen)
        return

    def _handle_frame_end(self):
        # flip() the display to put your work on screen
        pg.display.flip()
        self.frame_count += 1
        # limits FPS to 60
        self.cur_fps = round(self.clock.get_fps(), 1)

        if not self.is_server_mode:
            # Not running on server, stall to 60 fps
            self.dt = self.clock.tick(60) / 1000
        else:
            # Running on server, maybe stall differently? Manage tick rate on server
            self.dt = self.clock.tick(60) / 1000

        return

    def _send_out_data(self):
        if self.frame_count % 5 == 0:
            body = self.get_local_sprites_dict()
            if self.is_server_mode:
                body.extend(self.get_network_sprites_dict())
            message_type = (
                "SERVER_POSITION_V2" if self.is_server_mode else "CLIENT_POSITION_V2"
            )
            ws_message = WS_Message(
                player_session_uuid=self.get_cur_player_id(),
                message_type=message_type,
                body=body,
            )

            if self.is_server_mode:
                if len(self.network_sprite_lookup) > 0:
                    # Only send out messages if a user connected to
                    # avoid collecting too much memory on server and
                    # crashing!
                    self.network_client.enque_message_out(ws_message)
                else:
                    # Clear out queue if no one connected to avoid
                    # crashing server by using up all memory!
                    while self.network_client.has_message_out():
                        self.network_client.out_queue.get_nowait()
            else:
                self.network_client.enque_message_out(ws_message)
        return

    def _receive_data(self):
        while self.network_client.has_message_in():
            ws_msg = self.network_client.get_message_in()
            if ws_msg.message_type in ("SERVER_POSITION_V2", "CLIENT_POSITION_V2"):
                self.get_network_sprites(ws_msg.body)
                continue
            if ws_msg.message_type == "CLIENT_DISCONNECTED_FROM_SERVER_V2":
                self._remove_network_player(ws_msg.player_session_uuid)
        return

    def _add_cur_player(self, id):
        if not self.__cur_player_id:
            self.__cur_player_id = id
            Player(self, id, self.local_game_sprites)

    def _add_other_local_player(self):
        id = get_rand_player_id()
        Player(self, id, self.local_game_sprites)

    def _add_network_player(self, id: str, rect: pg.Rect | None = None):
        p = Player(self, id, self.network_game_sprites)
        if rect:
            p.rect = rect
        return p

    def _remove_network_player(self, id):
        sprite = self.network_sprite_lookup.pop(id)
        sprite.kill()
        return

    def get_cur_player_id(self):
        return self.__cur_player_id

    def _add_fps(self):
        Fps(self, self.other_game_sprites)

    def get_local_sprites_dict(self):
        return [
            {
                "id": sprite.id,
                "class_name": sprite.__class__.__name__,
                "rect": tuple(sprite.rect),
            }
            for sprite in self.local_game_sprites
        ]

    def get_network_sprites_dict(self):
        return [
            {
                "id": sprite.id,
                "class_name": sprite.__class__.__name__,
                "rect": tuple(sprite.rect),
            }
            for sprite in self.network_game_sprites
        ]

    def get_network_sprites(self, network_dict: List[Dict[str, Any]]):

        # This gets rid of lingering player data on the server that gets
        # sent over to clients when a new client joins after an old
        # client has left
        disconnected_client_ids = set(self.network_sprite_lookup.keys())

        for item in network_dict:
            id = item.get("id")
            if id in disconnected_client_ids:
                disconnected_client_ids.remove(id)
            rect = pg.Rect(item.get("rect"))
            if id == self.get_cur_player_id():
                continue
            elif id in self.network_sprite_lookup:
                cur_sprite = self.network_sprite_lookup[id]
                cur_sprite.rect = rect
                continue

            if item.get("class_name") == "Player":
                player = self._add_network_player(id)
                self.network_sprite_lookup[id] = player

        # Only clean up ids that haven't receievd updates on clients
        # b/c on server this method will be triggered when individual
        # clients send over updates for themselves and will delete the
        # sprites for the other clients.
        if not self.is_server_mode:
            for id in disconnected_client_ids:
                self._remove_network_player(id)
        return


class Player(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    speed = 1000
    images: List[pg.Surface] = []

    def __init__(self, game: Game, id: str, *groups):
        self.game = game
        self.id = id
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midtop=game.screen.get_rect().midtop)
        self.server_last_position = self.rect.center
        self.server_direction = 1

    def update(self, *args, **kwargs):
        if self.id == self.game.get_cur_player_id():
            if not self.game.is_server_mode:
                keys = pg.key.get_pressed()
                if keys[pg.K_w]:
                    self.rect.centery -= self.speed * self.game.dt
                if keys[pg.K_s]:
                    self.rect.centery += self.speed * self.game.dt
                if keys[pg.K_a]:
                    self.rect.centerx -= self.speed * self.game.dt
                if keys[pg.K_d]:
                    self.rect.centerx += self.speed * self.game.dt
            else:
                self.rect.centerx += self.server_direction * self.speed * self.game.dt
                if self.server_last_position == self.rect.center:
                    self.server_direction *= -1
                self.server_last_position = self.rect.center
        self.rect = self.rect.clamp(self.game.screen.get_rect())


class Fps(pg.sprite.Sprite):
    """to keep track of the Fps."""

    def __init__(self, game: Game, *groups):
        self.game = game
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = "white"
        self.last_fps = -1
        self.update()
        self.rect = self.image.get_rect(topleft=(0, 0))

    def update(self, *args, **kwargs):
        """We only update the Fps in update() when it has changed."""
        if self.game.cur_fps != self.last_fps:
            self.last_fps = self.game.cur_fps
            msg = f"FPS: {self.game.cur_fps}"
            self.image = self.font.render(msg, 0, self.color)


def create_game():
    pg.init()

    is_server_mode = os.environ.get("IS_SERVER_MODE", "false").lower() == "true"

    game = Game(is_server_mode=is_server_mode)
    display_caption = "SERVER" if is_server_mode else "CLIENT"
    pg.display.set_caption(display_caption)

    # Add some sort of environment variable guard eventually maybe:
    game._add_fps()

    img = load_image("player1.gif")
    Player.images = [img, pg.transform.flip(img, 1, 0)]

    cur_player_id = get_cur_player_id()

    game._add_cur_player(cur_player_id)

    return game


def main():
    game = create_game()
    while game.running:
        game.update()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
