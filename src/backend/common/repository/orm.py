from __future__ import annotations

from common.models.orm.base import Base as BaseORMModel
from interfaces import AbstractAsyncRepository
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped


class BaseORMRepository(AbstractAsyncRepository):
    Model: BaseORMModel
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._query = select(self.Model)

    async def insert(self, instance: BaseORMModel) -> None:
        self._session.add(instance)

    async def insert_many(self, instances: list[BaseORMModel]) -> None:
        self._session.add_all(instances)

    async def update(self, instance: BaseORMRepository.Model, **update_fields) -> None:
        update_fields = update_fields or {}
        for k, v in update_fields.items():
            if k in instance.__dict__:
                setattr(instance, k, v)

    async def update_by_filter(self, values: dict, *filters, **named_filters) -> None:
        await self._session.execute(update(self.Model).filter(*filters).filter_by(**named_filters).values(**values))

    async def get(self, *filters, **named_filters) -> BaseORMRepository.Model | None:
        result = await self._session.execute(self._query.filter(*filters).filter_by(**named_filters))
        return result.scalars().first()

    async def list(
        self, *filters, order_by: Mapped = None, unique: bool = False, **named_filters
    ) -> list[BaseORMRepository.Model]:
        result = await self._session.execute(self._query.filter(*filters).filter_by(**named_filters).order_by(order_by))
        if unique:
            return result.scalars().unique().all()
        else:
            return result.scalars().all()

    async def delete(self, instance: BaseORMRepository.Model) -> None:
        await self._session.delete(instance)

    async def delete_by_filter(self, *filters, **named_filters) -> None:
        await self._session.execute(delete(self.Model).filter(*filters).filter_by(**named_filters))
