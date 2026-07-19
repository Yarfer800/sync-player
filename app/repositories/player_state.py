import json
from typing import Optional
from redis.asyncio import Redis
from app.schemas.player_state import PlayerState

class PlayerStateRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _get_key(self, room_id: int) -> str:
        return f"room:{room_id}:player_state"

    async def get_state(self, room_id: int) -> Optional[PlayerState]:
        data = await self.redis.get(self._get_key(room_id))
        if data:
            return PlayerState.model_validate_json(data)
        return None

    async def set_state(self, room_id: int, state: PlayerState) -> None:
        await self.redis.set(self._get_key(room_id), state.model_dump_json())
