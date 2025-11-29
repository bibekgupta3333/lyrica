"""
Music generation and composition services.

This package provides comprehensive music generation capabilities including:
- AI-powered music generation (MusicGen)
- Chord progression generation
- Melody generation
- Genre-specific composition
"""

from app.services.music.chords import ChordProgressionService, get_chord_service
from app.services.music.generation import MusicGenerationService, get_music_generation
from app.services.music.melody import MelodyGenerationService, get_melody_service

__all__ = [
    "MusicGenerationService",
    "ChordProgressionService",
    "MelodyGenerationService",
    "get_music_generation",
    "get_chord_service",
    "get_melody_service",
]
