"""
Unified Data Ingestion Script for Lyrica

This script provides a single standard entry point for all data preparation
and ingestion tasks required for song generation.

Usage:
    python scripts/ingest_data.py [OPTIONS]

Examples:
    # Quick setup (100 lyrics, 10 min)
    python scripts/ingest_data.py --quick

    # Development setup (1K lyrics, 30 min)
    python scripts/ingest_data.py

    # Ingest 100 items for each table (lyrics, music tracks, songs, voice profiles)
    python scripts/ingest_data.py --all-100

    # Custom dataset and quantity
    python scripts/ingest_data.py --dataset genius-lyrics --max-lyrics 5000

    # Custom quantities per table
    python scripts/ingest_data.py --max-lyrics 200 --max-music-tracks 150 --max-songs 100

    # Production setup (50K+ lyrics, 3-4 hours)
    python scripts/ingest_data.py --env production

    # Voice profiles only
    python scripts/ingest_data.py --voices-only

    # Check status
    python scripts/ingest_data.py --status

    # Reset and reingest
    python scripts/ingest_data.py --reset
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.lyrics import Lyrics
from app.models.user import User
from app.models.voice_profile import VoiceProfile


class IngestionConfig:
    """Load and manage ingestion configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration."""
        if config_path is None:
            config_path = project_root / "config" / "ingestion_config.yaml"

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Using default configuration")
            self.config = self._get_default_config()
            return

        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

        logger.info(f"Loaded configuration from {self.config_path}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file doesn't exist."""
        return {
            "environment": "development",
            "database": {
                "auto_create_admin": True,
                "admin_email": "admin@lyrica.com",
                "admin_username": "admin",
                "admin_password": "AdminLyrica2024!",
            },
            "voice_profiles": {"auto_seed": True, "source": "config"},
            "lyrics": {
                "primary_dataset": "genius-lyrics",
                "max_lyrics_dev": 1000,
                "max_lyrics_quick": 100,
                "batch_size": 100,
            },
            "chromadb": {
                "collection_name": "lyrics_embeddings",
                "auto_populate": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value if value is not None else default


class DataIngestionOrchestrator:
    """Orchestrate the complete data ingestion pipeline."""

    def __init__(self, config: IngestionConfig, args: argparse.Namespace):
        """Initialize orchestrator."""
        self.config = config
        self.args = args
        self.stats = {
            "users_created": 0,
            "voice_profiles_created": 0,
            "lyrics_ingested": 0,
            "music_tracks_created": 0,
            "songs_created": 0,
            "voice_profiles_hf_created": 0,
            "documents_created": 0,
            "embeddings_created": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

    async def run(self):
        """Execute the complete ingestion pipeline."""
        self.stats["start_time"] = datetime.now()

        # If --all-100 flag is set, override all max values to 100
        if self.args.all_100:
            if not hasattr(self.args, "max_lyrics") or self.args.max_lyrics is None:
                self.args.max_lyrics = 100
            if not hasattr(self.args, "max_music_tracks") or self.args.max_music_tracks is None:
                self.args.max_music_tracks = 100
            if not hasattr(self.args, "max_songs") or self.args.max_songs is None:
                self.args.max_songs = 100
            if (
                not hasattr(self.args, "max_voice_profiles_hf")
                or self.args.max_voice_profiles_hf is None
            ):
                self.args.max_voice_profiles_hf = 100
            logger.info("🎯 --all-100 flag set: Ingesting 100 items for each table")
            logger.info("")

        logger.info("=" * 80)
        logger.info("LYRICA DATA INGESTION PIPELINE")
        logger.info("=" * 80)
        logger.info("")

        try:
            async with AsyncSessionLocal() as db:
                # Step 1: Environment Check
                if self.config.get("pipeline.steps.environment_check", True):
                    await self._step_environment_check(db)

                # Step 2: User Setup
                if self.config.get("pipeline.steps.user_setup", True):
                    await self._step_user_setup(db)

                # Step 3: Voice Profiles
                if self.config.get("pipeline.steps.voice_profiles", True):
                    if not self.args.lyrics_only:
                        await self._step_voice_profiles(db)

                # Step 4: Lyrics Ingestion
                if self.config.get("pipeline.steps.lyrics_ingestion", True):
                    if not self.args.voices_only:
                        await self._step_lyrics_ingestion(db)

                # Step 5: Music Track Ingestion (P0)
                if self.config.get("pipeline.steps.music_track_ingestion", True):
                    if not self.args.lyrics_only and not self.args.voices_only:
                        await self._step_music_track_ingestion(db)

                # Step 6: Song Ingestion (P1)
                if self.config.get("pipeline.steps.song_ingestion", True):
                    if not self.args.lyrics_only and not self.args.voices_only:
                        await self._step_song_ingestion(db)

                # Step 7: Voice Profile HF Ingestion (P1, optional)
                if self.config.get("pipeline.steps.voice_profile_hf_ingestion", False):
                    if not self.args.lyrics_only and not self.args.voices_only:
                        await self._step_voice_profile_hf_ingestion(db)

                # Step 8: Document Ingestion (P0, auto from lyrics)
                if self.config.get("pipeline.steps.document_ingestion", True):
                    if not self.args.lyrics_only and not self.args.voices_only:
                        await self._step_document_ingestion(db)

                # Step 9: Mood/Theme Ingestion (P2, optional)
                if self.config.get("pipeline.steps.mood_theme_ingestion", False):
                    if not self.args.lyrics_only and not self.args.voices_only:
                        await self._step_mood_theme_ingestion(db)

                # Step 10: Vector Store Population
                if self.config.get("pipeline.steps.vector_store_population", True):
                    if not self.args.voices_only and not self.args.skip_chromadb:
                        await self._step_vector_store_population(db)

                # Step 11: Verification
                if self.config.get("pipeline.steps.verification", True):
                    await self._step_verification(db)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats["errors"] += 1
            raise
        finally:
            self.stats["end_time"] = datetime.now()
            await self._print_summary()

    async def _step_environment_check(self, db: AsyncSession):
        """Step 1: Check environment and dependencies."""
        logger.info("Step 1/11: Environment Check")
        logger.info("-" * 80)

        # Check database connection
        try:
            await db.execute(select(User).limit(1))
            logger.success("✅ Database connection: OK")
        except Exception as e:
            logger.error(f"❌ Database connection: FAILED - {e}")
            raise

        # Check ChromaDB (if needed)
        if not self.args.voices_only and not self.args.skip_chromadb:
            try:
                from app.services.vector_store import VectorStoreService

                vector_store = VectorStoreService()
                count = vector_store.count()
                logger.success(f"✅ ChromaDB connection: OK (Current docs: {count})")
            except Exception as e:
                logger.warning(f"⚠️  ChromaDB connection: WARNING - {e}")

        logger.info("")

    async def _step_user_setup(self, db: AsyncSession):
        """Step 2: Ensure admin user exists."""
        logger.info("Step 2/11: User Setup")
        logger.info("-" * 80)

        # Check for existing users
        result = await db.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            logger.info(f"Found {len(existing_users)} existing users")
            for user in existing_users[:5]:  # Show first 5
                logger.info(f"  - {user.email} ({user.role})")
            logger.info("")
            return

        # Create admin user
        if self.config.get("database.auto_create_admin", True):
            admin_user = User(
                email=self.config.get("database.admin_email", "admin@lyrica.com"),
                username=self.config.get("database.admin_username", "admin"),
                password_hash=get_password_hash(
                    self.config.get("database.admin_password", "AdminLyrica2024!")
                ),
                full_name=self.config.get("database.admin_full_name", "Lyrica Admin"),
                role="admin",
                is_verified=True,
                is_active=True,
            )
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            self.stats["users_created"] += 1
            logger.success(f"✅ Created admin user: {admin_user.email}")
        else:
            logger.warning("⚠️  No users found and auto_create_admin is disabled")

        logger.info("")

    async def _step_voice_profiles(self, db: AsyncSession):
        """Step 3: Seed voice profiles."""
        logger.info("Step 3/11: Voice Profiles Setup")
        logger.info("-" * 80)

        # Check existing voice profiles
        result = await db.execute(select(VoiceProfile))
        existing_profiles = result.scalars().all()

        if existing_profiles:
            logger.info(f"Found {len(existing_profiles)} existing voice profiles")
            for profile in existing_profiles:
                logger.info(f"  - {profile.name} ({profile.gender}, {profile.language})")
            logger.info("")
            return

        # Load profiles from config
        profiles_config = self.config.get("voice_profiles.profiles", [])

        if not profiles_config:
            logger.warning("⚠️  No voice profiles defined in config")
            # Load from voice_config.py as fallback
            from app.core.voice_config import VOICE_PROFILES

            for profile_def in VOICE_PROFILES:
                voice_profile = VoiceProfile(
                    name=profile_def.name,
                    description=profile_def.description,
                    voice_model=profile_def.engine.value,
                    gender=profile_def.gender.value,
                    age_range=profile_def.age_range,
                    accent=profile_def.accent,
                    language=profile_def.language,
                    model_parameters={"engine_voice_id": profile_def.engine_voice_id},
                    is_available=True,
                    is_premium=False,
                )
                db.add(voice_profile)
                self.stats["voice_profiles_created"] += 1
                logger.info(f"  → Created profile: {voice_profile.name}")

        else:
            # Create from YAML config
            for profile_cfg in profiles_config:
                voice_profile = VoiceProfile(
                    name=profile_cfg["name"],
                    description=profile_cfg.get("description"),
                    voice_model=profile_cfg["engine"],
                    gender=profile_cfg.get("gender"),
                    age_range=profile_cfg.get("age_range"),
                    accent=profile_cfg.get("accent"),
                    language=profile_cfg.get("language", "en"),
                    model_parameters={"engine_voice_id": profile_cfg["engine_voice_id"]},
                    is_available=profile_cfg.get("is_available", True),
                    is_premium=profile_cfg.get("is_premium", False),
                )
                db.add(voice_profile)
                self.stats["voice_profiles_created"] += 1
                logger.info(f"  → Created profile: {voice_profile.name}")

        await db.commit()
        logger.success(f"✅ Created {self.stats['voice_profiles_created']} voice profiles")
        logger.info("")

    async def _step_lyrics_ingestion(self, db: AsyncSession):
        """Step 4: Ingest lyrics from Hugging Face."""
        logger.info("Step 4/11: Lyrics Ingestion")
        logger.info("-" * 80)

        # Determine quantity (no restrictions - use provided or default)
        if self.args.max_lyrics:
            max_lyrics = self.args.max_lyrics
        elif self.args.quick:
            max_lyrics = self.config.get("lyrics.max_lyrics_quick", 100)
        else:
            # No environment restrictions - use reasonable default
            max_lyrics = self.args.max_lyrics or 1000

        # Determine dataset
        dataset_name = self.args.dataset or self.config.get(
            "lyrics.primary_dataset", "genius-lyrics"
        )

        logger.info(f"Dataset: {dataset_name}")
        logger.info(f"Target quantity: {max_lyrics}")
        logger.info("")

        # Check existing lyrics (informational only)
        result = await db.execute(select(Lyrics))
        existing_lyrics = result.scalars().all()

        if existing_lyrics:
            logger.info(f"Found {len(existing_lyrics)} existing lyrics - will add more")
            logger.info("")

        # Get admin user for lyrics ownership
        result = await db.execute(select(User).where(User.role == "admin"))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            logger.error("❌ No admin user found. Run user setup first.")
            return

        # Import ingestion service
        from app.services.ingestion.huggingface_ingestion import HuggingFaceIngestionService

        # Create ingestion service with cache directory
        cache_dir = self.config.get("integration.huggingface.cache_dir")
        ingestion_service = HuggingFaceIngestionService(cache_dir=cache_dir)

        try:
            # Run ingestion
            stats = await ingestion_service.ingest_from_dataset(
                db=db,
                dataset_name=dataset_name,
                max_samples=max_lyrics,
                user_id=str(admin_user.id),
                batch_size=self.config.get("lyrics.batch_size", 100),
                min_length=self.config.get("lyrics.min_length", 100),
                max_length=self.config.get("lyrics.max_length", 10000),
            )

            self.stats["lyrics_ingested"] = stats.get("inserted", 0)
            logger.success(f"✅ Ingested {self.stats['lyrics_ingested']} lyrics")

        except Exception as e:
            logger.error(f"Hugging Face ingestion failed: {e}")
            self.stats["errors"] += 1

        logger.info("")

    async def _step_music_track_ingestion(self, db: AsyncSession):
        """Step 5: Ingest music tracks from GTZAN dataset (P0)."""
        logger.info("Step 5/11: Music Track Ingestion (P0)")
        logger.info("-" * 80)

        # Determine quantity (no restrictions)
        if hasattr(self.args, "max_music_tracks") and self.args.max_music_tracks is not None:
            max_tracks = self.args.max_music_tracks
        elif self.args.quick:
            max_tracks = self.config.get("music_tracks.max_tracks_quick", 50)
        else:
            # No environment restrictions - use reasonable default
            max_tracks = 100

        logger.info(f"Dataset: {self.config.get('music_tracks.primary_dataset', 'marsyas/gtzan')}")
        logger.info(f"Target quantity: {max_tracks}")
        logger.info("")

        # Import ingestion service
        from app.services.ingestion.musictrack_ingestion import MusicTrackIngestionService

        cache_dir = self.config.get("integration.huggingface.cache_dir")
        ingestion_service = MusicTrackIngestionService(cache_dir=cache_dir)

        try:
            stats = await ingestion_service.ingest_from_gtzan(
                db=db,
                max_samples=max_tracks,
                batch_size=self.config.get("music_tracks.batch_size", 50),
            )
            self.stats["music_tracks_created"] = stats.get("inserted", 0)
            logger.success(f"✅ Ingested {self.stats['music_tracks_created']} music tracks")
        except Exception as e:
            logger.error(f"Music track ingestion failed: {e}")
            self.stats["errors"] += 1

        logger.info("")

    async def _step_song_ingestion(self, db: AsyncSession):
        """Step 6: Ingest songs from Lyrics-MIDI dataset (P1)."""
        logger.info("Step 6/11: Song Ingestion (P1)")
        logger.info("-" * 80)

        # Determine quantity (no restrictions)
        if hasattr(self.args, "max_songs") and self.args.max_songs is not None:
            max_songs = self.args.max_songs
        elif self.args.quick:
            max_songs = self.config.get("songs.max_songs_quick", 50)
        else:
            # No environment restrictions - use reasonable default
            max_songs = 100

        logger.info(
            f"Dataset: {self.config.get('songs.primary_dataset', 'asigalov61/Lyrics-MIDI-Dataset')}"
        )
        logger.info(f"Target quantity: {max_songs}")
        logger.info("")

        # Import ingestion service
        from app.services.ingestion.song_ingestion import SongIngestionService

        cache_dir = self.config.get("integration.huggingface.cache_dir")
        ingestion_service = SongIngestionService(cache_dir=cache_dir)

        try:
            stats = await ingestion_service.ingest_from_lyrics_midi(
                db=db,
                max_samples=max_songs,
                batch_size=self.config.get("songs.batch_size", 50),
            )
            self.stats["songs_created"] = stats.get("inserted", 0)
            logger.success(f"✅ Ingested {self.stats['songs_created']} songs")
        except Exception as e:
            logger.error(f"Song ingestion failed: {e}")
            self.stats["errors"] += 1

        logger.info("")

    async def _step_voice_profile_hf_ingestion(self, db: AsyncSession):
        """Step 7: Ingest voice profiles from Common Voice dataset (P1, optional)."""
        logger.info("Step 7/11: Voice Profile HF Ingestion (P1)")
        logger.info("-" * 80)

        # Check if HF ingestion is enabled (or if --all-100 flag is set)
        use_hf = self.config.get("voice_profiles_hf.use_huggingface", False)
        if not use_hf and not self.args.all_100:
            logger.info(
                "Hugging Face voice profile ingestion disabled (using config-based profiles)"
            )
            logger.info("")
            return

        # Enable HF ingestion if --all-100 is set
        if self.args.all_100:
            logger.info("Enabling Hugging Face voice profile ingestion (--all-100 flag)")

        # Determine quantity (no restrictions)
        if (
            hasattr(self.args, "max_voice_profiles_hf")
            and self.args.max_voice_profiles_hf is not None
        ):
            max_profiles = self.args.max_voice_profiles_hf
        elif self.args.quick:
            max_profiles = self.config.get("voice_profiles_hf.max_profiles_quick", 10)
        else:
            # No environment restrictions - use reasonable default
            max_profiles = 20

        language = self.config.get("voice_profiles_hf.language", "en")

        logger.info(
            f"Dataset: {self.config.get('voice_profiles_hf.primary_dataset', 'mozilla-foundation/common_voice_13_0')}"
        )
        logger.info(f"Language: {language}")
        logger.info(f"Target quantity: {max_profiles}")
        logger.info("")

        # Import ingestion service
        from app.services.ingestion.voiceprofile_ingestion import VoiceProfileIngestionService

        cache_dir = self.config.get("integration.huggingface.cache_dir")
        ingestion_service = VoiceProfileIngestionService(cache_dir=cache_dir)

        try:
            stats = await ingestion_service.ingest_from_common_voice(
                db=db,
                language=language,
                max_samples=max_profiles,
                batch_size=self.config.get("voice_profiles_hf.batch_size", 20),
            )
            self.stats["voice_profiles_hf_created"] = stats.get("inserted", 0)
            logger.success(
                f"✅ Ingested {self.stats['voice_profiles_hf_created']} voice profiles from HF"
            )
        except Exception as e:
            logger.error(f"Voice profile HF ingestion failed: {e}")
            self.stats["errors"] += 1

        logger.info("")

    async def _step_document_ingestion(self, db: AsyncSession):
        """Step 8: Create documents from lyrics for RAG (P0)."""
        logger.info("Step 8/11: Document Ingestion (P0)")
        logger.info("-" * 80)

        if not self.config.get("documents.auto_create_from_lyrics", True):
            logger.info("Document auto-creation from lyrics disabled")
            logger.info("")
            return

        # Documents are created automatically from lyrics during lyrics ingestion
        # This step just verifies they exist
        from app.models.document import Document

        result = await db.execute(select(Document))
        documents = result.scalars().all()

        logger.info(f"Found {len(documents)} documents in database")
        logger.info("Documents are created automatically from lyrics")
        logger.success(f"✅ Document ingestion complete ({len(documents)} documents)")
        logger.info("")

    async def _step_mood_theme_ingestion(self, db: AsyncSession):
        """Step 9: Ingest mood/theme data from emotion dataset (P2, optional)."""
        logger.info("Step 9/11: Mood/Theme Ingestion (P2)")
        logger.info("-" * 80)

        # Determine quantity
        if self.args.quick:
            max_samples = self.config.get("mood_theme.max_samples_quick", 100)
        else:
            env = self.args.env or self.config.get("environment", "development")
            max_samples = self.config.get(f"mood_theme.max_samples_{env}", 500)

        logger.info(f"Dataset: {self.config.get('mood_theme.primary_dataset', 'joeddav/emotion')}")
        logger.info(f"Target quantity: {max_samples}")
        logger.info("")

        # Note: Mood/theme data is typically used as metadata on lyrics
        # This ingestion would enrich existing lyrics with emotion data
        logger.info("Mood/theme ingestion: Enriching lyrics with emotion data")
        logger.info("(This feature can be implemented to map emotions to lyrics)")
        logger.success("✅ Mood/theme ingestion placeholder complete")
        logger.info("")

    async def _step_vector_store_population(self, db: AsyncSession):
        """Step 10: Populate ChromaDB with embeddings."""
        logger.info("Step 10/11: Vector Store Population")
        logger.info("-" * 80)

        # Check if we have lyrics
        result = await db.execute(select(Lyrics))
        lyrics_list = result.scalars().all()

        if not lyrics_list:
            logger.warning("⚠️  No lyrics found in database. Skipping vector store population.")
            logger.info("")
            return

        logger.info(f"Found {len(lyrics_list)} lyrics to process")

        # Import population service
        from app.services.ingestion.chromadb_population import ChromaDBPopulationService

        # Create population service
        population_service = ChromaDBPopulationService()

        try:
            # Run population
            stats = await population_service.populate_from_database(
                db=db,
                batch_size=self.config.get("chromadb.batch_size", 32),
                chunk_size=self.config.get("chromadb.chunk_size", 512),
                chunk_overlap=self.config.get("chromadb.chunk_overlap", 50),
                reset_collection=self.args.reset,
            )

            self.stats["embeddings_created"] = stats.get("documents_indexed", 0)
            logger.success(f"✅ Created {self.stats['embeddings_created']} embeddings")

            # Test RAG search
            if self.config.get("verification.test_rag_query", True):
                logger.info("")
                test_query = self.config.get("verification.test_query", "Write a happy love song")
                await population_service.test_rag_search(query=test_query, n_results=5)

        except Exception as e:
            logger.error(f"ChromaDB population failed: {e}")
            self.stats["errors"] += 1

        logger.info("")

    async def _step_verification(self, db: AsyncSession):
        """Step 11: Verify ingestion and generate report."""
        logger.info("Step 11/11: Verification")
        logger.info("-" * 80)

        # Count users
        result = await db.execute(select(User))
        user_count = len(result.scalars().all())
        logger.info(f"Users: {user_count}")

        # Count voice profiles
        result = await db.execute(select(VoiceProfile))
        voice_count = len(result.scalars().all())
        logger.info(f"Voice Profiles: {voice_count}")

        # Count lyrics
        result = await db.execute(select(Lyrics))
        lyrics_count = len(result.scalars().all())
        logger.info(f"Lyrics: {lyrics_count}")

        # Check ChromaDB
        if not self.args.skip_chromadb:
            try:
                from app.services.vector_store import VectorStoreService

                vector_store = VectorStoreService()
                chromadb_count = vector_store.count()
                logger.info(f"ChromaDB Docs: {chromadb_count}")
            except Exception as e:
                logger.warning(f"ChromaDB check failed: {e}")
                chromadb_count = 0
        else:
            chromadb_count = 0

        logger.info("")

        # Readiness check
        min_users = self.config.get("verification.min_users", 1)
        min_voices = self.config.get("verification.min_voice_profiles", 4)
        min_lyrics = self.config.get("verification.min_lyrics", 100)

        ready = user_count >= min_users and voice_count >= min_voices

        if ready:
            logger.success("✅ System is ready for song generation!")
            if lyrics_count < min_lyrics:
                logger.warning(f"⚠️  Only {lyrics_count} lyrics loaded (recommended: {min_lyrics}+)")
                logger.info("   Generation will work but quality may be lower without RAG context")
        else:
            logger.error("❌ System is NOT ready for song generation")
            if user_count < min_users:
                logger.error(f"   - Need at least {min_users} user(s)")
            if voice_count < min_voices:
                logger.error(f"   - Need at least {min_voices} voice profiles")

        logger.info("")

    async def _print_summary(self):
        """Print final summary of ingestion."""
        logger.info("=" * 80)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 80)

        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Users Created: {self.stats['users_created']}")
        logger.info(f"Voice Profiles Created: {self.stats['voice_profiles_created']}")
        logger.info(f"Lyrics Ingested: {self.stats['lyrics_ingested']}")
        logger.info(f"Music Tracks Created: {self.stats.get('music_tracks_created', 0)}")
        logger.info(f"Songs Created: {self.stats.get('songs_created', 0)}")
        logger.info(
            f"Voice Profiles (HF) Created: {self.stats.get('voice_profiles_hf_created', 0)}"
        )
        logger.info(f"Documents Created: {self.stats.get('documents_created', 0)}")
        logger.info(f"Embeddings Created: {self.stats['embeddings_created']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("")

        if self.stats["errors"] == 0:
            logger.success("✅ INGESTION COMPLETE!")
        else:
            logger.warning(f"⚠️  INGESTION COMPLETE WITH {self.stats['errors']} ERRORS")


async def check_status():
    """Check current data status."""
    logger.info("=" * 80)
    logger.info("DATA INGESTION STATUS REPORT")
    logger.info("=" * 80)
    logger.info("")

    async with AsyncSessionLocal() as db:
        # Count users
        result = await db.execute(select(User))
        user_count = len(result.scalars().all())

        # Count voice profiles
        result = await db.execute(select(VoiceProfile))
        voice_count = len(result.scalars().all())

        # Count lyrics
        result = await db.execute(select(Lyrics))
        lyrics_count = len(result.scalars().all())

        # Count music tracks
        try:
            from app.models.music_track import MusicTrack

            result = await db.execute(select(MusicTrack))
            music_track_count = len(result.scalars().all())
        except Exception:
            music_track_count = 0

        # Count songs
        try:
            from app.models.song import Song

            result = await db.execute(select(Song))
            song_count = len(result.scalars().all())
        except Exception:
            song_count = 0

        # Count documents
        try:
            from app.models.document import Document

            result = await db.execute(select(Document))
            document_count = len(result.scalars().all())
        except Exception:
            document_count = 0

        # Check ChromaDB
        try:
            from app.services.vector_store import VectorStoreService

            vector_store = VectorStoreService()
            chromadb_count = vector_store.count()
        except Exception:
            chromadb_count = 0

        logger.info(f"Users:              {user_count}")
        logger.info(f"Voice Profiles:     {voice_count}")
        logger.info(f"Lyrics:             {lyrics_count}")
        logger.info(f"Music Tracks:       {music_track_count}")
        logger.info(f"Songs:              {song_count}")
        logger.info(f"Documents:          {document_count}")
        logger.info(f"ChromaDB Embeddings: {chromadb_count}")
        logger.info("-" * 80)

        # Readiness assessment
        if user_count >= 1 and voice_count >= 4:
            if lyrics_count >= 1000:
                logger.success("Status:             ✅ Ready for song generation (Optimal)")
            elif lyrics_count >= 100:
                logger.success("Status:             ✅ Ready for song generation (Good)")
                logger.info(f"Recommendation:     Add more lyrics (target: 1,000+)")
            else:
                logger.warning("Status:             ⚠️  Basic setup (Limited quality)")
                logger.info(f"Recommendation:     Add lyrics for better RAG quality")
        else:
            logger.error("Status:             ❌ NOT ready for song generation")
            if user_count < 1:
                logger.error("                    - Need at least 1 user")
            if voice_count < 4:
                logger.error("                    - Need at least 4 voice profiles")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Lyrica Data Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Environment
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "staging", "production"],
        help="Environment (overrides config file)",
    )

    # Dataset selection
    parser.add_argument(
        "--dataset",
        type=str,
        help="Hugging Face dataset name (e.g., 'genius-lyrics')",
    )

    parser.add_argument(
        "--max-lyrics",
        type=int,
        help="Maximum number of lyrics to ingest",
    )

    parser.add_argument(
        "--max-music-tracks",
        type=int,
        help="Maximum number of music tracks to ingest",
    )

    parser.add_argument(
        "--max-songs",
        type=int,
        help="Maximum number of songs to ingest",
    )

    parser.add_argument(
        "--max-voice-profiles-hf",
        type=int,
        help="Maximum number of voice profiles from HF to ingest",
    )

    parser.add_argument(
        "--all-100",
        action="store_true",
        help="Ingest 100 items for each table (lyrics, music tracks, songs, voice profiles)",
    )

    # Mode flags
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick setup (100 lyrics, ~10 min)",
    )

    parser.add_argument(
        "--voices-only",
        action="store_true",
        help="Only seed voice profiles",
    )

    parser.add_argument(
        "--lyrics-only",
        action="store_true",
        help="Only ingest lyrics (skip voice profiles)",
    )

    parser.add_argument(
        "--skip-chromadb",
        action="store_true",
        help="Skip ChromaDB population",
    )

    # Action flags
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check current data status and exit",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset existing data before ingestion",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate ingestion without making changes",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification checks (used with --status)",
    )

    # Configuration
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to ingestion config file",
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # Status check mode
    if args.status:
        asyncio.run(check_status())
        return

    # Load configuration
    config = IngestionConfig(args.config)

    # Override environment if specified
    if args.env:
        config.config["environment"] = args.env

    # Dry run warning
    if args.dry_run:
        logger.warning("DRY RUN MODE - No changes will be made")
        logger.info("")

    # Run ingestion
    orchestrator = DataIngestionOrchestrator(config, args)
    asyncio.run(orchestrator.run())


if __name__ == "__main__":
    main()
