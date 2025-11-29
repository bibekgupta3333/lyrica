"""
Final mastering service for songs.

This module provides the final mastering pipeline including
EQ, compression, limiting, and loudness normalization.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.services.audio.mastering import get_audio_mastering


class SongMasteringService:
    """Service for final song mastering."""

    def __init__(self):
        """Initialize song mastering service."""
        self.mastering_service = get_audio_mastering()

    def master_song(
        self,
        song_path: Path,
        output_path: Optional[Path] = None,
        target_loudness: float = -14.0,
        genre: Optional[str] = None,
    ) -> Path:
        """
        Apply complete mastering chain to song.

        Args:
            song_path: Path to song audio
            output_path: Optional output path
            target_loudness: Target LUFS loudness
            genre: Optional genre for genre-specific mastering

        Returns:
            Path to mastered song

        Example:
            ```python
            service = SongMasteringService()
            mastered = service.master_song(
                song_path=Path("raw_song.wav"),
                target_loudness=-14.0,  # Spotify/streaming standard
                genre="pop"
            )
            ```
        """
        logger.info(f"Mastering song with target loudness: {target_loudness} LUFS")

        # Apply genre-specific mastering
        if genre:
            target_loudness = self._get_genre_target_loudness(genre)
            logger.info(f"Using {genre} mastering preset: {target_loudness} LUFS")

        # Apply mastering chain
        mastered_path = self.mastering_service.apply_mastering_chain(
            audio_path=song_path,
            output_path=output_path,
            target_loudness=target_loudness,
            peak_limit=-1.0,  # Standard peak limit
            apply_compression=True,
        )

        logger.success(f"Song mastered: {mastered_path}")
        return mastered_path

    def _get_genre_target_loudness(self, genre: str) -> float:
        """
        Get target loudness for specific genre.

        Different genres have different loudness standards.

        Args:
            genre: Music genre

        Returns:
            Target LUFS loudness
        """
        genre_loudness = {
            "pop": -14.0,  # Streaming standard
            "rock": -12.0,  # Louder, more aggressive
            "electronic": -11.0,  # Very loud
            "hiphop": -13.0,  # Moderately loud
            "jazz": -18.0,  # Quieter, more dynamic
            "classical": -20.0,  # Very dynamic
            "country": -15.0,  # Moderate
            "rnb": -14.0,  # Streaming standard
            "indie": -16.0,  # Quieter, organic
            "metal": -10.0,  # Very loud
            "ambient": -16.0,  # Quieter, atmospheric
        }

        return genre_loudness.get(genre.lower(), -14.0)

    def create_radio_edit(
        self, song_path: Path, target_duration: int = 180, output_path: Optional[Path] = None
    ) -> Path:
        """
        Create radio edit version (typically 3 minutes).

        Args:
            song_path: Path to full song
            target_duration: Target duration in seconds (default: 180s = 3min)
            output_path: Optional output path

        Returns:
            Path to radio edit

        Example:
            Create 3-minute radio edit:
            ```python
            radio_edit = service.create_radio_edit(
                song_path=Path("full_song.wav"),
                target_duration=180
            )
            ```
        """
        from pydub import AudioSegment

        logger.info(f"Creating radio edit: {target_duration}s")

        # Load song
        song = AudioSegment.from_file(str(song_path))
        song_duration_s = len(song) / 1000

        if song_duration_s <= target_duration:
            logger.info("Song already within target duration")
            return song_path

        # Trim to target duration
        target_ms = target_duration * 1000
        radio_edit = song[:target_ms]

        # Add fade out at the end
        radio_edit = radio_edit.fade_out(3000)  # 3 second fade

        # Generate output path
        if output_path is None:
            output_path = song_path.with_stem(f"{song_path.stem}_radio")

        # Export
        radio_edit.export(str(output_path), format="wav")

        logger.success(f"Radio edit created: {output_path}")
        return output_path

    def create_instrumental_version(
        self, song_path: Path, output_path: Optional[Path] = None
    ) -> Path:
        """
        Create instrumental version (placeholder for vocal removal).

        Note: True vocal removal requires specialized models.
        This is a placeholder for future implementation.

        Args:
            song_path: Path to full song
            output_path: Optional output path

        Returns:
            Path to instrumental version
        """
        logger.warning("Instrumental extraction not fully implemented (placeholder)")

        # For now, just return the original
        # Future: Use models like Demucs, Spleeter for source separation

        from shutil import copy2

        if output_path is None:
            output_path = song_path.with_stem(f"{song_path.stem}_instrumental")

        copy2(song_path, output_path)

        return output_path

    def create_acapella_version(self, song_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Create acapella version (vocals only, placeholder).

        Note: True vocal isolation requires specialized models.
        This is a placeholder for future implementation.

        Args:
            song_path: Path to full song
            output_path: Optional output path

        Returns:
            Path to acapella version
        """
        logger.warning("Acapella extraction not fully implemented (placeholder)")

        # Future: Use models like Demucs, Spleeter for source separation

        from shutil import copy2

        if output_path is None:
            output_path = song_path.with_stem(f"{song_path.stem}_acapella")

        copy2(song_path, output_path)

        return output_path


# Singleton instance
_mastering_service: Optional[SongMasteringService] = None


def get_song_mastering() -> SongMasteringService:
    """Get or create song mastering service instance."""
    global _mastering_service
    if _mastering_service is None:
        _mastering_service = SongMasteringService()
    return _mastering_service
