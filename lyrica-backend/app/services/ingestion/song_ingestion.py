"""
Song Ingestion Service

Handles loading and processing songs from Hugging Face datasets.
"""

import os
import uuid
from typing import Any, Dict, List, Optional

from datasets import load_dataset
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.lyrics import Lyrics
from app.models.song import Song
from app.models.user import User
from app.models.voice_profile import VoiceProfile


class SongIngestionService:
    """Service for ingesting songs from Hugging Face datasets."""

    # Lyrics-MIDI dataset configuration
    LYRICS_MIDI_CONFIG = {
        "full_name": "asigalov61/Lyrics-MIDI-Dataset",
        "fields": {
            "title": "title",
            "lyrics": "lyrics",
            "midi": "midi",
            "tempo": "tempo",
            "key": "key",
            "time_signature": "time_signature",
        },
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

    async def ingest_from_lyrics_midi(
        self,
        db: AsyncSession,
        max_samples: int = 100,
        user_id: Optional[uuid.UUID] = None,
        batch_size: int = 50,
    ) -> Dict[str, int]:
        """
        Ingest songs from existing lyrics in database.
        (Lyrics-MIDI dataset has loading issues, so we create songs from lyrics instead)

        Args:
            db: Database session
            max_samples: Maximum number of songs to ingest
            user_id: User ID to assign songs to (uses admin if None)
            batch_size: Number of samples to process in each batch

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info("Starting song ingestion from existing lyrics")
        logger.info(f"Target samples: {max_samples}, Batch size: {batch_size}")
        logger.info("(Using existing lyrics - Lyrics-MIDI dataset has issues)")

        # Get or determine user
        if user_id is None:
            user_id = await self._get_admin_user_id(db)

        # Get default voice profile
        voice_profile = await self._get_default_voice_profile(db)

        try:
            # Load existing lyrics from database
            result = await db.execute(
                select(Lyrics).where(Lyrics.user_id == user_id).limit(max_samples)
            )
            lyrics_list = result.scalars().all()

            if not lyrics_list:
                logger.warning("No lyrics found in database - skipping song ingestion")
                logger.info(
                    "Run lyrics ingestion first: python scripts/ingest_data.py --max-lyrics 100"
                )
                return self.stats

            # Limit to max_samples
            lyrics_list = lyrics_list[:max_samples]
            self.stats["loaded"] = len(lyrics_list)
            logger.success(f"Found {len(lyrics_list)} lyrics to convert to songs")

            # Process in batches
            for i in range(0, len(lyrics_list), batch_size):
                batch = lyrics_list[i : i + batch_size]
                await self._process_lyrics_batch(db, batch, user_id, voice_profile)

                if (i + batch_size) % 50 == 0:
                    logger.info(
                        f"Processed {min(i + batch_size, len(lyrics_list))}/{len(lyrics_list)} samples"
                    )

            logger.success(f"✅ Song ingestion complete!")
            logger.info(f"   Loaded: {self.stats['loaded']}")
            logger.info(f"   Processed: {self.stats['processed']}")
            logger.info(f"   Inserted: {self.stats['inserted']}")
            logger.info(f"   Skipped: {self.stats['skipped']}")
            logger.info(f"   Errors: {self.stats['errors']}")

        except Exception as e:
            logger.error(f"Error ingesting songs: {e}")
            logger.warning("⚠️  Skipping song ingestion - continuing with other steps")
            self.stats["errors"] += 1
            # Don't raise - allow pipeline to continue

        return self.stats

    async def _process_batch(
        self,
        db: AsyncSession,
        batch: List[Dict[str, Any]],
        user_id: uuid.UUID,
        voice_profile: Optional[VoiceProfile],
    ):
        """Process a batch of song samples."""
        for sample in batch:
            try:
                # Extract fields
                title = sample.get(self.LYRICS_MIDI_CONFIG["fields"]["title"], "Untitled")
                lyrics_text = sample.get(self.LYRICS_MIDI_CONFIG["fields"]["lyrics"], "")
                tempo = sample.get(self.LYRICS_MIDI_CONFIG["fields"]["tempo"])
                key = sample.get(self.LYRICS_MIDI_CONFIG["fields"]["key"])
                time_signature = sample.get(self.LYRICS_MIDI_CONFIG["fields"]["time_signature"])

                if not title or not lyrics_text:
                    self.stats["skipped"] += 1
                    continue

                # Create lyrics first
                lyrics = Lyrics(
                    user_id=user_id,
                    title=title,
                    content=lyrics_text,
                    structure={},  # Will be extracted later
                    language="en",
                )
                db.add(lyrics)
                await db.flush()

                # Convert tempo to BPM if needed
                bpm = None
                if tempo:
                    try:
                        bpm = int(float(tempo))
                    except (ValueError, TypeError):
                        pass

                # Create song
                song = Song(
                    user_id=user_id,
                    lyrics_id=lyrics.id,
                    title=title,
                    bpm=bpm,
                    key=key,
                    voice_profile_id=voice_profile.id if voice_profile else None,
                    music_params={
                        "time_signature": time_signature,
                        "midi_data": "available",  # MIDI data available in dataset
                    },
                    generation_status="completed",
                )

                db.add(song)
                self.stats["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing song sample: {e}")
                self.stats["errors"] += 1
                continue

        # Commit batch
        try:
            await db.commit()
            self.stats["inserted"] += self.stats["processed"]
        except Exception as e:
            logger.error(f"Error committing song batch: {e}")
            await db.rollback()
            self.stats["errors"] += 1

    async def _process_lyrics_batch(
        self,
        db: AsyncSession,
        batch: List[Lyrics],
        user_id: uuid.UUID,
        voice_profile: Optional[VoiceProfile],
    ):
        """Process a batch of lyrics and create songs."""
        for lyrics in batch:
            try:
                # Check if song already exists for this lyrics
                result = await db.execute(select(Song).where(Song.lyrics_id == lyrics.id))
                existing_song = result.scalar_one_or_none()

                if existing_song:
                    self.stats["skipped"] += 1
                    continue

                # Create song from lyrics
                song = Song(
                    user_id=user_id,
                    title=lyrics.title or "Untitled Song",
                    lyrics_id=lyrics.id,
                    genre=lyrics.genre or "pop",
                    mood=lyrics.mood or "neutral",
                    bpm=120,  # Default BPM
                    key="C",  # Default key
                    duration_seconds=180.0,  # Default 3 minutes
                    voice_profile_id=voice_profile.id if voice_profile else None,
                    music_params={
                        "source": "lyrics_database",
                        "lyrics_id": str(lyrics.id),
                        "auto_generated": True,
                    },
                    generation_status="pending",  # Not yet generated
                )

                db.add(song)
                self.stats["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing lyrics {lyrics.id}: {e}")
                self.stats["errors"] += 1
                continue

        # Commit batch
        try:
            await db.commit()
            self.stats["inserted"] += self.stats["processed"]
        except Exception as e:
            logger.error(f"Error committing lyrics batch: {e}")
            await db.rollback()
            self.stats["errors"] += 1

    async def _get_admin_user_id(self, db: AsyncSession) -> uuid.UUID:
        """Get admin user ID."""
        result = await db.execute(select(User).where(User.role == "admin").limit(1))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            raise ValueError("No admin user found. Run user setup first.")

        return admin_user.id

    async def _get_default_voice_profile(self, db: AsyncSession) -> Optional[VoiceProfile]:
        """Get default voice profile."""
        result = await db.execute(
            select(VoiceProfile).where(VoiceProfile.is_available.is_(True)).limit(1)
        )
        return result.scalar_one_or_none()
