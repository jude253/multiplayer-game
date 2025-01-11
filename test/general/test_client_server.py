from server.v1.dummy_game_with_server_socket import start_uvicorn_server
from client.v1.dummy_game_with_socket import (
    async_simple_game_function_with_socket_communication,
)
import asyncio

import unittest


async def main(self: unittest.TestCase):
    """
    NOTE: pygame may only open one window and draw on it from both game
    loops.
    """
    # Start server first in task, allowing .5 seconds for start up
    server_task = asyncio.create_task(start_uvicorn_server())
    await asyncio.sleep(0.5)

    # Start client, which is communicating with server
    client_task = asyncio.create_task(
        async_simple_game_function_with_socket_communication()
    )

    # give some runtime
    await asyncio.sleep(0.5)

    # Check the server and client to ensure no excpetions have been raised:
    server_exception = None
    client_exception = None

    try:
        server_task.exception()
    except Exception as e:
        server_exception = e

    try:
        client_task.exception()
    except Exception as e:
        client_exception = e

    # Ensure that asyncio.exceptions.InvalidStateError, meaning that no exceptions raised
    self.assertIsInstance(server_exception, asyncio.exceptions.InvalidStateError)
    self.assertIsInstance(client_exception, asyncio.exceptions.InvalidStateError)

    # Cancel the client and server to end the test
    client_task.cancel()
    server_task.cancel()


class TestDummyGameClientServer(unittest.TestCase):
    def test_async_simple_game_function(self):
        """
        Check the client and server can run at the same time,
        communicating, and having no errors.
        """
        asyncio.run(main(self))


if __name__ == "__main__":
    unittest.main()
