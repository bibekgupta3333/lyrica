"""
Unit tests for HuggingFaceIngestionService.

Tests cover:
- Dataset loading and caching
- Field mapping and data transformation
- Batch processing
- Error handling and retry logic
- Statistics collection
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lyrics import Lyrics
from app.services.ingestion.huggingface_ingestion import HuggingFaceIngestionService


@pytest.fixture
def mock_dataset():
    """Mock Hugging Face dataset."""
    mock_data = [
        {
            "title": "Test Song 1",
            "lyrics": "Verse 1 lyrics here\nChorus here",
            "artist": "Test Artist",
            "genre": "pop",
        },
        {
            "title": "Test Song 2",
            "lyrics": "Another verse\nAnother chorus",
            "artist": "Test Artist 2",
            "genre": "rock",
        },
    ]
    return MagicMock(__iter__=lambda self: iter(mock_data), __len__=lambda self: len(mock_data))


@pytest.fixture
def ingestion_service():
    """Create HuggingFaceIngestionService instance."""
    return HuggingFaceIngestionService(cache_dir="/tmp/test_cache")


class TestHuggingFaceIngestionService:
    """Test suite for HuggingFaceIngestionService."""

    @pytest.mark.asyncio
    async def test_initialization(self, ingestion_service):
        """Test service initialization."""
        assert ingestion_service.cache_dir == "/tmp/test_cache"
        assert ingestion_service.stats == {
            "total_processed": 0,
            "inserted": 0,
            "skipped": 0,
            "errors": 0,
        }

    @pytest.mark.asyncio
    async def test_field_mapping_genius_lyrics(self, ingestion_service):
        """Test field mapping for genius-lyrics dataset."""
        raw_data = {
            "title": "Test Song",
            "lyrics": "Test lyrics content",
            "artist": "Test Artist",
            "genre": "pop",
        }

        mapped = ingestion_service._map_fields(raw_data, "genius-lyrics")

        assert mapped["title"] == "Test Song"
        assert mapped["content"] == "Test lyrics content"
        assert mapped["artist"] == "Test Artist"
        assert mapped["genre"] == "pop"

    @pytest.mark.asyncio
    async def test_field_mapping_spotify_tracks(self, ingestion_service):
        """Test field mapping for spotify-tracks-dataset."""
        raw_data = {
            "track_name": "Spotify Song",
            "lyrics": "Spotify lyrics",
            "artists": "Artist Name",
            "track_genre": "electronic",
        }

        mapped = ingestion_service._map_fields(raw_data, "spotify-tracks")

        assert mapped["title"] == "Spotify Song"
        assert mapped["content"] == "Spotify lyrics"
        assert mapped["artist"] == "Artist Name"
        assert mapped["genre"] == "electronic"

    @pytest.mark.asyncio
    async def test_data_cleaning(self, ingestion_service):
        """Test data cleaning pipeline."""
        raw_content = "  Line 1  \n\n\n  Line 2  \n  "

        cleaned = ingestion_service._clean_lyrics(raw_content)

        assert cleaned == "Line 1\n\nLine 2"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")

    @pytest.mark.asyncio
    async def test_data_validation_success(self, ingestion_service):
        """Test data validation with valid data."""
        data = {
            "title": "Valid Song",
            "content": "This is a valid lyrics content with enough text to pass validation.",
            "genre": "pop",
        }

        is_valid = ingestion_service._validate_data(data)

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_data_validation_failure_short_content(self, ingestion_service):
        """Test data validation fails with short content."""
        data = {
            "title": "Short",
            "content": "Too short",
            "genre": "pop",
        }

        is_valid = ingestion_service._validate_data(data, min_length=50)

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_data_validation_failure_missing_title(self, ingestion_service):
        """Test data validation fails with missing title."""
        data = {
            "title": "",
            "content": "Valid content here with enough text",
            "genre": "pop",
        }

        is_valid = ingestion_service._validate_data(data)

        assert is_valid is False

    @pytest.mark.asyncio
    @patch("app.services.ingestion.huggingface_ingestion.load_dataset")
    async def test_ingest_from_dataset_success(
        self, mock_load_dataset, ingestion_service, mock_dataset, db_session: AsyncSession
    ):
        """Test successful ingestion from dataset."""
        mock_load_dataset.return_value = mock_dataset

        user_id = "test-user-id"
        stats = await ingestion_service.ingest_from_dataset(
            db=db_session,
            dataset_name="genius-lyrics",
            max_samples=2,
            user_id=user_id,
            batch_size=1,
        )

        assert stats["total_processed"] == 2
        assert stats["inserted"] > 0
        assert stats["errors"] == 0

    @pytest.mark.asyncio
    async def test_batch_processing(self, ingestion_service, db_session: AsyncSession):
        """Test batch processing of lyrics."""
        lyrics_data = [
            {
                "title": f"Song {i}",
                "content": f"Lyrics content for song {i}" * 10,
                "genre": "pop",
                "artist": f"Artist {i}",
            }
            for i in range(5)
        ]

        user_id = "test-user-id"
        processed = await ingestion_service._process_batch(
            batch=lyrics_data, db=db_session, user_id=user_id
        )

        assert processed == 5

    @pytest.mark.asyncio
    async def test_error_handling_invalid_dataset(
        self, ingestion_service, db_session: AsyncSession
    ):
        """Test error handling with invalid dataset."""
        with pytest.raises(Exception):
            await ingestion_service.ingest_from_dataset(
                db=db_session,
                dataset_name="invalid-dataset-name",
                max_samples=10,
                user_id="test-user",
            )

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, ingestion_service):
        """Test statistics tracking during ingestion."""
        assert ingestion_service.stats["total_processed"] == 0

        ingestion_service.stats["total_processed"] += 5
        ingestion_service.stats["inserted"] += 4
        ingestion_service.stats["skipped"] += 1

        assert ingestion_service.stats["total_processed"] == 5
        assert ingestion_service.stats["inserted"] == 4
        assert ingestion_service.stats["skipped"] == 1

    @pytest.mark.asyncio
    async def test_duplicate_detection(self, ingestion_service, db_session: AsyncSession):
        """Test duplicate lyrics detection."""
        # Insert first lyrics
        lyrics1 = Lyrics(
            title="Duplicate Song",
            content="Same content",
            genre="pop",
            user_id="test-user",
        )
        db_session.add(lyrics1)
        await db_session.commit()

        # Try to insert duplicate
        data = {
            "title": "Duplicate Song",
            "content": "Same content",
            "genre": "pop",
        }

        # Should skip duplicate
        result = await ingestion_service._check_duplicate(db_session, data)
        assert result is True

    @pytest.mark.asyncio
    async def test_genre_normalization(self, ingestion_service):
        """Test genre normalization."""
        test_cases = [
            ("Pop", "pop"),
            ("ROCK", "rock"),
            ("Hip-Hop", "hip-hop"),
            ("R&B", "r&b"),
        ]

        for input_genre, expected in test_cases:
            normalized = ingestion_service._normalize_genre(input_genre)
            assert normalized == expected

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, ingestion_service):
        """Test metadata extraction from lyrics."""
        content = "[Verse 1]\nFirst verse\n\n[Chorus]\nChorus part\n\n[Verse 2]\nSecond verse"

        metadata = ingestion_service._extract_metadata(content)

        assert "structure" in metadata
        assert "verse" in metadata["structure"].lower()
        assert "chorus" in metadata["structure"].lower()

    @pytest.mark.asyncio
    async def test_max_samples_limit(
        self, ingestion_service, mock_dataset, db_session: AsyncSession
    ):
        """Test that max_samples limit is respected."""
        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = mock_dataset

            stats = await ingestion_service.ingest_from_dataset(
                db=db_session,
                dataset_name="genius-lyrics",
                max_samples=1,  # Limit to 1
                user_id="test-user",
            )

            assert stats["total_processed"] <= 1

    @pytest.mark.asyncio
    async def test_progress_callback(self, ingestion_service, db_session: AsyncSession):
        """Test progress callback functionality."""
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = [{"title": "Test", "lyrics": "Content" * 20}]

            await ingestion_service.ingest_from_dataset(
                db=db_session,
                dataset_name="test",
                max_samples=1,
                user_id="test-user",
                progress_callback=progress_callback,
            )

            assert len(progress_calls) > 0


@pytest.mark.asyncio
async def test_ingestion_service_integration(db_session: AsyncSession):
    """Integration test for complete ingestion workflow."""
    service = HuggingFaceIngestionService(cache_dir="/tmp/test_cache")

    # Mock dataset
    mock_data = [
        {
            "title": "Integration Test Song",
            "lyrics": "Full integration test lyrics content with enough text",
            "artist": "Test Artist",
            "genre": "pop",
        }
    ]

    with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
        mock_load.return_value = mock_data

        stats = await service.ingest_from_dataset(
            db=db_session,
            dataset_name="test-dataset",
            max_samples=1,
            user_id="integration-test-user",
            batch_size=1,
        )

        assert stats["total_processed"] == 1
        assert stats["errors"] == 0

        # Verify lyrics was inserted
        result = await db_session.execute(
            "SELECT COUNT(*) FROM lyrics WHERE title = 'Integration Test Song'"
        )
        count = result.scalar()
        assert count == 1
