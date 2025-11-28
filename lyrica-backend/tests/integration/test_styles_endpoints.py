"""
Integration tests for styles and genres endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestStylesEndpoints:
    """Test styles and genres endpoints."""

    async def test_get_all_styles(self, simple_client: AsyncClient):
        """Test getting all styles."""
        response = await simple_client.get("/api/v1/styles/")

        assert response.status_code == 200
        data = response.json()
        assert "genres" in data
        assert "moods" in data
        assert "themes" in data
        assert "style_references" in data
        assert len(data["genres"]) == 12
        assert len(data["moods"]) == 10
        assert len(data["themes"]) == 10

    async def test_get_genres(self, client: AsyncClient):
        """Test getting genres."""
        response = await client.get("/api/v1/styles/genres")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 12
        assert all("name" in genre for genre in data)
        assert all("description" in genre for genre in data)

    async def test_get_moods(self, client: AsyncClient):
        """Test getting moods."""
        response = await client.get("/api/v1/styles/moods")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10

    async def test_get_themes(self, client: AsyncClient):
        """Test getting themes."""
        response = await client.get("/api/v1/styles/themes")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10

    async def test_get_references(self, client: AsyncClient):
        """Test getting style references."""
        response = await client.get("/api/v1/styles/references")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10
