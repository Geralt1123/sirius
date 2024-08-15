from abc import ABC, abstractmethod
from typing import Any


class Service(ABC):
    """Предоставляет синхронный интерфейс вызова сервиса"""

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class AsyncService(ABC):
    """Предоставляет асинхронный интерфейс вызова сервиса"""

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
