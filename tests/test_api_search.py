import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_search_web(client: AsyncClient, auth_user):
    await auth_user()
    with patch("app.services.web_search.WebSearcher.search") as mock_search:
        mock_search.return_value = [{"title": "Example", "url": "https://example.com", "description": "Hello"}]
        response = await client.get("/api/search?query=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Example"
