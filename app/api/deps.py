import hashlib
import hmac
import json
from typing import Annotated
from urllib.parse import parse_qs, unquote

from fastapi import Depends, Header, HTTPException, status, WebSocketException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Config
from app.db.engine import build_engine, build_session_factory
from app.db.models import User
from app.db.redis import redis_client
from app.repositories.player_state import PlayerStateRepository
from app.services.player_state import PlayerStateService
from redis.asyncio import Redis
from app.repositories import (
    UserRepository,
    RoomRepository,
    RoomParticipantRepository,
    MessageRepository,
)

config = Config()

engine = build_engine(config.database_url)
session_factory = build_session_factory(engine)


async def get_session() -> AsyncSession:
    async with session_factory() as session:
        async with session.begin():
            yield session


def validate_init_data(init_data: str, bot_token: str) -> dict:
    parsed = parse_qs(init_data, keep_blank_values=True)

    check_hash = parsed.pop("hash", [None])[0]
    if not check_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in init data",
        )

    data_check_pairs = sorted(
        (k, unquote(v[0])) for k, v in parsed.items()
    )
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_check_pairs)

    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, check_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid init data signature",
        )

    user_data = parsed.get("user", [None])[0]
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user in init data",
        )

    return json.loads(unquote(user_data))


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    x_init_data: Annotated[str, Header()],
) -> User:
    tg_user = validate_init_data(x_init_data, config.token)

    tg_id: int = tg_user["id"]
    username: str | None = tg_user.get("username")

    repo = UserRepository(session)
    user = await repo.get_by_user_id(tg_id)

    if user is None:
        user = await repo.create(user_id=tg_id, username=username)
    elif user.username != username and username is not None:
        await repo.update(user.id, username=username)
        user.username = username

    return user


async def get_current_user_ws(
    session: Annotated[AsyncSession, Depends(get_session)],
    init_data: str = Query(..., alias="init_data"),
) -> User:
    try:
        tg_user = validate_init_data(init_data, config.token)
    except HTTPException as e:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e.detail))

    tg_id: int = tg_user["id"]
    username: str | None = tg_user.get("username")

    repo = UserRepository(session)
    user = await repo.get_by_user_id(tg_id)

    if user is None:
        user = await repo.create(user_id=tg_id, username=username)
    elif user.username != username and username is not None:
        await repo.update(user.id, username=username)
        user.username = username

    return user


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserWS = Annotated[User, Depends(get_current_user_ws)]


def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_room_repo(session: SessionDep) -> RoomRepository:
    return RoomRepository(session)


def get_participant_repo(session: SessionDep) -> RoomParticipantRepository:
    return RoomParticipantRepository(session)


def get_message_repo(session: SessionDep) -> MessageRepository:
    return MessageRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
RoomRepoDep = Annotated[RoomRepository, Depends(get_room_repo)]
ParticipantRepoDep = Annotated[RoomParticipantRepository, Depends(get_participant_repo)]
MessageRepoDep = Annotated[MessageRepository, Depends(get_message_repo)]


async def get_redis_client() -> Redis:
    yield redis_client


RedisDep = Annotated[Redis, Depends(get_redis_client)]


def get_player_state_repo(redis: RedisDep) -> PlayerStateRepository:
    return PlayerStateRepository(redis)


PlayerStateRepoDep = Annotated[PlayerStateRepository, Depends(get_player_state_repo)]


def get_player_state_service(repo: PlayerStateRepoDep) -> PlayerStateService:
    return PlayerStateService(repo)


PlayerStateServiceDep = Annotated[PlayerStateService, Depends(get_player_state_service)]
