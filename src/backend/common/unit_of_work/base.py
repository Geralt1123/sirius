from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AbstractAsyncUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self): ...

    async def __aexit__(self, *args):
        await self.rollback()

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class AbstractSyncUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self): ...

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...


class BaseORMUnitOfWork(AbstractAsyncUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self._session: AsyncSession = self.session_factory()
        return self

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        self._session.expunge_all()
        await self._session.rollback()

    def expunge(self, instance: Any):
        self._session.expunge(instance)
