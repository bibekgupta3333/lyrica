"""
Integration tests for lyrics management endpoints.
"""

from uuid import UUID

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.integration
@pytest.mark.asyncio
class TestLyricsPublicEndpoints:
    """Test public lyrics endpoints (no auth required)."""

    async def test_explore_public_lyrics(self, client: AsyncClient):
        """Test exploring public lyrics."""
        response = await client.get("/api/v1/lyrics/public/explore")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_explore_public_lyrics_with_genre(self, client: AsyncClient):
        """Test exploring public lyrics filtered by genre."""
        response = await client.get("/api/v1/lyrics/public/explore?genre=pop&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
@pytest.mark.asyncio
class TestLyricsProtectedEndpoints:
    """Test protected lyrics endpoints (auth required)."""

    async def test_list_lyrics_authenticated(self, client: AsyncClient, user_token: str):
        """Test listing lyrics with authentication."""
        response = await client.get(
            "/api/v1/lyrics/",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_lyrics_unauthorized(self, client: AsyncClient):
        """Test listing lyrics without authentication."""
        response = await client.get("/api/v1/lyrics/")

        assert response.status_code == 401

    async def test_generate_lyrics(self, client: AsyncClient, user_token: str):
        """Test generating new lyrics."""
        response = await client.post(
            "/api/v1/lyrics/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Test Song",
                "content": "[Verse 1]\nTest content\n[Chorus]\nTest chorus",
                "structure": {"sections": []},
                "genre": "pop",
                "mood": "happy",
            },
        )

        assert response.status_code in [201, 200]
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Song"

    async def test_get_lyrics_by_id(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test retrieving lyrics by ID."""
        response = await client.get(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_lyrics.id)
        assert data["title"] == test_lyrics.title

    async def test_update_lyrics(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test updating lyrics."""
        response = await client.put(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    async def test_delete_lyrics(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test deleting lyrics."""
        response = await client.delete(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 204

    async def test_get_lyrics_history(self, client: AsyncClient, user_token: str):
        """Test getting lyrics history."""
        response = await client.get(
            "/api/v1/lyrics/history",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
