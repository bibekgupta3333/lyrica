"""
Music generation configuration.

This module defines settings and constants for AI-powered music generation.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class MusicGenre(str, Enum):
    """Available music genres."""

    POP = "pop"
    ROCK = "rock"
    HIPHOP = "hiphop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    RNB = "rnb"
    INDIE = "indie"
    FOLK = "folk"
    METAL = "metal"
    BLUES = "blues"
    REGGAE = "reggae"
    LATIN = "latin"
    AMBIENT = "ambient"


class MusicKey(str, Enum):
    """Musical keys."""

    C_MAJOR = "C"
    C_SHARP_MAJOR = "C#"
    D_MAJOR = "D"
    D_SHARP_MAJOR = "D#"
    E_MAJOR = "E"
    F_MAJOR = "F"
    F_SHARP_MAJOR = "F#"
    G_MAJOR = "G"
    G_SHARP_MAJOR = "G#"
    A_MAJOR = "A"
    A_SHARP_MAJOR = "A#"
    B_MAJOR = "B"

    A_MINOR = "Am"
    B_MINOR = "Bm"
    C_MINOR = "Cm"
    D_MINOR = "Dm"
    E_MINOR = "Em"
    F_MINOR = "Fm"
    G_MINOR = "Gm"


class MusicMood(str, Enum):
    """Music mood/emotion."""

    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    DARK = "dark"
    UPLIFTING = "uplifting"
    MELANCHOLIC = "melancholic"
    AGGRESSIVE = "aggressive"
    ROMANTIC = "romantic"
    MYSTERIOUS = "mysterious"


class MusicStructure(str, Enum):
    """Song structure sections."""

    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    BREAKDOWN = "breakdown"
    SOLO = "solo"


class InstrumentType(str, Enum):
    """Instrument types."""

    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    STRINGS = "strings"
    SYNTH = "synth"
    BRASS = "brass"
    WOODWIND = "woodwind"
    PERCUSSION = "percussion"
    VOCALS = "vocals"


class MusicGenerationConfig(BaseModel):
    """Music generation configuration."""

    # Storage
    generated_music_path: Path = Field(default=Path("audio_files/music"))
    music_models_path: Path = Field(default=Path("music_models"))

    # Generation Settings
    default_genre: MusicGenre = Field(default=MusicGenre.POP)
    default_key: MusicKey = Field(default=MusicKey.C_MAJOR)
    default_bpm: int = Field(default=120, ge=40, le=200)
    default_duration_seconds: int = Field(default=30, ge=5, le=300)

    # Quality Settings
    sample_rate: int = Field(default=32000)  # Hz
    channels: int = Field(default=2)  # Stereo
    bit_depth: int = Field(default=16)

    # Model Settings
    model_name: str = Field(default="facebook/musicgen-small")
    use_gpu: bool = Field(default=False)
    max_generation_length: int = Field(default=30)  # seconds

    # Chord Progression
    max_chords_per_progression: int = Field(default=8)
    allow_complex_chords: bool = Field(default=True)

    # Melody Settings
    melody_note_range: tuple[int, int] = Field(default=(48, 84))  # MIDI notes (C3-C6)
    melody_tempo_range: tuple[int, int] = Field(default=(60, 180))  # BPM

    # Rhythm Settings
    time_signature_numerator: int = Field(default=4)
    time_signature_denominator: int = Field(default=4)


# Common chord progressions by genre
GENRE_CHORD_PROGRESSIONS = {
    MusicGenre.POP: [
        ["I", "V", "vi", "IV"],  # C - G - Am - F (very common)
        ["vi", "IV", "I", "V"],  # Am - F - C - G
        ["I", "vi", "IV", "V"],  # C - Am - F - G
    ],
    MusicGenre.ROCK: [
        ["I", "IV", "V", "IV"],  # C - F - G - F (power chords)
        ["I", "bVII", "IV", "I"],  # C - Bb - F - C
        ["i", "bVII", "bVI", "V"],  # Cm - Bb - Ab - G
    ],
    MusicGenre.JAZZ: [
        ["IIm7", "V7", "Imaj7", "VImaj7"],  # ii-V-I progression
        ["Im7", "IVm7", "bVII7", "IIImaj7"],
    ],
    MusicGenre.BLUES: [
        ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
    ],
    MusicGenre.ELECTRONIC: [
        ["i", "bVI", "bVII", "i"],  # Am - F - G - Am
        ["i", "v", "bVI", "bVII"],
    ],
}

# BPM ranges by genre
GENRE_BPM_RANGES = {
    MusicGenre.POP: (100, 130),
    MusicGenre.ROCK: (110, 140),
    MusicGenre.HIPHOP: (80, 110),
    MusicGenre.ELECTRONIC: (120, 140),
    MusicGenre.JAZZ: (100, 160),
    MusicGenre.CLASSICAL: (60, 120),
    MusicGenre.COUNTRY: (90, 120),
    MusicGenre.RNB: (70, 110),
    MusicGenre.METAL: (140, 200),
    MusicGenre.AMBIENT: (60, 90),
}

# Default instruments by genre
GENRE_INSTRUMENTS = {
    MusicGenre.POP: [
        InstrumentType.PIANO,
        InstrumentType.GUITAR,
        InstrumentType.BASS,
        InstrumentType.DRUMS,
        InstrumentType.SYNTH,
    ],
    MusicGenre.ROCK: [
        InstrumentType.GUITAR,
        InstrumentType.BASS,
        InstrumentType.DRUMS,
    ],
    MusicGenre.ELECTRONIC: [
        InstrumentType.SYNTH,
        InstrumentType.BASS,
        InstrumentType.DRUMS,
    ],
    MusicGenre.JAZZ: [
        InstrumentType.PIANO,
        InstrumentType.BASS,
        InstrumentType.DRUMS,
        InstrumentType.BRASS,
    ],
    MusicGenre.CLASSICAL: [
        InstrumentType.PIANO,
        InstrumentType.STRINGS,
    ],
}

# Global music config instance
music_config = MusicGenerationConfig()


def get_music_config() -> MusicGenerationConfig:
    """Get music generation configuration."""
    return music_config


def get_genre_bpm_range(genre: MusicGenre) -> tuple[int, int]:
    """
    Get typical BPM range for a genre.

    Args:
        genre: Music genre

    Returns:
        Tuple of (min_bpm, max_bpm)
    """
    return GENRE_BPM_RANGES.get(genre, (100, 130))


def get_genre_chord_progressions(genre: MusicGenre) -> list[list[str]]:
    """
    Get common chord progressions for a genre.

    Args:
        genre: Music genre

    Returns:
        List of chord progressions
    """
    return GENRE_CHORD_PROGRESSIONS.get(genre, GENRE_CHORD_PROGRESSIONS[MusicGenre.POP])


def get_genre_instruments(genre: MusicGenre) -> list[InstrumentType]:
    """
    Get typical instruments for a genre.

    Args:
        genre: Music genre

    Returns:
        List of instrument types
    """
    return GENRE_INSTRUMENTS.get(genre, GENRE_INSTRUMENTS[MusicGenre.POP])
