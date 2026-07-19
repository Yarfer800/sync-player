from typing import Optional

from sqlalchemy import select

from app.db.models import Room
from .base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    _model = Room

    async def get_by_invite_code(self, invite_code: str) -> Optional[Room]:
        stmt = select(Room).where(Room.invite_code == invite_code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
