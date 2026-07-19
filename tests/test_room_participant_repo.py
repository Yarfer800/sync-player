import pytest

from app.db.models import RoomParticipant, ParticipantRole


class TestParticipantCreate:

    async def test_create_participant(self, participant_repo, make_user, make_room):
        user = await make_user(user_id=2001)
        room = await make_room(content_title="Party Room")

        participant = await participant_repo.create(
            room_id=room.room_id,
            user_id=user.user_id,
            role=ParticipantRole.OWNER,
        )

        assert participant.id is not None
        assert participant.room_id == room.room_id
        assert participant.user_id == user.user_id
        assert participant.role == ParticipantRole.OWNER

    async def test_create_participant_default_role(
        self, participant_repo, make_user, make_room
    ):
        user = await make_user(user_id=2002)
        room = await make_room(content_title="Default Room")

        participant = await participant_repo.create(
            room_id=room.room_id,
            user_id=user.user_id,
        )

        assert participant.role == ParticipantRole.GUEST


class TestParticipantGetByRoom:

    async def test_empty_room(self, participant_repo, make_room):
        room = await make_room(content_title="Empty Room")

        participants = await participant_repo.get_by_room(room.room_id)
        assert len(participants) == 0

    async def test_multiple_participants(
        self, participant_repo, make_user, make_room
    ):
        room = await make_room(content_title="Full Room")
        u1 = await make_user(user_id=3001)
        u2 = await make_user(user_id=3002)
        u3 = await make_user(user_id=3003)

        for u in (u1, u2, u3):
            await participant_repo.create(
                room_id=room.room_id, user_id=u.user_id
            )

        participants = await participant_repo.get_by_room(room.room_id)
        assert len(participants) == 3


class TestParticipantGetByUser:

    async def test_user_in_multiple_rooms(
        self, participant_repo, make_user, make_room
    ):
        user = await make_user(user_id=4001)
        r1 = await make_room(content_title="Room A")
        r2 = await make_room(content_title="Room B")

        await participant_repo.create(room_id=r1.room_id, user_id=user.user_id)
        await participant_repo.create(room_id=r2.room_id, user_id=user.user_id)

        participations = await participant_repo.get_by_user(user.user_id)
        assert len(participations) == 2

    async def test_user_not_in_any_room(self, participant_repo, make_user):
        user = await make_user(user_id=4002)

        participations = await participant_repo.get_by_user(user.user_id)
        assert len(participations) == 0


class TestParticipantGetByRoomAndUser:

    async def test_find_existing_participant(
        self, participant_repo, make_user, make_room
    ):
        user = await make_user(user_id=5001)
        room = await make_room(content_title="Specific Room")
        await participant_repo.create(
            room_id=room.room_id,
            user_id=user.user_id,
            role=ParticipantRole.OWNER,
        )

        found = await participant_repo.get_by_room_and_user(
            room.room_id, user.user_id
        )

        assert found is not None
        assert found.role == ParticipantRole.OWNER

    async def test_not_found_returns_none(
        self, participant_repo, make_user, make_room
    ):
        user = await make_user(user_id=5002)
        room = await make_room(content_title="Other Room")

        found = await participant_repo.get_by_room_and_user(
            room.room_id, user.user_id
        )
        assert found is None


class TestParticipantDeleteByRoomAndUser:

    async def test_delete_existing(self, participant_repo, make_user, make_room):
        user = await make_user(user_id=6001)
        room = await make_room(content_title="Delete Room")
        await participant_repo.create(
            room_id=room.room_id, user_id=user.user_id
        )

        result = await participant_repo.delete_by_room_and_user(
            room.room_id, user.user_id
        )

        assert result is True
        assert (
            await participant_repo.get_by_room_and_user(
                room.room_id, user.user_id
            )
            is None
        )

    async def test_delete_nonexistent_returns_false(
        self, participant_repo, make_user, make_room
    ):
        user = await make_user(user_id=6002)
        room = await make_room(content_title="No Part Room")

        result = await participant_repo.delete_by_room_and_user(
            room.room_id, user.user_id
        )
        assert result is False


class TestParticipantDelete:

    async def test_delete_by_pk(self, participant_repo, make_user, make_room):
        user = await make_user(user_id=7001)
        room = await make_room(content_title="PK Delete Room")
        participant = await participant_repo.create(
            room_id=room.room_id, user_id=user.user_id
        )

        result = await participant_repo.delete(participant.id)

        assert result is True
        assert await participant_repo.get_by_id(participant.id) is None
