import asyncio

from client.v2.client import async_main
import pygame as pg
import sys

if __name__ == "__main__":
    asyncio.run(async_main())
    pg.quit()
    sys.exit()
