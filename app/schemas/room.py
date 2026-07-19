from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoomCreate(BaseModel):
    content_title: str
    title: Optional[str] = None
    password: Optional[str] = None


class RoomOut(BaseModel):
    room_id: int
    title: Optional[str]
    content_title: str
    created_at: datetime
    participant_count: int = 0
    is_private: bool = False

    class Config:
        from_attributes = True


class RoomDetail(BaseModel):
    room_id: int
    title: Optional[str]
    content_title: str
    created_at: datetime
    is_private: bool = False
    invite_code: Optional[str] = None
    participants: list["ParticipantOut"]

    class Config:
        from_attributes = True


class ParticipantOut(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class RoomJoin(BaseModel):
    password: Optional[str] = None


class RoomInviteResponse(BaseModel):
    invite_code: str


class RoomJoinByInvite(BaseModel):
    invite_code: str
