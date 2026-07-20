import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_download_chunk(client: AsyncClient, auth_user):
    await auth_user()
    with patch("app.services.player.YTDlpPlayer.download_chunk_of_video") as mock_dl:
        async def fake_dl(*args, **kwargs):
            with open(args[2], "wb") as f:
                f.write(b"fake video")
        mock_dl.side_effect = fake_dl
        
        response = await client.post("/api/player/download", json={
            "url": "https://youtu.be/fake",
            "start_time": 0,
            "end_time": 10
        })
        assert response.status_code == 200
        assert response.content == b"fake video"

@pytest.mark.asyncio
async def test_download_chunk_invalid_time(client: AsyncClient, auth_user):
    await auth_user()
    response = await client.post("/api/player/download", json={
        "url": "https://youtu.be/fake",
        "start_time": 10,
        "end_time": 5
    })
    assert response.status_code == 400
