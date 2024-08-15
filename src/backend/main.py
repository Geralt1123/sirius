import asyncio
import sys

from config import uvicorn_config
from uvicorn import run

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    run(**uvicorn_config.model_dump())
