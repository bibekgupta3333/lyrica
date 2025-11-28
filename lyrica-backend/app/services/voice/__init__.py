"""
Voice synthesis and manipulation services.

This package provides comprehensive voice synthesis capabilities including:
- Text-to-speech (TTS)
- Pitch adjustment
- Tempo control
- Vocal effects
- Voice profile management
"""

from app.services.voice.effects import VocalEffectsService, get_vocal_effects
from app.services.voice.pitch_control import PitchControlService, get_pitch_control
from app.services.voice.synthesis import VoiceSynthesisService, get_voice_synthesis

__all__ = [
    "VoiceSynthesisService",
    "PitchControlService",
    "VocalEffectsService",
    "get_voice_synthesis",
    "get_pitch_control",
    "get_vocal_effects",
]
