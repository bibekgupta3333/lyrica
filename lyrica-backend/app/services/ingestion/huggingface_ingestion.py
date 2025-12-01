"""
Hugging Face Dataset Ingestion Service

Handles loading and processing lyrics from Hugging Face datasets.
"""

import os
from typing import Any, Dict, List, Optional

from datasets import load_dataset
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.lyrics import Lyrics
from app.models.user import User


class HuggingFaceIngestionService:
    """Service for ingesting lyrics from Hugging Face datasets."""

    # Dataset configurations with field mappings
    # Priority: Datasets with actual lyrics content that are publicly available
    DATASET_CONFIGS = {
        # Primary: Poetry dataset (reliable, publicly available)
        "genius-lyrics": {
            "full_name": "merve/poetry",  # Reliable poetry dataset
            "fields": {
                "title": "title",
                "content": "content",
                "artist": "author",
            },
        },
        # Song lyrics classifier dataset
        "lyrics-dataset": {
            "full_name": "csv",
            "data_files": "https://raw.githubusercontent.com/hiteshpatil237/lyrics-genre-classification/master/lyrics.csv",
            "fields": {
                "title": "song",
                "content": "lyrics",
                "artist": "artist",
                "genre": "genre",
            },
        },
        # Poetry as lyrics alternative
        "poetry": {
            "full_name": "merve/poetry",
            "fields": {
                "title": "title",
                "content": "content",
                "artist": "author",
            },
        },
        # Quotes dataset (can be used as lyrical content)
        "quotes": {
            "full_name": "Abirate/english_quotes",
            "fields": {
                "title": "author",
                "content": "quote",
                "artist": "author",
            },
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

    async def ingest_from_dataset(
        self,
        db: AsyncSession,
        dataset_name: str,
        max_samples: int = 1000,
        user_id: Optional[str] = None,
        batch_size: int = 100,
        min_length: int = 100,
        max_length: int = 10000,
    ) -> Dict[str, int]:
        """
        Ingest lyrics from a Hugging Face dataset.

        Args:
            db: Database session
            dataset_name: Short name of the dataset (e.g., 'genius-lyrics')
            max_samples: Maximum number of samples to ingest
            user_id: User ID to assign lyrics to (uses admin if None)
            batch_size: Number of samples to process in each batch
            min_length: Minimum lyrics length in characters
            max_length: Maximum lyrics length in characters

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Starting Hugging Face ingestion: {dataset_name}")
        logger.info(f"Target samples: {max_samples}, Batch size: {batch_size}")

        # Get or determine user
        if user_id is None:
            user_id = await self._get_admin_user_id(db)

        # Load dataset configuration
        # Handle both short names and full Hugging Face paths
        if "/" in dataset_name:
            # Full path provided (e.g., "huggingface-lyrics/genius-lyrics")
            # Extract short name or use full path directly
            short_name = dataset_name.split("/")[-1]  # "genius-lyrics"
            dataset_config = self._get_dataset_config(short_name)
            if not dataset_config:
                # Use full path directly if not in config
                logger.info(f"Using dataset directly: {dataset_name}")
                dataset_config = {
                    "full_name": dataset_name,
                    "fields": {
                        "title": "title",
                        "content": "lyrics",
                        "artist": "artist",
                    },
                }
        else:
            # Short name provided
            dataset_config = self._get_dataset_config(dataset_name)
            if not dataset_config:
                logger.error(f"Unknown dataset: {dataset_name}")
                return self.stats

        # Load dataset from Hugging Face (parquet-based, no trust_remote_code)
        try:
            logger.info(f"Loading dataset: {dataset_config['full_name']}")
            try:
                # Try loading with split limit (use cache)
                logger.info(f"Using cache directory: {self.cache_dir}")
                dataset = load_dataset(
                    dataset_config["full_name"],
                    split=f"train[:{max_samples}]",
                    cache_dir=self.cache_dir,
                )
            except Exception as e:
                logger.warning(f"Load with split limit failed: {e}, loading full train split")
                # Fallback: load full train split
                dataset = load_dataset(
                    dataset_config["full_name"],
                    split="train",
                    cache_dir=self.cache_dir,
                )

            # Handle DatasetDict
            if hasattr(dataset, "train"):
                dataset = dataset["train"]

            # Limit samples if needed
            if hasattr(dataset, "__len__"):
                actual_len = len(dataset)
                if actual_len > max_samples:
                    dataset = dataset.select(range(max_samples))
                logger.success(f"Loaded dataset with {len(dataset)} samples")
            else:
                # Streaming dataset - convert to list
                dataset = list(dataset.take(max_samples))
                logger.success(f"Loaded dataset with {len(dataset)} samples")
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            logger.warning("⚠️  Skipping lyrics ingestion - continuing with other steps")
            self.stats["errors"] += 1
            return self.stats

        # Process in batches
        samples_to_process = len(dataset)
        field_mapping = dataset_config["fields"]

        for batch_start in range(0, samples_to_process, batch_size):
            batch_end = min(batch_start + batch_size, samples_to_process)
            batch_samples = dataset[batch_start:batch_end]

            logger.info(f"Processing batch {batch_start}-{batch_end}...")

            await self._process_batch(
                db=db,
                batch_samples=batch_samples,
                field_mapping=field_mapping,
                user_id=user_id,
                min_length=min_length,
                max_length=max_length,
            )

        logger.info("")
        logger.success(f"✅ Ingestion complete!")
        logger.info(f"   Loaded: {self.stats['loaded']}")
        logger.info(f"   Processed: {self.stats['processed']}")
        logger.info(f"   Inserted: {self.stats['inserted']}")
        logger.info(f"   Skipped: {self.stats['skipped']}")
        logger.info(f"   Errors: {self.stats['errors']}")

        return self.stats

    async def _process_batch(
        self,
        db: AsyncSession,
        batch_samples: Any,
        field_mapping: Dict[str, str],
        user_id: str,
        min_length: int,
        max_length: int,
    ):
        """Process a batch of samples."""

        # Simple inline processing functions (no external dependencies)
        def clean_lyrics(text: str) -> str:
            """Basic lyrics cleaning."""
            if not text:
                return ""
            # Remove extra whitespace
            text = " ".join(text.split())
            # Remove common artifacts
            text = text.replace("\n\n\n", "\n\n")
            return text.strip()

        def categorize_lyrics(text: str) -> Dict[str, str]:
            """Simple categorization (can be enhanced later)."""
            text_lower = text.lower()
            # Simple genre detection
            genre = "pop"  # Default
            if any(word in text_lower for word in ["rock", "guitar", "electric"]):
                genre = "rock"
            elif any(word in text_lower for word in ["hip", "rap", "beat"]):
                genre = "hip-hop"
            elif any(word in text_lower for word in ["country", "cowboy", "ranch"]):
                genre = "country"

            # Simple mood detection
            mood = "neutral"
            if any(word in text_lower for word in ["happy", "joy", "smile", "laugh"]):
                mood = "happy"
            elif any(word in text_lower for word in ["sad", "cry", "tears", "lonely"]):
                mood = "sad"
            elif any(word in text_lower for word in ["love", "heart", "kiss", "romance"]):
                mood = "romantic"

            return {"genre": genre, "mood": mood}

        def extract_metadata(text: str) -> Dict[str, Any]:
            """Simple metadata extraction."""
            lines = text.split("\n")
            sections = []
            current_section = None

            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith("[") and line_stripped.endswith("]"):
                    if current_section:
                        sections.append(current_section)
                    current_section = {"type": line_stripped[1:-1].lower(), "lines": []}
                elif current_section:
                    current_section["lines"].append(line_stripped)

            if current_section:
                sections.append(current_section)

            return {
                "structure": {"sections": sections},
                "theme": "general",
                "language": "en",
                "quality_score": 0.7,
            }

        def validate_lyrics(
            title: str, content: str, genre: str, mood: str, language: str
        ) -> Dict[str, Any]:
            """Simple validation."""
            errors = []
            if not content or len(content.strip()) < min_length:
                errors.append(f"Content too short (min {min_length} chars)")
            if len(content) > max_length:
                errors.append(f"Content too long (max {max_length} chars)")

            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
            }

        # Get batch size
        if isinstance(batch_samples, dict):
            # Dataset returns dict of lists
            batch_size = len(batch_samples[list(batch_samples.keys())[0]])
        else:
            batch_size = len(batch_samples)

        for i in range(batch_size):
            try:
                # Extract fields
                if isinstance(batch_samples, dict):
                    sample = {key: batch_samples[key][i] for key in batch_samples.keys()}
                else:
                    sample = batch_samples[i]

                self.stats["loaded"] += 1

                # Map fields
                title = self._get_field(sample, field_mapping.get("title", "title"))
                content = self._get_field(sample, field_mapping.get("content", "lyrics"))
                artist = self._get_field(sample, field_mapping.get("artist"))
                genre = self._get_field(sample, field_mapping.get("genre"))

                # Basic validation (minimal - only skip if completely empty)
                if not content or len(content.strip()) == 0:
                    self.stats["skipped"] += 1
                    continue

                # Truncate if too long (but don't skip)
                if len(content) > max_length:
                    content = content[:max_length]

                # Clean content (always proceed even if cleaning removes some content)
                cleaned_content = clean_lyrics(content)
                if not cleaned_content:
                    # Use original content if cleaning removed everything
                    cleaned_content = content.strip()
                    if not cleaned_content:
                        self.stats["skipped"] += 1
                        continue

                self.stats["processed"] += 1

                # Categorize (genre, mood)
                categorization = categorize_lyrics(cleaned_content)
                genre = genre or categorization.get("genre", "unknown")
                mood = categorization.get("mood", "neutral")

                # Extract metadata
                metadata = extract_metadata(cleaned_content)
                structure = metadata.get("structure", {"sections": []})
                theme = metadata.get("theme")
                language = metadata.get("language", "en")
                quality_score = metadata.get("quality_score", 0.7)

                # Validate (non-blocking - log warnings but don't skip)
                validation = validate_lyrics(
                    title=title or "Untitled",
                    content=cleaned_content,
                    genre=genre,
                    mood=mood,
                    language=language,
                )

                if not validation["is_valid"]:
                    logger.warning(
                        f"Validation warnings (proceeding anyway): {validation.get('errors', [])}"
                    )
                    # Continue processing despite validation warnings

                # Create Lyrics object
                lyrics = Lyrics(
                    user_id=user_id,
                    title=title or "Untitled",
                    content=cleaned_content,
                    structure=structure,
                    genre=genre,
                    mood=mood,
                    theme=theme,
                    language=language,
                    quality_score=quality_score,
                    is_public=True,
                    status="published",
                    generation_params={
                        "source": "huggingface",
                        "artist": artist,
                    },
                )

                db.add(lyrics)
                self.stats["inserted"] += 1

            except Exception as e:
                logger.error(f"Error processing sample {i}: {e}")
                self.stats["errors"] += 1
                continue

        # Commit batch
        try:
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to commit batch: {e}")
            await db.rollback()
            self.stats["errors"] += 1

    def _get_dataset_config(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get dataset configuration by name."""
        return self.DATASET_CONFIGS.get(dataset_name)

    def _get_field(self, sample: Dict[str, Any], field_name: Optional[str]) -> Optional[str]:
        """Safely get a field from a sample."""
        if not field_name:
            return None

        value = sample.get(field_name)
        if value is None:
            return None

        # Handle list values (e.g., artists list)
        if isinstance(value, list):
            return ", ".join(str(v) for v in value if v)

        return str(value) if value else None

    async def _get_admin_user_id(self, db: AsyncSession) -> str:
        """Get admin user ID."""
        result = await db.execute(select(User).where(User.role == "admin"))
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            raise ValueError("No admin user found. Please run user setup first.")

        return str(admin_user.id)

    def list_available_datasets(self) -> List[Dict[str, str]]:
        """List all available datasets."""
        return [
            {
                "short_name": short_name,
                "full_name": config["full_name"],
                "fields": ", ".join(config["fields"].values()),
            }
            for short_name, config in self.DATASET_CONFIGS.items()
        ]
