"""
Client that goes along with V2 server. Start server at `server/v2/app.py`
before running this file.


Run with:
```
source .venv/bin/activate
python client/v2/main.py
```
"""

import sys
from lib.v2.game_simple import *
from lib.v1.common import WS_Message, parse_WS_Message
from lib.v1.config import TEST_DOMAIN, FullPath
from websockets import connect
from websockets.asyncio.client import ClientConnection


def get_websocket_url(game):
    DOMAIN = os.environ.get("DOMAIN", TEST_DOMAIN)
    SECURE_S = "s" if os.environ.get("SECURE", "false").lower() == "true" else ""
    url = f"ws{SECURE_S}://{DOMAIN}{FullPath.WS.value}".replace(
        "{player_session_uuid}", game.get_cur_player_id()
    )
    return url


async def out_worker(websocket: ClientConnection, out_queue: asyncio.Queue):
    while True:
        message: WS_Message = await out_queue.get()
        await websocket.send(message.model_dump_json())
        out_queue.task_done()


async def in_worker(websocket: ClientConnection, in_queue: asyncio.Queue):
    while True:
        message = await websocket.recv()
        ws_msg: WS_Message = parse_WS_Message(message)
        if ws_msg.message_type == "SERVER_POSITION_V2":
            print(ws_msg)
            in_queue.put_nowait(ws_msg)


async def async_main():
    os.environ["IS_SERVER_MODE"] = "FALSE"
    game = create_game()
    game.network_client = NetworkClient()
    url = get_websocket_url(game)

    async with connect(
        url, close_timeout=0.1  # Didn't implement closing functionality yet on server
    ) as websocket:
        tasks = [
            asyncio.create_task(out_worker(websocket, game.network_client.out_queue)),
            asyncio.create_task(in_worker(websocket, game.network_client.in_queue)),
        ]
        while game.running:
            game.update()
            await asyncio.sleep(0)
    # Cancel all tasks
    for task in tasks:
        task.cancel()

    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(async_main())
    pg.quit()
    sys.exit()
