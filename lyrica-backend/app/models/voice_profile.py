"""
Voice profile model for text-to-speech voices.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class VoiceProfile(Base):
    """Available voice profiles for song vocals."""

    __tablename__ = "voice_profiles"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Profile information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    voice_model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Voice characteristics
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    age_range: Mapped[Optional[str]] = mapped_column(String(50))
    accent: Mapped[Optional[str]] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(10), default="en", index=True)

    # Technical parameters
    base_pitch_hz: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    pitch_range: Mapped[Optional[dict]] = mapped_column(JSON)
    timbre_profile: Mapped[Optional[dict]] = mapped_column(JSON)
    model_parameters: Mapped[dict] = mapped_column(JSON, default=dict)

    # Sample audio
    sample_audio_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id")
    )

    # Availability
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # Rating
    average_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # sample_audio_file = relationship("AudioFile", back_populates="voice_profiles")
    # songs = relationship("Song", back_populates="voice_profile")

    def __repr__(self) -> str:
        return f"<VoiceProfile(id={self.id}, name='{self.name}', language={self.language})>"
