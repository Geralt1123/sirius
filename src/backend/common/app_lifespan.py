import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Sequence

from fastapi import FastAPI
from interfaces import AsyncService


@dataclass(kw_only=True)
class ApplicationLifeSpan:
    services: Sequence[AsyncService]
    tasks: list[asyncio.Task] | None = field(default=None)

    @asynccontextmanager
    async def __call__(self, app: FastAPI):
        self.tasks = [asyncio.create_task(service()) for service in self.services]

        yield

        self.tasks.clear()
