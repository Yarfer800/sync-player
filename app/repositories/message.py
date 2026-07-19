from typing import Sequence

from sqlalchemy import delete, select

from app.db.models import Message
from .base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    _model = Message

    async def get_by_room(
        self,
        room_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Message]:
        stmt = (
            select(Message)
            .where(Message.room_id == room_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Message]:
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def delete_by_room(self, room_id: int) -> int:
        stmt = delete(Message).where(Message.room_id == room_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
