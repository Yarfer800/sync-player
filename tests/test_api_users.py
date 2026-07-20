import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_user):
    user = await auth_user(username="my_user")
    response = await client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "my_user"

@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, auth_user):
    user = await auth_user(username="old_user")
    response = await client.patch("/api/users/me", json={"username": "new_user"})
    assert response.status_code == 200
    assert response.json()["username"] == "new_user"
