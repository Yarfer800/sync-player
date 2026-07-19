import pytest

from app.db.models import Message


class TestMessageCreate:

    async def test_create_message(self, message_repo, make_user, make_room):
        user = await make_user(user_id=8001)
        room = await make_room(content_title="Chat Room")

        msg = await message_repo.create(
            text="Hello, world!",
            user_id=user.user_id,
            room_id=room.room_id,
        )

        assert msg.id is not None
        assert msg.text == "Hello, world!"
        assert msg.user_id == user.user_id
        assert msg.room_id == room.room_id
        assert msg.image is None

    async def test_create_message_with_image(self, message_repo, make_user, make_room):
        user = await make_user(user_id=8002)
        room = await make_room(content_title="Image Room")

        msg = await message_repo.create(
            text="Look!",
            image="https://example.com/photo.jpg",
            user_id=user.user_id,
            room_id=room.room_id,
        )

        assert msg.image == "https://example.com/photo.jpg"


class TestMessageGetByRoom:

    async def test_messages_in_room(self, message_repo, make_user, make_room):
        user = await make_user(user_id=9001)
        room = await make_room(content_title="Msg Room")

        await message_repo.create(text="First", user_id=user.user_id, room_id=room.room_id)
        await message_repo.create(text="Second", user_id=user.user_id, room_id=room.room_id)
        await message_repo.create(text="Third", user_id=user.user_id, room_id=room.room_id)

        messages = await message_repo.get_by_room(room.room_id)
        assert len(messages) == 3

    async def test_empty_room_returns_empty(self, message_repo, make_room):
        room = await make_room(content_title="Silent Room")

        messages = await message_repo.get_by_room(room.room_id)
        assert len(messages) == 0

    async def test_messages_do_not_leak_between_rooms(
        self, message_repo, make_user, make_room
    ):
        user = await make_user(user_id=9002)
        room_a = await make_room(content_title="Room A")
        room_b = await make_room(content_title="Room B")

        await message_repo.create(text="In A", user_id=user.user_id, room_id=room_a.room_id)
        await message_repo.create(text="In B", user_id=user.user_id, room_id=room_b.room_id)

        msgs_a = await message_repo.get_by_room(room_a.room_id)
        msgs_b = await message_repo.get_by_room(room_b.room_id)

        assert len(msgs_a) == 1
        assert msgs_a[0].text == "In A"
        assert len(msgs_b) == 1
        assert msgs_b[0].text == "In B"

    async def test_limit_and_offset(self, message_repo, make_user, make_room):
        user = await make_user(user_id=9003)
        room = await make_room(content_title="Paged Room")

        for i in range(5):
            await message_repo.create(
                text=f"msg_{i}", user_id=user.user_id, room_id=room.room_id
            )

        page = await message_repo.get_by_room(room.room_id, limit=2, offset=1)
        assert len(page) == 2


class TestMessageGetByUser:

    async def test_messages_by_user(self, message_repo, make_user, make_room):
        user = await make_user(user_id=10001)
        room = await make_room(content_title="User Msg Room")

        await message_repo.create(text="Hi", user_id=user.user_id, room_id=room.room_id)
        await message_repo.create(text="Bye", user_id=user.user_id, room_id=room.room_id)

        messages = await message_repo.get_by_user(user.user_id)
        assert len(messages) == 2

    async def test_no_messages_returns_empty(self, message_repo, make_user):
        user = await make_user(user_id=10002)

        messages = await message_repo.get_by_user(user.user_id)
        assert len(messages) == 0

    async def test_does_not_return_other_users_messages(
        self, message_repo, make_user, make_room
    ):
        user_a = await make_user(user_id=10003)
        user_b = await make_user(user_id=10004)
        room = await make_room(content_title="Mixed Room")

        await message_repo.create(text="From A", user_id=user_a.user_id, room_id=room.room_id)
        await message_repo.create(text="From B", user_id=user_b.user_id, room_id=room.room_id)

        msgs = await message_repo.get_by_user(user_a.user_id)
        assert len(msgs) == 1
        assert msgs[0].text == "From A"


class TestMessageDeleteByRoom:

    async def test_delete_all_messages_in_room(
        self, message_repo, make_user, make_room
    ):
        user = await make_user(user_id=11001)
        room = await make_room(content_title="Cleanup Room")

        await message_repo.create(text="a", user_id=user.user_id, room_id=room.room_id)
        await message_repo.create(text="b", user_id=user.user_id, room_id=room.room_id)
        await message_repo.create(text="c", user_id=user.user_id, room_id=room.room_id)

        deleted_count = await message_repo.delete_by_room(room.room_id)

        assert deleted_count == 3
        assert len(await message_repo.get_by_room(room.room_id)) == 0

    async def test_delete_empty_room_returns_zero(self, message_repo, make_room):
        room = await make_room(content_title="Already Empty")

        deleted_count = await message_repo.delete_by_room(room.room_id)
        assert deleted_count == 0

    async def test_delete_does_not_affect_other_rooms(
        self, message_repo, make_user, make_room
    ):
        user = await make_user(user_id=11002)
        room_target = await make_room(content_title="Target Room")
        room_safe = await make_room(content_title="Safe Room")

        await message_repo.create(text="target", user_id=user.user_id, room_id=room_target.room_id)
        await message_repo.create(text="safe", user_id=user.user_id, room_id=room_safe.room_id)

        await message_repo.delete_by_room(room_target.room_id)

        assert len(await message_repo.get_by_room(room_target.room_id)) == 0
        assert len(await message_repo.get_by_room(room_safe.room_id)) == 1


class TestMessageDelete:

    async def test_delete_single_message(self, message_repo, make_user, make_room):
        user = await make_user(user_id=12001)
        room = await make_room(content_title="Single Del Room")

        msg = await message_repo.create(
            text="deleteme", user_id=user.user_id, room_id=room.room_id
        )

        result = await message_repo.delete(msg.id)

        assert result is True
        assert await message_repo.get_by_id(msg.id) is None
