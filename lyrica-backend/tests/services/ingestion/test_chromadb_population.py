"""
Unit tests for ChromaDB Population Service.

Tests cover:
- Embedding generation
- Document chunking
- ChromaDB indexing
- Search quality verification
- Collection management
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lyrics import Lyrics
from app.services.ingestion.chromadb_population import ChromaDBPopulationService


@pytest.fixture
def population_service():
    """Create ChromaDBPopulationService instance."""
    return ChromaDBPopulationService()


@pytest.fixture
def sample_lyrics():
    """Create sample lyrics for testing."""
    return [
        Lyrics(
            id=1,
            title="Test Song 1",
            content="This is verse one\n\nThis is the chorus\n\nThis is verse two",
            genre="pop",
            user_id="test-user-1",
        ),
        Lyrics(
            id=2,
            title="Test Song 2",
            content="Different lyrics here\n\nAnother chorus\n\nMore verses",
            genre="rock",
            user_id="test-user-1",
        ),
    ]


class TestChromaDBPopulationService:
    """Test suite for ChromaDB Population Service."""

    @pytest.mark.asyncio
    async def test_initialization(self, population_service):
        """Test service initialization."""
        assert population_service is not None
        assert hasattr(population_service, "vector_store")
        assert hasattr(population_service, "stats")

    @pytest.mark.asyncio
    async def test_text_chunking_basic(self, population_service):
        """Test basic text chunking functionality."""
        text = "Line 1\n\nLine 2\n\nLine 3\n\nLine 4"
        chunk_size = 20
        overlap = 5

        chunks = population_service._chunk_text(text, chunk_size=chunk_size, overlap=overlap)

        assert len(chunks) > 0
        assert all(len(chunk) <= chunk_size + overlap for chunk in chunks)

    @pytest.mark.asyncio
    async def test_text_chunking_respects_structure(self, population_service):
        """Test that chunking respects song structure."""
        text = (
            "[Verse 1]\nFirst verse content\n\n[Chorus]\nChorus content\n\n[Verse 2]\nSecond verse"
        )

        chunks = population_service._chunk_text(text, chunk_size=50, respect_structure=True)

        # Should split on structural markers
        assert len(chunks) > 1
        assert any("[Verse" in chunk for chunk in chunks)
        assert any("[Chorus]" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, population_service, sample_lyrics):
        """Test metadata extraction from lyrics."""
        lyrics = sample_lyrics[0]

        metadata = population_service._extract_metadata(lyrics)

        assert "lyrics_id" in metadata
        assert "title" in metadata
        assert "genre" in metadata
        assert metadata["title"] == "Test Song 1"
        assert metadata["genre"] == "pop"

    @pytest.mark.asyncio
    async def test_embedding_generation(self, population_service):
        """Test embedding generation for text."""
        text = "This is a test lyrics content for embedding generation"

        embedding = await population_service._generate_embedding(text)

        assert embedding is not None
        assert len(embedding) > 0
        assert isinstance(embedding, list)
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_batch_embedding_generation(self, population_service):
        """Test batch embedding generation."""
        texts = [
            "First test lyrics",
            "Second test lyrics",
            "Third test lyrics",
        ]

        embeddings = await population_service._generate_embeddings_batch(texts, batch_size=2)

        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_populate_from_database(
        self, population_service, sample_lyrics, db_session: AsyncSession
    ):
        """Test population from database."""
        # Add sample lyrics to database
        for lyrics in sample_lyrics:
            db_session.add(lyrics)
        await db_session.commit()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = AsyncMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            stats = await population_service.populate_from_database(
                db=db_session, batch_size=1, chunk_size=100
            )

            assert stats["documents_indexed"] > 0
            assert stats["errors"] == 0

    @pytest.mark.asyncio
    async def test_duplicate_prevention(self, population_service, db_session: AsyncSession):
        """Test that duplicate documents are not added."""
        lyrics = Lyrics(
            id=1,
            title="Duplicate Test",
            content="Content to test duplicates",
            genre="pop",
            user_id="test",
        )

        db_session.add(lyrics)
        await db_session.commit()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.get_by_id = MagicMock(return_value={"id": "lyrics_1_chunk_0"})

            # First population
            stats1 = await population_service.populate_from_database(db=db_session)

            # Second population (should skip duplicates)
            stats2 = await population_service.populate_from_database(db=db_session)

            assert stats2["documents_indexed"] == 0  # Should skip

    @pytest.mark.asyncio
    async def test_collection_reset(self, population_service):
        """Test collection reset functionality."""
        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.reset_collection = AsyncMock(return_value=True)

            await population_service.reset_collection()

            mock_store.reset_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_quality_verification(self, population_service):
        """Test RAG search quality verification."""
        with patch.object(population_service, "vector_store") as mock_store:
            mock_results = [
                {"content": "Test lyrics 1", "metadata": {"title": "Song 1"}},
                {"content": "Test lyrics 2", "metadata": {"title": "Song 2"}},
            ]
            mock_store.search = MagicMock(return_value=mock_results)

            results = await population_service.test_rag_search(query="love song", n_results=2)

            assert len(results) == 2
            mock_store.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_progress_tracking(self, population_service, db_session: AsyncSession):
        """Test progress tracking during population."""
        progress_updates = []

        def progress_callback(current, total, message):
            progress_updates.append((current, total, message))

        lyrics = Lyrics(
            id=1,
            title="Progress Test",
            content="Content for progress testing",
            genre="pop",
            user_id="test",
        )
        db_session.add(lyrics)
        await db_session.commit()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = AsyncMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            await population_service.populate_from_database(
                db=db_session, progress_callback=progress_callback
            )

            assert len(progress_updates) > 0

    @pytest.mark.asyncio
    async def test_error_handling_embedding_failure(self, population_service):
        """Test error handling when embedding generation fails."""
        with patch.object(population_service, "_generate_embedding") as mock_embed:
            mock_embed.side_effect = Exception("Embedding failed")

            result = await population_service._generate_embedding_safe("test text")

            assert result is None  # Should return None on failure

    @pytest.mark.asyncio
    async def test_batch_size_optimization(self, population_service, db_session: AsyncSession):
        """Test that batch size is properly utilized."""
        # Create multiple lyrics
        for i in range(10):
            lyrics = Lyrics(
                id=i + 1,
                title=f"Song {i}",
                content=f"Lyrics content {i}" * 10,
                genre="pop",
                user_id="test",
            )
            db_session.add(lyrics)
        await db_session.commit()

        batch_sizes = []

        async def mock_add_documents(docs):
            batch_sizes.append(len(docs))
            return True

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = mock_add_documents
            mock_store.count = MagicMock(return_value=0)

            await population_service.populate_from_database(db=db_session, batch_size=3)

            # Verify batching occurred
            assert len(batch_sizes) > 0
            assert all(size <= 3 for size in batch_sizes)

    @pytest.mark.asyncio
    async def test_genre_filtering(self, population_service):
        """Test filtering by genre in search."""
        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.search = MagicMock(return_value=[])

            await population_service.search_by_genre(query="love", genre="pop", n_results=5)

            # Verify filter was passed
            call_args = mock_store.search.call_args
            assert "filter" in call_args.kwargs
            assert call_args.kwargs["filter"]["genre"] == "pop"

    @pytest.mark.asyncio
    async def test_statistics_collection(self, population_service, db_session: AsyncSession):
        """Test statistics collection during population."""
        lyrics = Lyrics(
            id=1,
            title="Stats Test",
            content="Content for statistics testing",
            genre="pop",
            user_id="test",
        )
        db_session.add(lyrics)
        await db_session.commit()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = AsyncMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            stats = await population_service.populate_from_database(db=db_session)

            assert "documents_indexed" in stats
            assert "chunks_created" in stats
            assert "errors" in stats
            assert "duration" in stats

    @pytest.mark.asyncio
    async def test_incremental_update(self, population_service, db_session: AsyncSession):
        """Test incremental updates to vector store."""
        # Initial population
        lyrics1 = Lyrics(
            id=1, title="Initial", content="Initial content", genre="pop", user_id="test"
        )
        db_session.add(lyrics1)
        await db_session.commit()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = AsyncMock(return_value=True)
            mock_store.count = MagicMock(return_value=1)
            mock_store.get_by_id = MagicMock(return_value=None)

            stats1 = await population_service.populate_from_database(db=db_session)
            assert stats1["documents_indexed"] > 0

            # Add new lyrics
            lyrics2 = Lyrics(id=2, title="New", content="New content", genre="rock", user_id="test")
            db_session.add(lyrics2)
            await db_session.commit()

            # Incremental update
            stats2 = await population_service.populate_from_database(
                db=db_session, reset_collection=False
            )

            # Should only index new lyrics
            assert stats2["documents_indexed"] > 0


@pytest.mark.asyncio
async def test_chromadb_population_integration(db_session: AsyncSession):
    """Integration test for ChromaDB population workflow."""
    service = ChromaDBPopulationService()

    # Create test lyrics
    lyrics = Lyrics(
        id=1,
        title="Integration Test Song",
        content="Full integration test with complete lyrics content for ChromaDB",
        genre="pop",
        user_id="integration-test",
    )
    db_session.add(lyrics)
    await db_session.commit()

    with patch.object(service, "vector_store") as mock_store:
        mock_store.add_documents = AsyncMock(return_value=True)
        mock_store.count = MagicMock(return_value=0)

        stats = await service.populate_from_database(db=db_session, batch_size=32, chunk_size=512)

        assert stats["documents_indexed"] > 0
        assert stats["errors"] == 0
        mock_store.add_documents.assert_called()
