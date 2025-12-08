"""
Music generation and composition services.

This package provides comprehensive music generation capabilities including:
- AI-powered music generation (MusicGen, YuE)
- Chord progression generation
- Melody generation
- Genre-specific composition
- Full-song generation (YuE)
"""

from app.services.music.chords import ChordProgressionService, get_chord_service
from app.services.music.generation import MusicGenerationService, get_music_generation
from app.services.music.melody import MelodyGenerationService, get_melody_service
from app.services.music.structure import MusicStructureService, get_music_structure
from app.services.music.yue_generation import YueGenerationService, get_yue_generation

__all__ = [
    "MusicGenerationService",
    "ChordProgressionService",
    "MelodyGenerationService",
    "YueGenerationService",
    "MusicStructureService",
    "get_music_generation",
    "get_chord_service",
    "get_melody_service",
    "get_yue_generation",
    "get_music_structure",
]
