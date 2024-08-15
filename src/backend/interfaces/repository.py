from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractRepository:
    Model: Any
    _session: Any

    def __init__(self, session: Any) -> None:
        self._session = session


class AbstractAsyncRepository(AbstractRepository, ABC):
    @abstractmethod
    async def get(self, *filters, **named_filters) -> AbstractRepository.Model | None:
        """Получение элемента"""

    @abstractmethod
    async def insert(self, instance: AbstractRepository.Model) -> None:
        """Вставка элемента"""

    @abstractmethod
    async def delete(self, instance: AbstractRepository.Model) -> None:
        """Удаление элемента"""

    @abstractmethod
    async def update(self, instance: AbstractRepository.Model, **update_fields) -> None:
        """Изменение элемента"""


class AbstractSyncRepository(AbstractRepository):
    @abstractmethod
    def get(self, *filters, **named_filters) -> AbstractRepository.Model | None:
        """Получение элемента"""

    @abstractmethod
    def insert(self, instance: AbstractRepository.Model) -> None:
        """Вставка элемента"""

    @abstractmethod
    def delete(self, instance: AbstractRepository.Model) -> None:
        """Удаление элемента"""

    @abstractmethod
    def update(self, instance: AbstractRepository.Model, **update_fields) -> None:
        """Изменение элемента"""
