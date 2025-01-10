import asyncio
from server.v1.app import start_uvicorn_server
from lib.v1.dummy_game import async_simple_game_function


if __name__ == "__main__":
    start_uvicorn_server()
