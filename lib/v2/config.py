from enum import Enum

ROOT_PREFIX = "v2"

TEST_HOST = "127.0.0.1"
TEST_PORT = 8000
TEST_DOMAIN = f"{TEST_HOST}:{TEST_PORT}"


class RootPath(Enum):
    JOIN = f"/{ROOT_PREFIX}/join"
    PING = f"/{ROOT_PREFIX}/ping"
    UPDATE = f"/{ROOT_PREFIX}/update"
    LEAVE = f"/{ROOT_PREFIX}/leave"
    WS = f"/{ROOT_PREFIX}/ws"


class FullPath(Enum):
    JOIN = RootPath.JOIN.value
    PING = f"{RootPath.PING.value}/{{player_session_uuid}}"
    UPDATE = f"{RootPath.UPDATE.value}/{{player_session_uuid}}"
    LEAVE = f"{RootPath.LEAVE.value}/{{player_session_uuid}}"
    WS = f"{RootPath.WS.value}/{{player_session_uuid}}"
