import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_room(client: AsyncClient, auth_user):
    await auth_user()
    response = await client.post("/api/rooms", json={
        "content_title": "Test Video",
        "title": "My Room",
        "password": "pass"
    })
    assert response.status_code == 201
    room_id = response.json()["room_id"]
    assert response.json()["title"] == "My Room"

    response = await client.get(f"/api/rooms/{room_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "My Room"

    response = await client.get("/api/rooms")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_join_leave_room(client: AsyncClient, auth_user):
    await auth_user(user_id=1, username="u1")
    resp = await client.post("/api/rooms", json={"content_title": "Video"})
    room_id = resp.json()["room_id"]
    
    await auth_user(user_id=2, username="u2")
    resp = await client.post(f"/api/rooms/{room_id}/join", json={})
    assert resp.status_code == 200
    
    resp = await client.get(f"/api/rooms/{room_id}/participants")
    assert len(resp.json()) == 2
    
    resp = await client.post(f"/api/rooms/{room_id}/leave")
    assert resp.status_code == 204
    
    resp = await client.get(f"/api/rooms/{room_id}/participants")
    assert len(resp.json()) == 1

@pytest.mark.asyncio
async def test_invite_join(client: AsyncClient, auth_user):
    await auth_user(user_id=1, username="u1")
    resp = await client.post("/api/rooms", json={"content_title": "Video"})
    room_id = resp.json()["room_id"]

    resp = await client.post(f"/api/rooms/{room_id}/invite")
    assert resp.status_code == 200
    invite_code = resp.json()["invite_code"]

    await auth_user(user_id=2, username="u2")
    resp = await client.post("/api/rooms/join/invite", json={"invite_code": invite_code})
    if resp.status_code != 200:
        print("ERROR RESPONSE:", resp.text)
    assert resp.status_code == 200
    assert resp.json()["room_id"] == room_id
