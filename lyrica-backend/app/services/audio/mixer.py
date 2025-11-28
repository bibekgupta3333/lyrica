"""
Audio mixing service.

Combines multiple audio tracks, applies effects, and creates final mixes.
"""

from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydub import AudioSegment
from pydub.effects import normalize as pydub_normalize

from app.core.audio_config import get_audio_config


class AudioMixerService:
    """Service for mixing and combining audio tracks."""

    def __init__(self):
        """Initialize mixer service."""
        self.config = get_audio_config()

    def mix_tracks(
        self,
        tracks: List[Path],
        output_path: Path,
        volumes: Optional[List[float]] = None,
    ) -> Path:
        """
        Mix multiple audio tracks into one.

        Args:
            tracks: List of audio file paths to mix
            output_path: Output path for mixed audio
            volumes: Optional list of volume multipliers (0.0-1.0)

        Returns:
            Path to mixed audio file

        Example:
            ```python
            mixed = mixer.mix_tracks(
                tracks=[vocals.mp3, music.mp3],
                output_path=song.mp3,
                volumes=[1.0, 0.8]  # Vocals at 100%, music at 80%
            )
            ```
        """
        if len(tracks) == 0:
            raise ValueError("At least one track is required")

        if len(tracks) > self.config.max_tracks:
            raise ValueError(f"Too many tracks: {len(tracks)} (max: {self.config.max_tracks})")

        logger.info(f"Mixing {len(tracks)} tracks")

        # Load first track as base
        mixed = AudioSegment.from_file(str(tracks[0]))

        # Apply volume if specified
        if volumes and len(volumes) > 0:
            mixed = mixed + (20 * np.log10(volumes[0]))  # dB adjustment

        # Overlay remaining tracks
        for i, track_path in enumerate(tracks[1:], start=1):
            track = AudioSegment.from_file(str(track_path))

            # Apply volume
            if volumes and i < len(volumes):
                track = track + (20 * np.log10(volumes[i]))

            # Overlay (mix) the track
            mixed = mixed.overlay(track)

        # Export
        mixed.export(str(output_path), format=output_path.suffix[1:])

        logger.success(f"Mixed {len(tracks)} tracks to: {output_path}")
        return output_path

    def concatenate_tracks(
        self,
        tracks: List[Path],
        output_path: Path,
        crossfade_ms: int = 0,
    ) -> Path:
        """
        Concatenate audio tracks sequentially.

        Args:
            tracks: List of audio file paths
            output_path: Output path
            crossfade_ms: Crossfade duration in milliseconds

        Returns:
            Path to concatenated audio
        """
        if len(tracks) == 0:
            raise ValueError("At least one track is required")

        logger.info(f"Concatenating {len(tracks)} tracks")

        # Load first track
        combined = AudioSegment.from_file(str(tracks[0]))

        # Append remaining tracks
        for track_path in tracks[1:]:
            track = AudioSegment.from_file(str(track_path))

            if crossfade_ms > 0:
                combined = combined.append(track, crossfade=crossfade_ms)
            else:
                combined = combined + track

        # Export
        combined.export(str(output_path), format=output_path.suffix[1:])

        logger.success(f"Concatenated audio saved: {output_path}")
        return output_path

    def add_fade(
        self,
        audio_path: Path,
        fade_in_ms: int = 0,
        fade_out_ms: int = 0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add fade in/out to audio.

        Args:
            audio_path: Path to audio file
            fade_in_ms: Fade in duration (milliseconds)
            fade_out_ms: Fade out duration (milliseconds)
            output_path: Optional output path

        Returns:
            Path to audio with fades
        """
        logger.info(f"Adding fades: in={fade_in_ms}ms, out={fade_out_ms}ms")

        audio = AudioSegment.from_file(str(audio_path))

        if fade_in_ms > 0:
            audio = audio.fade_in(fade_in_ms)

        if fade_out_ms > 0:
            audio = audio.fade_out(fade_out_ms)

        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_faded")

        audio.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Fades applied: {output_path}")
        return output_path

    def adjust_volume(
        self,
        audio_path: Path,
        volume_db: float,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Adjust audio volume.

        Args:
            audio_path: Path to audio file
            volume_db: Volume adjustment in dB (positive to increase, negative to decrease)
            output_path: Optional output path

        Returns:
            Path to adjusted audio
        """
        logger.info(f"Adjusting volume by {volume_db:+.1f}dB")

        audio = AudioSegment.from_file(str(audio_path))
        audio = audio + volume_db

        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_vol{volume_db:+.0f}db")

        audio.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Volume adjusted: {output_path}")
        return output_path

    def trim_silence(
        self,
        audio_path: Path,
        silence_thresh_db: int = -50,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Trim silence from beginning and end.

        Args:
            audio_path: Path to audio file
            silence_thresh_db: Silence threshold in dB
            output_path: Optional output path

        Returns:
            Path to trimmed audio
        """
        from pydub.silence import detect_leading_silence

        logger.info("Trimming silence")

        audio = AudioSegment.from_file(str(audio_path))

        # Detect silence at start and end
        start_trim = detect_leading_silence(audio, silence_threshold=silence_thresh_db)
        end_trim = detect_leading_silence(audio.reverse(), silence_threshold=silence_thresh_db)

        # Trim
        duration = len(audio)
        trimmed = audio[start_trim : duration - end_trim]

        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_trimmed")

        trimmed.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Trimmed {start_trim + end_trim}ms silence: {output_path}")
        return output_path

    def apply_reverb(
        self,
        audio_path: Path,
        room_size: float = 0.5,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply reverb effect (placeholder - requires external library).

        Args:
            audio_path: Path to audio file
            room_size: Room size (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to audio with reverb
        """
        logger.warning("Reverb effect requires pedalboard library (not implemented)")

        # Placeholder - copy file
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_reverb")

        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(output_path), format=audio_path.suffix[1:])

        return output_path


# Import numpy for volume calculations
import numpy as np

# Singleton instance
_mixer_service: Optional[AudioMixerService] = None


def get_audio_mixer() -> AudioMixerService:
    """Get or create audio mixer service instance."""
    global _mixer_service
    if _mixer_service is None:
        _mixer_service = AudioMixerService()
    return _mixer_service
