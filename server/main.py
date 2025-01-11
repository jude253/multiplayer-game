from server.v1.dummy_game_with_server_socket import start_uvicorn_server
import asyncio

if __name__ == "__main__":
    asyncio.run(start_uvicorn_server())
