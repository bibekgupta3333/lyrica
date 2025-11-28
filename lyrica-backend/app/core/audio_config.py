"""
Audio processing configuration.

This module defines settings and constants for audio processing operations.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    """Supported audio formats."""

    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"


class AudioQuality(str, Enum):
    """Audio quality presets."""

    LOW = "low"  # 64kbps, 22.05kHz
    MEDIUM = "medium"  # 128kbps, 44.1kHz
    HIGH = "high"  # 192kbps, 44.1kHz
    LOSSLESS = "lossless"  # WAV/FLAC, 48kHz


class AudioConfig(BaseModel):
    """Audio processing configuration."""

    # Storage
    storage_path: Path = Field(default=Path("audio_files"))
    max_file_size_mb: int = Field(default=50)
    allowed_formats: list[AudioFormat] = Field(
        default=[AudioFormat.MP3, AudioFormat.WAV, AudioFormat.OGG]
    )

    # Processing
    default_sample_rate: int = Field(default=44100)  # Hz
    default_bit_depth: int = Field(default=16)  # bits
    default_channels: int = Field(default=2)  # stereo

    # Quality settings
    mp3_bitrate: dict[AudioQuality, int] = Field(
        default={
            AudioQuality.LOW: 64,
            AudioQuality.MEDIUM: 128,
            AudioQuality.HIGH: 192,
            AudioQuality.LOSSLESS: 320,
        }
    )

    # Waveform generation
    waveform_width: int = Field(default=1800)  # pixels
    waveform_height: int = Field(default=280)  # pixels
    waveform_color: str = Field(default="#1DB954")  # Spotify green

    # Mixing
    max_tracks: int = Field(default=10)
    default_fade_duration: float = Field(default=2.0)  # seconds

    # Normalization
    target_lufs: float = Field(default=-14.0)  # LUFS
    true_peak_limit: float = Field(default=-1.0)  # dBTP

    # Limits
    max_duration_seconds: int = Field(default=600)  # 10 minutes
    chunk_size: int = Field(default=1024)  # bytes


# Global audio config instance
audio_config = AudioConfig()


def get_audio_config() -> AudioConfig:
    """Get audio configuration."""
    return audio_config


# Audio file naming
def get_audio_filename(prefix: str, format: AudioFormat, user_id: Optional[str] = None) -> str:
    """
    Generate a unique audio filename.

    Args:
        prefix: File prefix (e.g., "song", "voice", "music")
        format: Audio format
        user_id: Optional user ID

    Returns:
        Filename string

    Example:
        >>> get_audio_filename("song", AudioFormat.MP3, "user123")
        "song_user123_20231128_143022.mp3"
    """
    import uuid
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    if user_id:
        return f"{prefix}_{user_id}_{timestamp}_{unique_id}.{format.value}"
    return f"{prefix}_{timestamp}_{unique_id}.{format.value}"
