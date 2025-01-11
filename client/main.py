"""
This is a rough draft of the client to call the server with a game.

To test, start the server in `server/v1/app.py`,

Then run: bazel run //client:v1_client

NOTE: Optionally run `python -m websockets ws://127.0.0.1:8000/v1/ws/2`
from another terminal window to watch the messages as another client.
"""

import asyncio
from client.v1.dummy_game_with_socket import (
    async_simple_game_function_with_socket_communication,
)


if __name__ == "__main__":
    asyncio.run(async_simple_game_function_with_socket_communication())
