from fastapi import APIRouter

from .users import router as users_router
from .rooms import router as rooms_router
from .messages import router as messages_router
from .search import router as search_router
from .player import router as player_router

router = APIRouter(prefix="/api")
router.include_router(users_router)
router.include_router(rooms_router)
router.include_router(messages_router)
router.include_router(search_router)
router.include_router(player_router)
