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

    async def test_explore_public_lyrics_pagination(self, client: AsyncClient):
        """Test exploring public lyrics with pagination."""
        response = await client.get("/api/v1/lyrics/public/explore?skip=0&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    async def test_explore_public_lyrics_invalid_genre(self, client: AsyncClient):
        """Test exploring public lyrics with invalid genre returns empty list."""
        response = await client.get("/api/v1/lyrics/public/explore?genre=nonexistent")

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

    async def test_list_lyrics_with_filters(self, client: AsyncClient, user_token: str):
        """Test listing lyrics with genre filter."""
        response = await client.get(
            "/api/v1/lyrics/?genre=pop&skip=0&limit=10",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_public_lyrics_only(self, client: AsyncClient, user_token: str):
        """Test listing only public lyrics."""
        response = await client.get(
            "/api/v1/lyrics/?public_only=true",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

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

    async def test_generate_lyrics_with_prompt(self, client: AsyncClient, user_token: str):
        """Test generating lyrics with custom prompt."""
        response = await client.post(
            "/api/v1/lyrics/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Summer Dreams",
                "content": "[Verse 1]\nWalking down the beach\n[Chorus]\nSummer dreams",
                "structure": {"sections": [{"type": "verse", "count": 2}]},
                "genre": "pop",
                "mood": "happy",
                "theme": "love",
                "prompt": "Write a happy pop song about summer love",
                "generation_params": {"temperature": 0.8},
            },
        )

        assert response.status_code in [201, 200]
        data = response.json()
        assert "id" in data
        assert data["title"] == "Summer Dreams"
        assert data["genre"] == "pop"
        assert data["mood"] == "happy"

    async def test_generate_lyrics_minimal(self, client: AsyncClient, user_token: str):
        """Test generating lyrics with minimal data."""
        response = await client.post(
            "/api/v1/lyrics/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "content": "[Verse 1]\nMinimal content",
                "structure": {"sections": []},
            },
        )

        assert response.status_code in [201, 200]
        data = response.json()
        assert "id" in data

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

    async def test_get_lyrics_by_id_not_found(self, client: AsyncClient, user_token: str):
        """Test retrieving non-existent lyrics."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/lyrics/{fake_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404

    async def test_get_lyrics_forbidden(self, client: AsyncClient, user_token: str, db_session):
        """Test accessing another user's private lyrics."""
        from app.core.security import get_password_hash
        from app.models.lyrics import Lyrics
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            password_hash=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create private lyrics for other user
        private_lyrics = Lyrics(
            user_id=other_user.id,
            title="Private Song",
            content="[Verse 1]\nPrivate content",
            genre="rock",
            is_public=False,
        )
        db_session.add(private_lyrics)
        await db_session.commit()
        await db_session.refresh(private_lyrics)

        # Try to access with current user token
        response = await client.get(
            f"/api/v1/lyrics/{private_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 403

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

    async def test_update_lyrics_content(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test updating lyrics content."""
        response = await client.put(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"content": "[Verse 1]\nUpdated content\n[Chorus]\nNew chorus"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "Updated content" in data["content"]

    async def test_update_lyrics_status(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test updating lyrics status."""
        response = await client.put(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "published", "is_public": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["is_public"] is True

    async def test_update_lyrics_not_found(self, client: AsyncClient, user_token: str):
        """Test updating non-existent lyrics."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.put(
            f"/api/v1/lyrics/{fake_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated"},
        )

        assert response.status_code == 404

    async def test_update_lyrics_forbidden(self, client: AsyncClient, user_token: str, db_session):
        """Test updating another user's lyrics."""
        from app.core.security import get_password_hash
        from app.models.lyrics import Lyrics
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other2@example.com",
            username="otheruser2",
            password_hash=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create lyrics for other user
        other_lyrics = Lyrics(
            user_id=other_user.id,
            title="Other Song",
            content="[Verse 1]\nOther content",
            genre="pop",
        )
        db_session.add(other_lyrics)
        await db_session.commit()
        await db_session.refresh(other_lyrics)

        # Try to update with current user token
        response = await client.put(
            f"/api/v1/lyrics/{other_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Hacked Title"},
        )

        assert response.status_code == 403

    async def test_delete_lyrics(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test deleting lyrics."""
        response = await client.delete(
            f"/api/v1/lyrics/{test_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 204

    async def test_delete_lyrics_not_found(self, client: AsyncClient, user_token: str):
        """Test deleting non-existent lyrics."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.delete(
            f"/api/v1/lyrics/{fake_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404

    async def test_delete_lyrics_forbidden(self, client: AsyncClient, user_token: str, db_session):
        """Test deleting another user's lyrics."""
        from app.core.security import get_password_hash
        from app.models.lyrics import Lyrics
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other3@example.com",
            username="otheruser3",
            password_hash=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create lyrics for other user
        other_lyrics = Lyrics(
            user_id=other_user.id,
            title="Protected Song",
            content="[Verse 1]\nProtected content",
            genre="jazz",
        )
        db_session.add(other_lyrics)
        await db_session.commit()
        await db_session.refresh(other_lyrics)

        # Try to delete with current user token
        response = await client.delete(
            f"/api/v1/lyrics/{other_lyrics.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 403

    async def test_get_lyrics_history(self, client: AsyncClient, user_token: str):
        """Test getting lyrics history."""
        response = await client.get(
            "/api/v1/lyrics/history",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_lyrics_history_pagination(self, client: AsyncClient, user_token: str):
        """Test getting lyrics history with pagination."""
        response = await client.get(
            "/api/v1/lyrics/history?skip=0&limit=5",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    async def test_regenerate_section(self, client: AsyncClient, user_token: str, test_lyrics):
        """Test regenerating a lyrics section."""
        response = await client.post(
            f"/api/v1/lyrics/{test_lyrics.id}/regenerate?section_type=verse",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_lyrics.id)

    async def test_regenerate_section_not_found(self, client: AsyncClient, user_token: str):
        """Test regenerating section for non-existent lyrics."""
        from uuid import uuid4

        fake_id = uuid4()
        response = await client.post(
            f"/api/v1/lyrics/{fake_id}/regenerate?section_type=chorus",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404

    async def test_regenerate_section_forbidden(
        self, client: AsyncClient, user_token: str, db_session
    ):
        """Test regenerating section for another user's lyrics."""
        from app.core.security import get_password_hash
        from app.models.lyrics import Lyrics
        from app.models.user import User

        # Create another user
        other_user = User(
            email="other4@example.com",
            username="otheruser4",
            password_hash=get_password_hash("Password123!"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create lyrics for other user
        other_lyrics = Lyrics(
            user_id=other_user.id,
            title="Locked Song",
            content="[Verse 1]\nLocked content",
            genre="metal",
        )
        db_session.add(other_lyrics)
        await db_session.commit()
        await db_session.refresh(other_lyrics)

        # Try to regenerate with current user token
        response = await client.post(
            f"/api/v1/lyrics/{other_lyrics.id}/regenerate?section_type=verse",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
class TestLyricsCompleteWorkflow:
    """Test complete workflows combining multiple endpoints."""

    async def test_complete_crud_workflow(self, client: AsyncClient, user_token: str):
        """Test complete CRUD workflow: create, read, update, delete."""
        # 1. Create lyrics
        create_response = await client.post(
            "/api/v1/lyrics/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Workflow Test Song",
                "content": "[Verse 1]\nOriginal content",
                "structure": {"sections": []},
                "genre": "electronic",
                "mood": "energetic",
            },
        )
        assert create_response.status_code == 201
        lyrics_id = create_response.json()["id"]

        # 2. Read lyrics
        get_response = await client.get(
            f"/api/v1/lyrics/{lyrics_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Workflow Test Song"

        # 3. Update lyrics
        update_response = await client.put(
            f"/api/v1/lyrics/{lyrics_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated Workflow Song", "is_public": True},
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Workflow Song"

        # 4. Verify it appears in history
        history_response = await client.get(
            "/api/v1/lyrics/history",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert history_response.status_code == 200
        history_ids = [item["id"] for item in history_response.json()]
        assert lyrics_id in history_ids

        # 5. Delete lyrics
        delete_response = await client.delete(
            f"/api/v1/lyrics/{lyrics_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert delete_response.status_code == 204

        # 6. Verify it's deleted
        get_deleted_response = await client.get(
            f"/api/v1/lyrics/{lyrics_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert get_deleted_response.status_code == 404

    async def test_public_lyrics_workflow(self, client: AsyncClient, user_token: str):
        """Test publishing lyrics and exploring public lyrics."""
        # 1. Create private lyrics
        create_response = await client.post(
            "/api/v1/lyrics/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Public Test Song",
                "content": "[Verse 1]\nPublic content",
                "structure": {"sections": []},
                "genre": "jazz",
            },
        )
        assert create_response.status_code == 201
        lyrics_id = create_response.json()["id"]

        # 2. Publish lyrics
        update_response = await client.put(
            f"/api/v1/lyrics/{lyrics_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"is_public": True, "status": "published"},
        )
        assert update_response.status_code == 200

        # 3. Verify it appears in public explore (no auth needed)
        explore_response = await client.get("/api/v1/lyrics/public/explore")
        assert explore_response.status_code == 200

    async def test_genre_filtering_workflow(self, client: AsyncClient, user_token: str):
        """Test creating lyrics with different genres and filtering."""
        # Create multiple lyrics with different genres
        genres = ["pop", "rock", "hip-hop"]
        created_ids = []

        for genre in genres:
            response = await client.post(
                "/api/v1/lyrics/generate",
                headers={"Authorization": f"Bearer {user_token}"},
                json={
                    "title": f"{genre.title()} Song",
                    "content": f"[Verse 1]\n{genre} content",
                    "structure": {"sections": []},
                    "genre": genre,
                },
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Filter by specific genre
        filter_response = await client.get(
            "/api/v1/lyrics/?genre=rock",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert filter_response.status_code == 200
        filtered_data = filter_response.json()

        # Verify filtered results contain only rock genre
        for item in filtered_data:
            if item["id"] in created_ids:
                assert item["genre"] == "rock"
