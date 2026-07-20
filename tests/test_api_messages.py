import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_send_and_list_messages(client: AsyncClient, auth_user):
    user = await auth_user()
    resp = await client.post("/api/rooms", json={"content_title": "Video"})
    room_id = resp.json()["room_id"]
    
    resp = await client.post(f"/api/rooms/{room_id}/messages", json={
        "text": "Hello world"
    })
    assert resp.status_code == 201
    msg_id = resp.json()["id"]
    
    resp = await client.get(f"/api/rooms/{room_id}/messages")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["text"] == "Hello world"
    
    resp = await client.delete(f"/api/rooms/{room_id}/messages/{msg_id}")
    assert resp.status_code == 204
