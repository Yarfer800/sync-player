import pytest

from app.db.models import Room


class TestRoomRepositoryCreate:

    async def test_create_room_with_title(self, room_repo):
        room = await room_repo.create(content_title="Cool Song", title="Music Room")

        assert room.room_id is not None
        assert room.content_title == "Cool Song"
        assert room.title == "Music Room"

    async def test_create_room_without_title(self, room_repo):
        room = await room_repo.create(content_title="Another Video")

        assert room.room_id is not None
        assert room.content_title == "Another Video"
        assert room.title is None


class TestRoomRepositoryGetById:

    async def test_get_existing_room(self, room_repo, make_room):
        created = await make_room(content_title="Test Video")

        found = await room_repo.get_by_id(created.room_id)

        assert found is not None
        assert found.content_title == "Test Video"

    async def test_get_nonexistent_room_returns_none(self, room_repo):
        assert await room_repo.get_by_id(999_999) is None


class TestRoomRepositoryGetAll:

    async def test_empty_list(self, room_repo):
        rooms = await room_repo.get_all()
        assert len(rooms) == 0

    async def test_multiple_rooms(self, room_repo, make_room):
        await make_room(content_title="Video A")
        await make_room(content_title="Video B")

        rooms = await room_repo.get_all()
        assert len(rooms) == 2
        titles = {r.content_title for r in rooms}
        assert titles == {"Video A", "Video B"}


class TestRoomRepositoryDelete:

    async def test_delete_existing_room(self, room_repo, make_room):
        room = await make_room(content_title="To Delete")

        result = await room_repo.delete(room.room_id)

        assert result is True
        assert await room_repo.get_by_id(room.room_id) is None

    async def test_delete_nonexistent_returns_false(self, room_repo):
        result = await room_repo.delete(999_999)
        assert result is False
