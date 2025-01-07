"""
This is a rough draft of the client to call the server.

To test, start the server in `server/v1/app.py`,

Then run: bazel run //client:v1_client


NOTE: it seems that pydantic needs to be specifed as a dependency of
//client, because Bazel doesn't seem to pick it up as a dependency of
//lib.

NOTE: running the client from the .venv does not appear work b/c
//client does not seem to be able to find the //lib, but the server
seems to be able to.  Not sure if this is some caching issue that will
be solved by a clean or if there's some mixed up config.
"""

from lib.v1.config import FullPath, TEST_HTTP_DOMAIN
from lib.v1.common import PlayerInfo
import requests
import json


def prettify_json(response_json):
    return json.dumps(response_json, indent=2, default=str)


if __name__ == "__main__":
    r = requests.get(f"{TEST_HTTP_DOMAIN}")
    print(prettify_json(r.json()))

    r = requests.get(f"{TEST_HTTP_DOMAIN}/{FullPath.JOIN.value}")
    player_info = PlayerInfo(**r.json()["player_info"])
    print(player_info)

    r = requests.get(
        f"{TEST_HTTP_DOMAIN}/{FullPath.PING.value}".replace(
            "{player_session_uuid}", player_info.id
        )
    )
    print(prettify_json(r.json()))

    r = requests.get(
        f"{TEST_HTTP_DOMAIN}/{FullPath.UPDATE.value}".replace(
            "{player_session_uuid}", player_info.id
        )
    )
    print(prettify_json(r.json()))

    r = requests.get(
        f"{TEST_HTTP_DOMAIN}/{FullPath.LEAVE.value}".replace(
            "{player_session_uuid}", player_info.id
        )
    )
    print(prettify_json(r.json()))
