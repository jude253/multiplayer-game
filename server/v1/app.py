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

from contextlib import asynccontextmanager
import sys
from typing import Dict
from fastapi import FastAPI
import uuid
import logging

from lib.v1.common import PlayerInfo
from lib.v1.config import TEST_HOST, TEST_PORT, FullPath
from lib.data_structures import Point
import threading
import time
from datetime import datetime, timezone

from lib.v1.config import ROOT_PREFIX

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


class BackgroundTasks(threading.Thread):
    def run(self, *args, **kwargs):
        global IS_RUNNING
        while IS_RUNNING:
            logger.info("Tick")
            time.sleep(1)


# For terminating the background task
IS_RUNNING = True

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
    global IS_RUNNING
    logger.info("lifespan starting up!")
    t = BackgroundTasks(daemon=True)
    t.start()

    yield

    logger.info("lifespan closing!")

    # Docs: https://docs.python.org/3/library/threading.html#thread-objects
    IS_RUNNING = False
    t.join()


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
