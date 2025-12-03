"""
Voice synthesis configuration.

This module defines settings and constants for voice synthesis and TTS operations.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class VoiceGender(str, Enum):
    """Voice gender options."""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceStyle(str, Enum):
    """Voice style/emotion options."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    WHISPER = "whisper"
    SHOUTING = "shouting"


class TTSEngine(str, Enum):
    """Available TTS engines."""

    BARK = "bark"  # Suno AI's Bark (best quality, slower) - Requires Python <=3.11
    COQUI = "coqui"  # Coqui TTS (fast, good quality) - Requires Python <=3.11
    TORTOISE = "tortoise"  # Tortoise TTS (high quality, very slow) - Requires Python <=3.11
    EDGE = "edge"  # Edge TTS (fast, cloud-based) - Python 3.12 compatible
    GTTS = "gtts"  # Google TTS (cloud-based, simple) - Python 3.12 compatible
    PYTTSX3 = "pyttsx3"  # Offline TTS (system voices) - Python 3.12 compatible


class VoiceProfile(BaseModel):
    """Voice profile definition."""

    id: str = Field(..., description="Unique voice profile ID")
    name: str = Field(..., description="Display name")
    gender: VoiceGender = Field(default=VoiceGender.NEUTRAL)
    language: str = Field(default="en", description="Language code")
    accent: Optional[str] = Field(default=None, description="Accent type")
    age_range: Optional[str] = Field(default=None, description="Age range (young/adult/senior)")
    description: Optional[str] = Field(default=None)
    engine: TTSEngine = Field(default=TTSEngine.BARK)
    engine_voice_id: str = Field(..., description="Engine-specific voice identifier")


class VoiceConfig(BaseModel):
    """Voice synthesis configuration."""

    # Storage
    voice_models_path: Path = Field(default=Path("voice_models"))
    generated_voices_path: Path = Field(default=Path("audio_files/voices"))

    # TTS Settings
    default_engine: TTSEngine = Field(default=TTSEngine.EDGE)  # Changed to Edge for Python 3.12
    default_sample_rate: int = Field(default=24000)  # Hz
    default_temperature: float = Field(default=0.7)  # Creativity
    default_speed: float = Field(default=1.0)  # Playback speed

    # Pitch adjustment
    pitch_shift_semitones_range: tuple[float, float] = Field(default=(-12.0, 12.0))
    default_pitch_shift: float = Field(default=0.0)

    # Tempo control
    tempo_range: tuple[float, float] = Field(default=(0.5, 2.0))
    default_tempo: float = Field(default=1.0)

    # Voice effects
    reverb_room_size: float = Field(default=0.5, ge=0.0, le=1.0)
    echo_delay_ms: int = Field(default=500)
    echo_decay: float = Field(default=0.3, ge=0.0, le=1.0)

    # Quality
    max_text_length: int = Field(default=500)  # characters
    chunk_size: int = Field(default=100)  # characters per chunk
    silence_duration_ms: int = Field(default=500)  # Between chunks

    # Performance
    use_gpu: bool = Field(default=False)
    batch_size: int = Field(default=1)


# Predefined voice profiles
VOICE_PROFILES = [
    VoiceProfile(
        id="male_narrator_1",
        name="Male Narrator",
        gender=VoiceGender.MALE,
        language="en",
        accent="american",
        age_range="adult",
        description="Deep, clear male voice suitable for storytelling",
        engine=TTSEngine.EDGE,  # Changed to Edge for Python 3.12 compatibility
        engine_voice_id="en-US-GuyNeural",
    ),
    VoiceProfile(
        id="female_singer_1",
        name="Female Singer",
        gender=VoiceGender.FEMALE,
        language="en",
        accent="american",
        age_range="young",
        description="Clear, melodic female voice perfect for singing",
        engine=TTSEngine.EDGE,  # Changed to Edge for Python 3.12 compatibility
        engine_voice_id="en-US-JennyNeural",
    ),
    VoiceProfile(
        id="male_singer_1",
        name="Male Singer",
        gender=VoiceGender.MALE,
        language="en",
        accent="american",
        age_range="adult",
        description="Rich male voice with good range for singing",
        engine=TTSEngine.EDGE,  # Changed to Edge for Python 3.12 compatibility
        engine_voice_id="en-US-ChristopherNeural",
    ),
    VoiceProfile(
        id="neutral_soft",
        name="Soft Narrator",
        gender=VoiceGender.NEUTRAL,
        language="en",
        accent="neutral",
        age_range="adult",
        description="Gentle, soothing voice",
        engine=TTSEngine.EDGE,  # Changed to Edge for Python 3.12 compatibility
        engine_voice_id="en-US-AriaNeural",
    ),
]


# Global voice config instance
voice_config = VoiceConfig()


def get_voice_config() -> VoiceConfig:
    """Get voice configuration."""
    return voice_config


def get_voice_profile(profile_id: str) -> Optional[VoiceProfile]:
    """
    Get voice profile by ID.

    Args:
        profile_id: Voice profile ID

    Returns:
        VoiceProfile if found, None otherwise
    """
    for profile in VOICE_PROFILES:
        if profile.id == profile_id:
            return profile
    return None


def list_voice_profiles(
    gender: Optional[VoiceGender] = None,
    language: Optional[str] = None,
    engine: Optional[TTSEngine] = None,
) -> list[VoiceProfile]:
    """
    List available voice profiles with optional filtering.

    Args:
        gender: Filter by gender
        language: Filter by language
        engine: Filter by TTS engine

    Returns:
        List of matching voice profiles
    """
    profiles = VOICE_PROFILES.copy()

    if gender:
        profiles = [p for p in profiles if p.gender == gender]

    if language:
        profiles = [p for p in profiles if p.language == language]

    if engine:
        profiles = [p for p in profiles if p.engine == engine]

    return profiles
