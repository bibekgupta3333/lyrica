"""
Database base configuration.
Imports all models for Alembic migrations.
"""

from app.db.base_class import Base
from app.models.document import Document
from app.models.feedback import UserFeedback
from app.models.generation import AgentLog, GenerationHistory
from app.models.lyrics import Lyrics, LyricsSection
from app.models.mixing_config import AudioFeatureVector, MixingConfiguration, ReferenceTrack
from app.models.mixing_feedback import MixingFeedback, QualityMetricHistory

# Import all models here so Alembic can detect them
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Lyrics",
    "LyricsSection",
    "GenerationHistory",
    "AgentLog",
    "UserFeedback",
    "Document",
    "MixingConfiguration",
    "ReferenceTrack",
    "AudioFeatureVector",
    "MixingFeedback",
    "QualityMetricHistory",
]
