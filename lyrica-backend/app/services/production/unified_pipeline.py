"""
Unified Pipeline for Voice Enhancement and Music Mixing.

This module provides a complete end-to-end pipeline that integrates:
- Voice synthesis with enhancement
- Music generation
- Intelligent mixing with memory system
- Quality tracking and feedback loop
"""

import uuid
from pathlib import Path
from typing import Dict, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enhancement_config import get_enhancement_config
from app.core.music_config import MusicGenre
from app.services.music import get_music_generation
from app.services.production import get_song_assembly, get_song_mastering
from app.services.voice import get_voice_enhancement, get_voice_synthesis


class UnifiedPipelineService:
    """
    Unified pipeline service for complete song generation with enhancement.

    This service orchestrates:
    1. Voice synthesis with enhancement
    2. Music generation
    3. Intelligent mixing (frequency balancing, stereo imaging, genre-specific)
    4. Quality tracking and feedback collection
    5. Memory-based optimization
    """

    def __init__(self):
        """Initialize unified pipeline service."""
        self.voice_synthesis = get_voice_synthesis()
        self.voice_enhancement = get_voice_enhancement()
        self.music_generation = get_music_generation()
        self.song_assembly = get_song_assembly()
        self.song_mastering = get_song_mastering()
        self.config_manager = get_enhancement_config()
        logger.success("UnifiedPipelineService initialized")

    async def generate_complete_song_with_enhancement(
        self,
        lyrics_text: str,
        voice_profile_id: str,
        genre: str,
        bpm: int,
        key: Optional[str],
        duration: int,
        output_dir: Path,
        db: Optional[AsyncSession] = None,
        user_id: Optional[uuid.UUID] = None,
        song_id: Optional[uuid.UUID] = None,
        enable_voice_enhancement: bool = True,
        enable_intelligent_mixing: bool = True,
        enable_memory_learning: bool = True,
        mixing_config_id: Optional[uuid.UUID] = None,
    ) -> Dict:
        """
        Generate complete song with voice enhancement and intelligent mixing.

        Args:
            lyrics_text: Lyrics text to synthesize
            voice_profile_id: Voice profile ID
            genre: Music genre
            bpm: Beats per minute
            key: Musical key
            duration: Duration in seconds
            output_dir: Output directory for audio files
            db: Optional database session
            user_id: Optional user ID
            song_id: Optional song ID
            enable_voice_enhancement: Enable voice enhancement (neural vocoder, prosody)
            enable_intelligent_mixing: Enable intelligent mixing (frequency balancing, stereo imaging)
            enable_memory_learning: Enable memory-based learning and optimization
            mixing_config_id: Optional mixing configuration ID to use

        Returns:
            Dictionary with paths and metadata:
            {
                "vocals_path": Path,
                "enhanced_vocals_path": Path,
                "music_path": Path,
                "mixed_path": Path,
                "final_path": Path,
                "preview_path": Path,
                "mixing_config_id": UUID,
                "quality_metrics": dict,
            }
        """
        logger.info(
            f"Generating complete song with enhancement: "
            f"voice_enhancement={enable_voice_enhancement}, "
            f"intelligent_mixing={enable_intelligent_mixing}, "
            f"memory_learning={enable_memory_learning}"
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        genre_enum = self._normalize_genre(genre)

        # Step 1: Generate vocals
        logger.info("Step 1/6: Generating vocals")
        vocals_path = output_dir / "vocals_raw.wav"
        from app.core.voice_config import get_voice_profile

        voice_profile = get_voice_profile(voice_profile_id)
        self.voice_synthesis.synthesize_lyrics(
            lyrics=lyrics_text,
            voice_profile=voice_profile,
            output_path=vocals_path,
            chunk_sentences=True,
        )

        # Step 2: Enhance vocals (if enabled)
        enhanced_vocals_path = vocals_path
        if enable_voice_enhancement:
            logger.info("Step 2/6: Enhancing vocals")
            try:
                enhanced_vocals_path = output_dir / "vocals_enhanced.wav"
                enhanced_vocals_path = self.voice_enhancement.enhance_tts_output(
                    tts_output_path=vocals_path, output_path=enhanced_vocals_path
                )
                logger.success("Voice enhancement completed")
            except Exception as e:
                if self.config_manager.settings.fallback_on_error:
                    logger.warning(f"Voice enhancement failed, using raw vocals: {e}")
                    enhanced_vocals_path = vocals_path
                else:
                    raise

        # Step 3: Generate music
        logger.info("Step 3/6: Generating instrumental music")
        music_path = output_dir / "music.wav"
        from app.core.music_config import MusicKey

        key_enum = None
        if key:
            try:
                key_enum = MusicKey(key.lower().replace(" ", "_"))
            except ValueError:
                logger.warning(f"Invalid key '{key}', using default")

        self.music_generation.generate_by_genre(
            genre=genre_enum,
            mood=None,
            key=key_enum,
            bpm=bpm,
            duration=duration,
            output_path=music_path,
        )

        # Step 4: Get mixing recommendations from memory (if enabled)
        mixing_config_id_to_use = mixing_config_id
        if enable_memory_learning and db:
            logger.info("Step 4/6: Getting mixing recommendations from memory")
            try:
                from app.agents.memory_agent import MemoryAgent

                memory_agent = MemoryAgent()
                from app.agents.state import AgentState

                # Create a minimal state for memory agent
                state = AgentState(
                    user_id=int(user_id.int) if user_id else 1,
                    prompt=lyrics_text[:100],
                    genre=genre,
                )
                recommendations = await memory_agent.run(state, db=db)
                if recommendations.get("mixing_recommendations"):
                    logger.info("Mixing recommendations retrieved from memory")
            except Exception as e:
                if self.config_manager.settings.fallback_on_error:
                    logger.warning(f"Memory agent failed, using default mixing: {e}")
                elif self.config_manager.settings.log_failures:
                    logger.error(f"Memory agent failed: {e}")

        # Step 5: Mix vocals and music with intelligent mixing
        logger.info("Step 5/6: Mixing vocals and music")
        mixed_path = output_dir / "mixed.wav"
        self.song_assembly.assemble_song(
            vocals_path=enhanced_vocals_path,
            music_path=music_path,
            output_path=mixed_path,
            vocals_volume_db=0.0,
            music_volume_db=-5.0,
            crossfade_ms=500,
            use_intelligent_mixing=enable_intelligent_mixing,
            genre=genre_enum,
        )

        # Step 6: Master song
        logger.info("Step 6/6: Applying final mastering")
        final_path = output_dir / "final.wav"
        self.song_mastering.master_song(song_path=mixed_path, output_path=final_path, genre=genre)

        # Step 7: Create preview
        preview_path = output_dir / "preview.wav"
        self.song_assembly.create_song_preview(
            song_path=final_path, preview_duration=30, output_path=preview_path
        )

        # Step 8: Track quality metrics (if enabled and db available)
        quality_metrics = {}
        if enable_memory_learning and db:
            try:
                from app.services.voice.quality_metrics import get_quality_metrics

                quality_service = get_quality_metrics()
                quality_metrics = quality_service.calculate_all_metrics(audio_path=final_path)
                logger.info(f"Quality metrics calculated: {quality_metrics}")
            except Exception as e:
                logger.warning(f"Quality metrics calculation failed: {e}")

        logger.success(f"Complete song generated: {final_path}")

        return {
            "vocals_path": str(vocals_path),
            "enhanced_vocals_path": str(enhanced_vocals_path),
            "music_path": str(music_path),
            "mixed_path": str(mixed_path),
            "final_path": str(final_path),
            "preview_path": str(preview_path),
            "mixing_config_id": str(mixing_config_id_to_use) if mixing_config_id_to_use else None,
            "quality_metrics": quality_metrics,
        }

    def _normalize_genre(self, genre: str) -> MusicGenre:
        """Normalize genre string to MusicGenre enum."""
        if not genre:
            return MusicGenre.POP

        genre_normalized = genre.lower().strip()
        genre_mapping = {
            "hip-hop": "hiphop",
            "hip hop": "hiphop",
            "r&b": "rnb",
            "r and b": "rnb",
            "rnb": "rnb",
            "ballad": "pop",
        }

        genre_normalized = genre_mapping.get(genre_normalized, genre_normalized)

        try:
            return MusicGenre(genre_normalized)
        except ValueError:
            logger.warning(f"Invalid genre '{genre}', defaulting to pop")
            return MusicGenre.POP


# Singleton instance
_unified_pipeline_service: Optional[UnifiedPipelineService] = None


def get_unified_pipeline() -> UnifiedPipelineService:
    """Get or create unified pipeline service instance."""
    global _unified_pipeline_service
    if _unified_pipeline_service is None:
        _unified_pipeline_service = UnifiedPipelineService()
    return _unified_pipeline_service
