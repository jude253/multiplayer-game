"""
Run with this command: 

```
bazel run :fastapi -- dev server/v1/app.py
```

or

```
bazel run //server:fastapi_dev_v1
```

or

```
bazel run //server:fastapi_prod_v1
```

or

```
source .venv/bin/activate
fastapi dev server/v1/app.py
```

NOTE: the watch mode will only work if bazel built again.
"""

import asyncio
from contextlib import asynccontextmanager
import sys
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid
import logging

import uvicorn

from lib.v1.common import PlayerInfo, WS_Message, parse_WS_Message
from lib.v1.config import TEST_HOST, TEST_PORT, FullPath
from lib.data_structures import Point
from datetime import datetime, timezone

from server.v1.async_simple_game_event_queue import async_simple_game_function_event


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# For keeping track of players on server
ALL_PLAYERS: Dict[str, PlayerInfo] = {}

NETWORK_EVENT_IN_QUEUE = asyncio.Queue()
NETWORK_EVENT_OUT_QUEUE = asyncio.Queue()

print(Point(100, 100))


def get_now_utc() -> float:
    return datetime.now(timezone.utc).timestamp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Needed to run game loop in background or server ticks.

    See:
    - https://stackoverflow.com/a/70873984
    - https://fastapi.tiangolo.com/advanced/events/#lifespan
    """

    asyncio.create_task(
        async_simple_game_function_event(
            network_event_in_queue=NETWORK_EVENT_IN_QUEUE,
            network_event_out_queue=NETWORK_EVENT_OUT_QUEUE,
        )
    )

    yield

    logger.info("lifespan closing!")

    # Docs: https://docs.python.org/3/library/threading.html#thread-objects


app = FastAPI(
    lifespan=lifespan,
    host=TEST_HOST,
    port=TEST_PORT,
)


@app.get("/")
async def read_root():
    return {"hello": "world"}


########################################################################
# App http operations are currently get, even though that's not
# sematically best because this enables debugging the server by
# navigating to the routes in the browser.
########################################################################


@app.get(FullPath.JOIN.value)
async def get_join(requested_name: str | None = None):
    player_session_uuid = str(uuid.uuid4())
    if not requested_name:
        requested_name = player_session_uuid

    player_info = PlayerInfo(
        id=player_session_uuid,
        user_name=requested_name,
        last_update_utc_timestamp=get_now_utc(),
    )
    ALL_PLAYERS[player_session_uuid] = player_info
    return {
        "player_info": player_info,
        "all_players": ALL_PLAYERS,
    }


@app.get(FullPath.PING.value)
async def get_ping(player_session_uuid: str):
    """
    This is like update, except it only updates the
    `last_update_utc_timestamp` instead of also updating potentially
    other things.
    """
    if player_session_uuid not in ALL_PLAYERS:
        return {
            "player_info": {},
            "all_players": {},
        }
    ALL_PLAYERS[player_session_uuid].last_update_utc_timestamp = get_now_utc()
    player_info = ALL_PLAYERS[player_session_uuid]

    return {
        "player_info": player_info,
        "all_players": ALL_PLAYERS,
    }


@app.get(FullPath.UPDATE.value)
async def get_update(player_session_uuid: str):

    if player_session_uuid not in ALL_PLAYERS:
        return {
            "player_info": {},
            "all_players": {},
        }
    ALL_PLAYERS[player_session_uuid].last_update_utc_timestamp = get_now_utc()
    player_info = ALL_PLAYERS[player_session_uuid]

    return {
        "player_info": player_info,
        "all_players": ALL_PLAYERS,
    }


@app.get(FullPath.UPDATE.value)
async def get_update(player_session_uuid: str):

    if player_session_uuid not in ALL_PLAYERS:
        return {
            "player_info": {},
            "all_players": {},
        }
    ALL_PLAYERS[player_session_uuid].last_update_utc_timestamp = get_now_utc()
    player_info = ALL_PLAYERS[player_session_uuid]

    return {
        "player_info": player_info,
        "all_players": ALL_PLAYERS,
    }


@app.get(FullPath.LEAVE.value)
async def get_leave(player_session_uuid: str):

    if player_session_uuid not in ALL_PLAYERS:
        return {
            "player_info": {},
        }
    # NOTE: this approach doesn't work for disconnecting. Need to
    # understand this deeper.  Might need all communication to happen
    # Through queueues or like garbage collecting of clients that
    # disconnected.
    NETWORK_EVENT_IN_QUEUE.put_nowait(
        WS_Message(
            player_session_uuid=player_session_uuid,
            message_type="CLIENT_DISCONNECTED_FROM_SERVER_V1",
            body="",
        )
    )
    player_info = ALL_PLAYERS.pop(player_session_uuid)

    return {
        "player_info": player_info,
    }


@app.websocket(FullPath.WS.value)
async def websocket_endpoint(websocket: WebSocket, player_session_uuid: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            ws_msg = parse_WS_Message(data)

            # Only put allowed events in the NETWORK_EVENT_IN_QUEUE for game
            if ws_msg.message_type == "CLIENT_POSITION_V1":
                NETWORK_EVENT_IN_QUEUE.put_nowait(ws_msg)

            # Send out this info for debugging
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client {player_session_uuid} says: {data}")

            while not NETWORK_EVENT_OUT_QUEUE.empty():
                message: WS_Message = await NETWORK_EVENT_OUT_QUEUE.get()
                await manager.broadcast(message.model_dump_json())
    except WebSocketDisconnect:

        # NOTE: this approach doesn't work for disconnecting. Need to
        # understand this deeper.  Might need all communication to happen
        # Through queueues or like garbage collecting of clients that
        # disconnected.
        # It also seems like the `/leave` may be process after the client
        # has disonnected and the client already and the characters might
        # be getting mixed up on the clients, as the one without a uuid
        # should be what is moved, but that seems to get switched sometimes
        # Maybe after disconnects?
        # NETWORK_EVENT_IN_QUEUE.put_nowait(WS_Message(
        #     player_session_uuid=player_session_uuid,
        #     message_type='CLIENT_DISCONNECTED_FROM_SERVER_V1',
        #     body=''
        # ))
        manager.disconnect(websocket)

        await manager.broadcast(f"Client {player_session_uuid} left the chat")


async def start_uvicorn_server():
    config = uvicorn.Config("server.v1.app:app", host=TEST_HOST, port=TEST_PORT)
    server = uvicorn.Server(config)
    await server.serve()
