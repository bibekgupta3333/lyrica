"""
Voice synthesis and manipulation services.

This package provides comprehensive voice synthesis capabilities including:
- Text-to-speech (TTS)
- Voice enhancement (neural vocoders)
- Prosody and pitch enhancement (CREPE, auto-tune, formant shifting)
- Quality metrics (PESQ, STOI, MOS)
- Evaluation and A/B testing
- Pitch adjustment
- Tempo control
- Vocal effects
- Voice profile management
"""

from app.services.voice.effects import VocalEffectsService, get_vocal_effects
from app.services.voice.enhancement import VoiceEnhancementService, get_voice_enhancement
from app.services.voice.evaluation import (
    ABTestingService,
    EvaluationService,
    get_ab_testing,
    get_evaluation,
)
from app.services.voice.pitch_control import PitchControlService, get_pitch_control
from app.services.voice.prosody_pitch import ProsodyPitchService, get_prosody_pitch
from app.services.voice.quality_metrics import QualityMetricsService, get_quality_metrics
from app.services.voice.synthesis import VoiceSynthesisService, get_voice_synthesis

__all__ = [
    "VoiceSynthesisService",
    "VoiceEnhancementService",
    "ProsodyPitchService",
    "QualityMetricsService",
    "EvaluationService",
    "ABTestingService",
    "PitchControlService",
    "VocalEffectsService",
    "get_voice_synthesis",
    "get_voice_enhancement",
    "get_prosody_pitch",
    "get_quality_metrics",
    "get_evaluation",
    "get_ab_testing",
    "get_pitch_control",
    "get_vocal_effects",
]
