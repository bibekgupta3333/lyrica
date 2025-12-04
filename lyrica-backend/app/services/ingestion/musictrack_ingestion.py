"""
Music Track Ingestion Service

Handles loading and processing music tracks from Hugging Face datasets.
"""

import os
import uuid
from typing import Any, Dict, List, Optional

from datasets import load_dataset
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.music_track import MusicTrack
from app.models.song import Song
from app.models.user import User


class MusicTrackIngestionService:
    """Service for ingesting music tracks from Hugging Face datasets."""

    # GTZAN dataset configuration
    GTZAN_CONFIG = {
        "full_name": "marsyas/gtzan",
        "fields": {
            "genre": "genre",
            "file": "file",  # Audio file path
        },
    }

    # Track type mapping from genre
    GENRE_TO_TRACK_TYPE = {
        "blues": "instrumental",
        "classical": "instrumental",
        "country": "instrumental",
        "disco": "instrumental",
        "hiphop": "instrumental",
        "jazz": "instrumental",
        "metal": "instrumental",
        "pop": "instrumental",
        "reggae": "instrumental",
        "rock": "instrumental",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the ingestion service.

        Args:
            cache_dir: Directory to cache datasets (defaults to ~/.cache/huggingface)
        """
        self.cache_dir = cache_dir or os.getenv(
            "HF_DATASETS_CACHE", os.path.expanduser("~/.cache/huggingface")
        )
        self.stats = {
            "loaded": 0,
            "processed": 0,
            "inserted": 0,
            "skipped": 0,
            "errors": 0,
        }

    async def ingest_from_gtzan(
        self,
        db: AsyncSession,
        max_samples: int = 100,
        user_id: Optional[uuid.UUID] = None,
        batch_size: int = 50,
    ) -> Dict[str, int]:
        """
        Ingest music tracks from GTZAN dataset or generate from genre templates.

        Args:
            db: Database session
            max_samples: Maximum number of tracks to ingest
            user_id: User ID to assign songs to (uses admin if None)
            batch_size: Number of samples to process in each batch

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info("Starting music track ingestion")
        logger.info(f"Target samples: {max_samples}, Batch size: {batch_size}")

        # Get or determine user
        if user_id is None:
            user_id = await self._get_admin_user_id(db)

        try:
            # Instead of loading audio datasets (which require torchcodec),
            # generate music track metadata from predefined genres
            logger.info("Generating music tracks from genre templates")
            logger.info("(Audio datasets require torchcodec - using metadata generation instead)")

            # Generate synthetic dataset from genres
            genres = [
                "pop",
                "rock",
                "jazz",
                "classical",
                "hip-hop",
                "electronic",
                "country",
                "blues",
                "reggae",
                "metal",
            ]

            # Create synthetic samples
            synthetic_samples = []
            samples_per_genre = max_samples // len(genres) + 1

            for genre in genres:
                for i in range(samples_per_genre):
                    if len(synthetic_samples) >= max_samples:
                        break
                    synthetic_samples.append({"genre": genre, "index": i + 1})
                if len(synthetic_samples) >= max_samples:
                    break

            self.stats["loaded"] = len(synthetic_samples)
            logger.success(f"Generated {len(synthetic_samples)} music track templates")

            # Process in batches
            for i in range(0, len(synthetic_samples), batch_size):
                batch = synthetic_samples[i : i + batch_size]
                await self._process_batch(db, batch, user_id)

                if (i + batch_size) % 100 == 0:
                    logger.info(
                        f"Processed {min(i + batch_size, len(synthetic_samples))}/{len(synthetic_samples)} samples"
                    )

            logger.success(f"✅ Music track ingestion complete!")
            logger.info(f"   Loaded: {self.stats['loaded']}")
            logger.info(f"   Processed: {self.stats['processed']}")
            logger.info(f"   Inserted: {self.stats['inserted']}")
            logger.info(f"   Skipped: {self.stats['skipped']}")
            logger.info(f"   Errors: {self.stats['errors']}")

        except Exception as e:
            logger.error(f"Error ingesting music tracks: {e}")
            logger.warning("⚠️  Skipping music track ingestion - continuing with other steps")
            self.stats["errors"] += 1
            # Don't raise - allow pipeline to continue

        return self.stats

    async def _process_batch(
        self, db: AsyncSession, batch: List[Dict[str, Any]], user_id: uuid.UUID
    ):
        """Process a batch of music track samples."""
        for sample in batch:
            try:
                # Extract genre (handle different dataset formats)
                genre = None
                if isinstance(sample, dict):
                    # Try various possible field names
                    genre = (
                        sample.get(self.GTZAN_CONFIG["fields"].get("genre", "genre"))
                        or sample.get("genre")
                        or sample.get("label")
                        or sample.get("category")
                        or sample.get("style")
                        or "unknown"
                    )
                else:
                    genre = "unknown"

                if not genre or genre == "unknown":
                    self.stats["skipped"] += 1
                    continue

                # Create new song for this track (no restrictions)
                song = await self._create_song(db, user_id, genre, self.stats["processed"] + 1)

                # Determine track type from genre
                track_type = self.GENRE_TO_TRACK_TYPE.get(genre.lower(), "instrumental")

                # Create music track
                music_track = MusicTrack(
                    song_id=song.id,
                    track_name=f"{genre.title()} Track",
                    track_type=track_type,
                    track_order=1,  # Will be updated if multiple tracks
                    volume=1.0,
                    pan=0.0,
                )

                db.add(music_track)
                self.stats["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing music track sample: {e}")
                self.stats["errors"] += 1
                continue

        # Commit batch
        try:
            await db.commit()
            self.stats["inserted"] += self.stats["processed"]
        except Exception as e:
            logger.error(f"Error committing music track batch: {e}")
            await db.rollback()
            self.stats["errors"] += 1

    async def _create_song(
        self, db: AsyncSession, user_id: uuid.UUID, genre: str, track_index: int
    ) -> Song:
        """Create a new song for the music track (no restrictions)."""
        # Always create new song (no duplicate checking)
        song = Song(
            user_id=user_id,
            title=f"{genre.title()} Song #{track_index}",
            genre=genre,
            music_style=genre,
            generation_status="completed",
        )
        db.add(song)
        await db.flush()
        return song

    async def _get_admin_user_id(self, db: AsyncSession) -> uuid.UUID:
        """Get admin user ID."""
        result = await db.execute(select(User).where(User.role == "admin").limit(1))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            raise ValueError("No admin user found. Run user setup first.")

        return admin_user.id
