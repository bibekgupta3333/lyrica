"""
Integration tests for RAG system endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.rag
@pytest.mark.asyncio
class TestRAGEndpoints:
    """Test RAG system endpoints."""

    async def test_get_rag_stats(self, client: AsyncClient):
        """Test getting RAG statistics."""
        response = await client.get("/api/v1/rag/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "collection_name" in data

    async def test_ingest_custom_text(self, client: AsyncClient):
        """Test ingesting custom text."""
        response = await client.post(
            "/api/v1/rag/ingest/custom",
            json={
                "text": "This is a test song about love and happiness",
                "metadata": {"source": "test", "genre": "pop"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "success"

    async def test_search_documents(self, client: AsyncClient):
        """Test searching documents."""
        # First ingest a document
        await client.post(
            "/api/v1/rag/ingest/custom",
            json={
                "text": "A beautiful song about sunsets and dreams",
                "metadata": {"source": "test"},
            },
        )

        # Search for it
        response = await client.post(
            "/api/v1/rag/search",
            json={"query": "sunset dreams", "n_results": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)

    async def test_query_rag(self, client: AsyncClient):
        """Test querying RAG system."""
        response = await client.post(
            "/api/v1/rag/query",
            json={"query": "love songs", "n_results": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data


@pytest.mark.integration
@pytest.mark.rag
@pytest.mark.asyncio
@pytest.mark.slow
class TestRAGGeneration:
    """Test RAG generation endpoints (slow tests)."""

    async def test_generate_with_rag(self, client: AsyncClient):
        """Test generating lyrics with RAG."""
        response = await client.post(
            "/api/v1/rag/generate/lyrics",
            json={
                "prompt": "A short song about sunshine",
                "genre": "pop",
                "use_rag": True,
                "max_length": 200,
            },
            timeout=30.0,
        )

        assert response.status_code == 200
        data = response.json()
        assert "lyrics" in data
        assert "context_used" in data
