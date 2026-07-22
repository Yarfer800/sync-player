from abc import ABC
from typing import Generic, Optional, Sequence, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository(ABC, Generic[Model]):
    _model: type[Model]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **kwargs) -> Model:
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, pk: int) -> Optional[Model]:
        return await self._session.get(self._model, pk)

    async def get_all(self) -> Sequence[Model]:
        stmt = select(self._model)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, pk: int, **kwargs) -> Optional[Model]:
        pk_col = self._model.__table__.primary_key.columns.values()[0]
        stmt = (
            update(self._model)
            .where(pk_col == pk)
            .values(**kwargs)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one_or_none()

    async def delete(self, pk: int) -> bool:
        pk_col = self._model.__table__.primary_key.columns.values()[0]
        stmt = delete(self._model).where(pk_col == pk)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0
