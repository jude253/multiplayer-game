import json
from typing import Any
from pydantic import BaseModel


class PlayerInfo(BaseModel):
    id: str
    user_name: str
    last_update_utc_timestamp: float


class WS_Message(BaseModel):
    player_session_uuid: str
    message_type: str
    body: Any


def parse_WS_Message(input_str: str):
    input_dict = {
        "player_session_uuid": "UNKOWN",
        "message_type": "UNKOWN",
        "body": input_str,
    }
    try:
        input_dict = json.loads(input_str)
    except Exception as e:
        print(f"Unable to parse message '{input_str}'.  Error Message:\n\n'{e}'")

    return WS_Message(**input_dict)
