"""Database models package."""

# Import all models here so Alembic can discover them
from app.models.api_key import APIKey
from app.models.audio_file import AudioFile
from app.models.document import Document
from app.models.feedback import UserFeedback
from app.models.generation import AgentLog, GenerationHistory
from app.models.lyrics import Lyrics, LyricsSection
from app.models.mixing_config import AudioFeatureVector, MixingConfiguration, ReferenceTrack
from app.models.mixing_feedback import MixingFeedback, QualityMetricHistory
from app.models.music_track import MusicTrack
from app.models.song import Song
from app.models.song_generation_history import SongGenerationHistory
from app.models.usage_statistic import UsageStatistic
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.voice_profile import VoiceProfile

__all__ = [
    # User models
    "User",
    "UserPreference",
    "APIKey",
    # Lyrics models
    "Lyrics",
    "LyricsSection",
    # Generation models
    "GenerationHistory",
    "AgentLog",
    # Feedback
    "UserFeedback",
    # RAG
    "Document",
    # Song generation models
    "Song",
    "AudioFile",
    "VoiceProfile",
    "MusicTrack",
    "SongGenerationHistory",
    # Mixing & Memory models
    "MixingConfiguration",
    "ReferenceTrack",
    "AudioFeatureVector",
    "MixingFeedback",
    "QualityMetricHistory",
    # Statistics
    "UsageStatistic",
]
