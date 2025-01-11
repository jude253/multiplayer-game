from server.v1.app import start_uvicorn_server
import asyncio

if __name__ == "__main__":
    asyncio.run(start_uvicorn_server())
