from app.db.models import Room
from .base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    _model = Room
