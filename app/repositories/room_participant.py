from typing import Optional, Sequence

from sqlalchemy import delete, select

from app.db.models import RoomParticipant
from .base import BaseRepository


class RoomParticipantRepository(BaseRepository[RoomParticipant]):
    _model = RoomParticipant

    async def get_by_room_and_user(
        self, room_id: int, user_id: int
    ) -> Optional[RoomParticipant]:
        stmt = select(RoomParticipant).where(
            RoomParticipant.room_id == room_id,
            RoomParticipant.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_room(self, room_id: int) -> Sequence[RoomParticipant]:
        stmt = select(RoomParticipant).where(
            RoomParticipant.room_id == room_id
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: int) -> Sequence[RoomParticipant]:
        stmt = select(RoomParticipant).where(
            RoomParticipant.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def delete_by_room_and_user(
        self, room_id: int, user_id: int
    ) -> bool:
        stmt = delete(RoomParticipant).where(
            RoomParticipant.room_id == room_id,
            RoomParticipant.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0
