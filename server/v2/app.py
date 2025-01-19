"""
Run with this command: 

```
bazel run :fastapi -- dev server/v2/app.py
```

or

```
source .venv/bin/activate
fastapi dev server/v2/app.py
```

NOTE: the watch mode will only work if bazel built again.
"""

import asyncio
from contextlib import asynccontextmanager
import os
import sys
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid
import logging

import uvicorn

from lib.v1.common import PlayerInfo, WS_Message, parse_WS_Message
from lib.v2.config import TEST_HOST, TEST_PORT, FullPath
from lib.data_structures import Point
from datetime import datetime, timezone

from lib.v2.game_simple import NetworkClient, create_game


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

NETWORK_CLIENT = NetworkClient()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.active_player_uuids: set[str] = set()
        self.game_network_client = NETWORK_CLIENT

    async def connect(self, websocket: WebSocket, player_session_uuid: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_player_uuids.add(player_session_uuid)

    def disconnect(self, websocket: WebSocket, player_session_uuid: str):
        ws_disconnect_msg = WS_Message(
            player_session_uuid=player_session_uuid,
            message_type="CLIENT_DISCONNECTED_FROM_SERVER_V2",
            body="",
        )
        self.game_network_client.in_queue.put_nowait(ws_disconnect_msg)
        self.game_network_client.out_queue.put_nowait(ws_disconnect_msg)
        self.active_connections.remove(websocket)
        self.active_player_uuids.remove(player_session_uuid)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            # If a disconnect exception gets raised when broadcasting,
            # catch it and log it, so the right client will be disconnected,
            # not any that happens to get this error when trying to
            # broadcast a message to all clients and disconnected the
            # client that gets this error caught, who still has an open
            # websocket connection.
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.exception(e)


manager = ConnectionManager()

# For keeping track of players on server
ALL_PLAYERS: Dict[str, PlayerInfo] = {}


print(Point(100, 100))


def get_now_utc() -> float:
    return datetime.now(timezone.utc).timestamp()


async def async_main_server():
    os.environ["IS_SERVER_MODE"] = "TRUE"
    game = create_game()
    game.network_client = NETWORK_CLIENT

    while game.running:
        game.update()
        await asyncio.sleep(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Needed to run game loop in background or server ticks.

    See:
    - https://stackoverflow.com/a/70873984
    - https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    logger.info("lifespan starting!")

    # Comment out pygame so that the server connect/disconnect
    # can be handled on it's own.  It is too complext to follow
    # the logic to pygame and back.  I think I will send events to
    # PyGame from the server as if it was another client that cannot
    # play at some point.
    task = asyncio.create_task(async_main_server())

    yield

    logger.info("lifespan closing!")
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    # Docs: https://docs.python.org/3/library/threading.html#thread-objects


app = FastAPI(
    lifespan=lifespan,
    host=TEST_HOST,
    port=TEST_PORT,
)


@app.get("/")
async def read_root():
    return {"hello": "world"}


@app.websocket(FullPath.WS.value)
async def websocket_endpoint(websocket: WebSocket, player_session_uuid: str):
    global manager
    await manager.connect(websocket, player_session_uuid)
    try:
        while True:
            data = await websocket.receive_text()
            ws_msg = parse_WS_Message(data)
            if ws_msg.message_type == "CLIENT_POSITION_V2":
                manager.game_network_client.in_queue.put_nowait(ws_msg)

            # This is currently the only way the disconnect exceptions get
            # thrown to disconnect a client.  Well websocket.receive_text()
            # might also raise the exeption too.  It could be worth
            # cleaning up.
            await manager.send_personal_message(f"You wrote: {data}", websocket)

            # Send out this info for debugging
            await manager.broadcast(f"Client {player_session_uuid} says: {data}")

            while not manager.game_network_client.out_queue.empty():
                message: WS_Message = await manager.game_network_client.out_queue.get()
                await manager.broadcast(message.model_dump_json())
    except WebSocketDisconnect:
        manager.disconnect(websocket, player_session_uuid)
        await manager.broadcast(f"Client {player_session_uuid} left the chat")


async def start_uvicorn_server():
    config = uvicorn.Config("server.v2.app:app", host=TEST_HOST, port=TEST_PORT)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_uvicorn_server())
