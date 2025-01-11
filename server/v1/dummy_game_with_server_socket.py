"""
This file is mainly to create a test that work with local client
and server interaction.
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

from lib.v1.common import PlayerInfo
from lib.v1.config import TEST_HOST, TEST_PORT, FullPath
from lib.data_structures import Point
from datetime import datetime, timezone

from lib.v1.dummy_game import async_simple_game_function


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

    # Not sure what is best for this.  Thinking it could be good to run
    # This headlessly maybe? Id.  It would be nice to have pygame
    # running on server to reuse the same logic as in the game, but
    # not sure what is best exactly yet.  Need some sort of queue system
    asyncio.create_task(async_simple_game_function())

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
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client {player_session_uuid} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {player_session_uuid} left the chat")


async def start_uvicorn_server():
    config = uvicorn.Config(
        "server.v1.dummy_game_with_server_socket:app", host=TEST_HOST, port=TEST_PORT
    )
    server = uvicorn.Server(config)
    await server.serve()
