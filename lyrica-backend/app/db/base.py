"""
Database base configuration.
Imports all models for Alembic migrations.
"""

from app.db.base_class import Base

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.lyrics import Lyrics, LyricsSection
from app.models.generation import GenerationHistory, AgentLog
from app.models.feedback import UserFeedback
from app.models.document import Document

__all__ = [
    "Base",
    "User",
    "Lyrics",
    "LyricsSection",
    "GenerationHistory",
    "AgentLog",
    "UserFeedback",
    "Document",
]
