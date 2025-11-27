"""
Song generation history model for tracking production process.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class SongGenerationHistory(Base):
    """Track complete song generation process from lyrics to final audio."""

    __tablename__ = "song_generation_history"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    song_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="SET NULL"), index=True
    )

    lyrics_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lyrics.id", ondelete="SET NULL"), index=True
    )

    # Generation parameters
    generation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    input_params: Mapped[dict] = mapped_column(JSON, nullable=False)
    voice_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voice_profiles.id")
    )

    # Process tracking
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    current_stage: Mapped[Optional[str]] = mapped_column(String(100))
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    agent_steps: Mapped[list] = mapped_column(JSON, default=list)

    # Performance metrics
    total_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    vocal_generation_time: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    music_generation_time: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    mixing_time: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    # user = relationship("User", back_populates="song_generation_history")
    # song = relationship("Song", back_populates="generation_history")
    # lyrics = relationship("Lyrics")
    # voice_profile = relationship("VoiceProfile")

    def __repr__(self) -> str:
        return f"<SongGenerationHistory(id={self.id}, status={self.status}, progress={self.progress_percentage}%)>"
