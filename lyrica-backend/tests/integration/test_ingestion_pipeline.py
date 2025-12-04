"""
Integration tests for data ingestion pipeline.

Tests the complete end-to-end workflow including:
- Dataset loading
- Data processing
- Database seeding
- Vector store population
- Error recovery
"""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.lyrics import Lyrics
from app.models.user import User
from app.models.voice_profile import VoiceProfile
from app.services.ingestion.chromadb_population import ChromaDBPopulationService
from app.services.ingestion.huggingface_ingestion import HuggingFaceIngestionService


@pytest.fixture
async def setup_test_user(db_session: AsyncSession):
    """Create a test user for ingestion."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpass"),
        role="admin",
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def mock_hf_dataset():
    """Mock Hugging Face dataset with realistic data."""
    return [
        {
            "title": f"Test Song {i}",
            "lyrics": f"[Verse 1]\nTest verse {i}\n\n[Chorus]\nTest chorus {i}\n\n[Verse 2]\nAnother verse {i}",
            "artist": f"Artist {i}",
            "genre": ["pop", "rock", "hip-hop"][i % 3],
        }
        for i in range(10)
    ]


class TestEndToEndIngestion:
    """Integration tests for complete ingestion pipeline."""

    @pytest.mark.asyncio
    async def test_complete_ingestion_workflow(
        self, db_session: AsyncSession, setup_test_user, mock_hf_dataset
    ):
        """Test complete workflow from dataset to vector store."""
        user = setup_test_user

        # Step 1: Ingest lyrics from HuggingFace
        ingestion_service = HuggingFaceIngestionService(cache_dir="/tmp/test_cache")

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = mock_hf_dataset

            ingestion_stats = await ingestion_service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=10,
                user_id=str(user.id),
                batch_size=5,
            )

            assert ingestion_stats["total_processed"] == 10
            assert ingestion_stats["inserted"] > 0
            assert ingestion_stats["errors"] == 0

        # Step 2: Verify lyrics in database
        result = await db_session.execute(select(Lyrics))
        lyrics_list = result.scalars().all()
        assert len(lyrics_list) >= 10

        # Step 3: Populate vector store
        population_service = ChromaDBPopulationService()

        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = MagicMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            population_stats = await population_service.populate_from_database(
                db=db_session, batch_size=32, chunk_size=512
            )

            assert population_stats["documents_indexed"] > 0
            assert population_stats["errors"] == 0

        # Step 4: Verify end-to-end success
        assert ingestion_stats["inserted"] > 0
        assert population_stats["documents_indexed"] > 0

    @pytest.mark.asyncio
    async def test_ingestion_with_different_datasets(
        self, db_session: AsyncSession, setup_test_user
    ):
        """Test ingestion with different dataset formats."""
        user = setup_test_user
        datasets = {
            "genius-lyrics": [
                {"title": "Song 1", "lyrics": "Content 1" * 20, "artist": "Artist 1"}
            ],
            "spotify-tracks": [
                {
                    "track_name": "Song 2",
                    "lyrics": "Content 2" * 20,
                    "artists": "Artist 2",
                    "track_genre": "pop",
                }
            ],
        }

        service = HuggingFaceIngestionService()

        for dataset_name, mock_data in datasets.items():
            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
                mock_load.return_value = mock_data

                stats = await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name=dataset_name,
                    max_samples=1,
                    user_id=str(user.id),
                )

                assert stats["total_processed"] > 0
                assert stats["errors"] == 0

    @pytest.mark.asyncio
    async def test_error_recovery_and_rollback(
        self, db_session: AsyncSession, setup_test_user, mock_hf_dataset
    ):
        """Test error recovery and transaction rollback."""
        user = setup_test_user

        # Modify one item to cause validation error
        bad_dataset = mock_hf_dataset.copy()
        bad_dataset[5] = {
            "title": "",  # Invalid empty title
            "lyrics": "x",  # Too short
            "artist": "Bad",
        }

        service = HuggingFaceIngestionService()

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = bad_dataset

            stats = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=10,
                user_id=str(user.id),
                batch_size=2,
            )

            # Should skip invalid items but continue
            assert stats["total_processed"] == 10
            assert stats["skipped"] > 0
            assert stats["inserted"] < 10

    @pytest.mark.asyncio
    async def test_concurrent_ingestion(self, db_session: AsyncSession, setup_test_user):
        """Test concurrent ingestion operations."""
        user = setup_test_user

        async def ingest_batch(batch_id: int):
            service = HuggingFaceIngestionService()
            mock_data = [
                {
                    "title": f"Batch {batch_id} Song {i}",
                    "lyrics": f"Content for batch {batch_id} song {i}" * 10,
                    "artist": f"Artist {batch_id}",
                }
                for i in range(5)
            ]

            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
                mock_load.return_value = mock_data

                return await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name=f"test-batch-{batch_id}",
                    max_samples=5,
                    user_id=str(user.id),
                )

        # Run 3 concurrent ingestion tasks
        results = await asyncio.gather(
            ingest_batch(1),
            ingest_batch(2),
            ingest_batch(3),
            return_exceptions=True,
        )

        # Verify all succeeded
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert all(r["errors"] == 0 for r in results)

    @pytest.mark.asyncio
    async def test_environment_specific_behavior(
        self, db_session: AsyncSession, setup_test_user, mock_hf_dataset
    ):
        """Test different behavior for different environments."""
        user = setup_test_user
        service = HuggingFaceIngestionService()

        environments = {
            "development": {"max_samples": 100, "batch_size": 10},
            "staging": {"max_samples": 1000, "batch_size": 50},
            "production": {"max_samples": 50000, "batch_size": 100},
        }

        for env, config in environments.items():
            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
                mock_load.return_value = mock_hf_dataset[: config["max_samples"]]

                stats = await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name="test-dataset",
                    max_samples=config["max_samples"],
                    user_id=str(user.id),
                    batch_size=config["batch_size"],
                )

                assert stats["total_processed"] <= config["max_samples"]

    @pytest.mark.asyncio
    async def test_voice_profile_seeding(self, db_session: AsyncSession):
        """Test voice profile seeding as part of complete setup."""
        from app.core.voice_config import VOICE_PROFILES

        # Seed voice profiles
        for profile_def in VOICE_PROFILES[:5]:  # Seed first 5
            voice_profile = VoiceProfile(
                name=profile_def.name,
                description=profile_def.description,
                voice_model=profile_def.engine.value,
                gender=profile_def.gender.value,
                language=profile_def.language,
                is_available=True,
            )
            db_session.add(voice_profile)

        await db_session.commit()

        # Verify
        result = await db_session.execute(select(VoiceProfile))
        profiles = result.scalars().all()
        assert len(profiles) >= 5

    @pytest.mark.asyncio
    async def test_incremental_ingestion(
        self, db_session: AsyncSession, setup_test_user, mock_hf_dataset
    ):
        """Test incremental ingestion (adding new data to existing)."""
        user = setup_test_user
        service = HuggingFaceIngestionService()

        # First batch
        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = mock_hf_dataset[:5]

            stats1 = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=5,
                user_id=str(user.id),
            )

        # Second batch (new data)
        new_data = [
            {
                "title": f"New Song {i}",
                "lyrics": f"New content {i}" * 20,
                "artist": f"New Artist {i}",
            }
            for i in range(5)
        ]

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = new_data

            stats2 = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=5,
                user_id=str(user.id),
            )

        # Verify both batches were ingested
        result = await db_session.execute(select(Lyrics))
        all_lyrics = result.scalars().all()
        assert len(all_lyrics) >= 10

    @pytest.mark.asyncio
    async def test_data_quality_validation(self, db_session: AsyncSession, setup_test_user):
        """Test that data quality validation works end-to-end."""
        user = setup_test_user
        service = HuggingFaceIngestionService()

        # Mix of good and bad data
        mixed_data = [
            {
                "title": "Good Song 1",
                "lyrics": "Valid lyrics content here" * 20,
                "artist": "Valid Artist",
            },
            {"title": "", "lyrics": "x", "artist": ""},  # Invalid
            {
                "title": "Good Song 2",
                "lyrics": "More valid content" * 20,
                "artist": "Another Artist",
            },
        ]

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = mixed_data

            stats = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=3,
                user_id=str(user.id),
                min_length=50,
            )

            # Should insert only valid items
            assert stats["inserted"] == 2
            assert stats["skipped"] == 1

    @pytest.mark.asyncio
    async def test_full_pipeline_with_search(
        self, db_session: AsyncSession, setup_test_user, mock_hf_dataset
    ):
        """Test full pipeline including search verification."""
        user = setup_test_user

        # 1. Ingest lyrics
        ingestion_service = HuggingFaceIngestionService()
        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
            mock_load.return_value = mock_hf_dataset

            await ingestion_service.ingest_from_dataset(
                db=db_session,
                dataset_name="test-dataset",
                max_samples=10,
                user_id=str(user.id),
            )

        # 2. Populate vector store
        population_service = ChromaDBPopulationService()
        with patch.object(population_service, "vector_store") as mock_store:
            mock_store.add_documents = MagicMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            await population_service.populate_from_database(db=db_session)

            # 3. Test search
            mock_search_results = [
                {"content": "Test verse", "metadata": {"title": "Test Song 1"}},
                {"content": "Test chorus", "metadata": {"title": "Test Song 2"}},
            ]
            mock_store.search = MagicMock(return_value=mock_search_results)

            results = await population_service.test_rag_search(query="test song", n_results=2)

            assert len(results) == 2
            assert results[0]["metadata"]["title"] == "Test Song 1"


@pytest.mark.asyncio
async def test_complete_system_readiness(db_session: AsyncSession, setup_test_user):
    """Integration test for complete system readiness check."""
    user = setup_test_user

    # 1. Verify user exists
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) >= 1

    # 2. Seed voice profiles
    from app.core.voice_config import VOICE_PROFILES

    for profile_def in VOICE_PROFILES[:4]:
        voice_profile = VoiceProfile(
            name=profile_def.name,
            description=profile_def.description,
            voice_model=profile_def.engine.value,
            gender=profile_def.gender.value,
            language=profile_def.language,
            is_available=True,
        )
        db_session.add(voice_profile)
    await db_session.commit()

    # 3. Ingest lyrics
    service = HuggingFaceIngestionService()
    mock_data = [
        {
            "title": f"Readiness Test {i}",
            "lyrics": f"Content for readiness test {i}" * 20,
            "artist": "Test Artist",
        }
        for i in range(100)
    ]

    with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock_load:
        mock_load.return_value = mock_data

        await service.ingest_from_dataset(
            db=db_session,
            dataset_name="test",
            max_samples=100,
            user_id=str(user.id),
        )

    # 4. Verify system readiness
    result = await db_session.execute(select(User))
    user_count = len(result.scalars().all())

    result = await db_session.execute(select(VoiceProfile))
    voice_count = len(result.scalars().all())

    result = await db_session.execute(select(Lyrics))
    lyrics_count = len(result.scalars().all())

    # System should be ready
    assert user_count >= 1
    assert voice_count >= 4
    assert lyrics_count >= 100
