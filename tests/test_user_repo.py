import pytest

from app.db.models import User


class TestUserRepositoryCreate:

    async def test_create_user(self, user_repo):
        user = await user_repo.create(user_id=12345, username="alice")

        assert user.id is not None
        assert user.user_id == 12345
        assert user.username == "alice"

    async def test_create_user_without_username(self, user_repo):
        user = await user_repo.create(user_id=99999)

        assert user.user_id == 99999
        assert user.username is None


class TestUserRepositoryGetById:

    async def test_get_existing_user(self, user_repo, make_user):
        created = await make_user(user_id=11111, username="bob")

        found = await user_repo.get_by_id(created.id)

        assert found is not None
        assert found.user_id == 11111
        assert found.username == "bob"

    async def test_get_nonexistent_user_returns_none(self, user_repo):
        assert await user_repo.get_by_id(999_999) is None


class TestUserRepositoryGetByUserId:

    async def test_find_by_user_id(self, user_repo, make_user):
        await make_user(user_id=77777, username="charlie")

        found = await user_repo.get_by_user_id(77777)

        assert found is not None
        assert found.username == "charlie"

    async def test_not_found_returns_none(self, user_repo):
        assert await user_repo.get_by_user_id(000000) is None


class TestUserRepositoryGetAll:

    async def test_get_all_empty(self, user_repo):
        users = await user_repo.get_all()
        assert len(users) == 0

    async def test_get_all_multiple(self, user_repo, make_user):
        await make_user(user_id=1001)
        await make_user(user_id=1002)
        await make_user(user_id=1003)

        users = await user_repo.get_all()
        assert len(users) == 3


class TestUserRepositoryDelete:

    async def test_delete_existing_user(self, user_repo, make_user):
        user = await make_user(user_id=55555)

        result = await user_repo.delete(user.id)

        assert result is True
        assert await user_repo.get_by_id(user.id) is None

    async def test_delete_nonexistent_returns_false(self, user_repo):
        result = await user_repo.delete(999_999)
        assert result is False
