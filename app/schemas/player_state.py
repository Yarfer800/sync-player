from typing import Optional
from pydantic import BaseModel

class PlayerState(BaseModel):
    room_id: int
    current_timecode: float = 0.0
    video_source_link: Optional[str] = None
    is_paused: bool = True
