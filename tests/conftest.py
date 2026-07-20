import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import build_engine, build_session_factory, init_db, drop_db
from app.db.models import User, Room
from app.repositories import (
    UserRepository,
    RoomRepository,
    RoomParticipantRepository,
    MessageRepository,
)
from httpx import AsyncClient, ASGITransport

import os
os.environ.setdefault("TOKEN", "test_token")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("ADMIN_ID", "1")

from app.app import app
from app.api.deps import get_session, get_current_user, get_current_user_ws


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    eng = build_engine("sqlite+aiosqlite://")
    await init_db(eng)
    yield eng
    await drop_db(eng)
    await eng.dispose()


@pytest.fixture()
async def session(engine) -> AsyncSession:
    factory = build_session_factory(engine)
    async with factory() as sess:
        async with sess.begin():
            yield sess
            await sess.rollback()

@pytest.fixture
def test_app(session: AsyncSession):
    app.dependency_overrides[get_session] = lambda: session
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
async def client(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_user(test_app, make_user):
    async def _auth(user_id=100, username="testuser"):
        user = await make_user(user_id=user_id, username=username)
        test_app.dependency_overrides[get_current_user] = lambda: user
        test_app.dependency_overrides[get_current_user_ws] = lambda: user
        return user
    return _auth


@pytest.fixture()
def user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture()
def room_repo(session: AsyncSession) -> RoomRepository:
    return RoomRepository(session)


@pytest.fixture()
def participant_repo(session: AsyncSession) -> RoomParticipantRepository:
    return RoomParticipantRepository(session)


@pytest.fixture()
def message_repo(session: AsyncSession) -> MessageRepository:
    return MessageRepository(session)


@pytest.fixture()
def make_user(session: AsyncSession):
    _counter = 0

    async def _make(user_id: int | None = None, username: str | None = None, **kw):
        nonlocal _counter
        _counter += 1
        defaults = {
            "user_id": user_id or (100_000 + _counter),
            "username": username or f"testuser_{_counter}",
        }
        defaults.update(kw)
        user = User(**defaults)
        session.add(user)
        await session.flush()
        return user

    return _make


@pytest.fixture()
def make_room(session: AsyncSession):
    _counter = 0

    async def _make(content_title: str | None = None, title: str | None = None, **kw):
        nonlocal _counter
        _counter += 1
        defaults = {
            "content_title": content_title or f"Test Video #{_counter}",
            "title": title,
        }
        defaults.update(kw)
        room = Room(**defaults)
        session.add(room)
        await session.flush()
        return room

    return _make
