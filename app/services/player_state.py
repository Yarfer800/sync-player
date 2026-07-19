from app.repositories.player_state import PlayerStateRepository
from app.schemas.player_state import PlayerState

class PlayerStateService:
    def __init__(self, repo: PlayerStateRepository):
        self.repo = repo

    async def get_room_state(self, room_id: int) -> PlayerState:
        state = await self.repo.get_state(room_id)
        if state is None:
            # Return default state if not initialized
            return PlayerState(room_id=room_id)
        return state

    async def update_room_state(self, room_id: int, state: PlayerState) -> PlayerState:
        # Enforce the correct room_id on the state object
        state.room_id = room_id
        await self.repo.set_state(room_id, state)
        return state
