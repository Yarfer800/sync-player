from typing import Optional

from sqlalchemy import select

from app.db.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    _model = User

    async def get_by_user_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
