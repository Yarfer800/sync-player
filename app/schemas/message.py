from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    text: str
    image: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    text: str
    image: Optional[str]
    user_id: int
    username: Optional[str] = None
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True
