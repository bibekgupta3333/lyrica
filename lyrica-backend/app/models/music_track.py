"""
Music track model for multi-track composition.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MusicTrack(Base):
    """Individual track in a multi-track song composition."""

    __tablename__ = "music_tracks"
    __table_args__ = (UniqueConstraint("song_id", "track_order", name="unique_track_order"),)

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    audio_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id")
    )

    # Track information
    track_name: Mapped[Optional[str]] = mapped_column(String(255))
    track_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    track_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Track properties
    volume: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    pan: Mapped[float] = mapped_column(Numeric(3, 2), default=0.0)
    eq_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    effects: Mapped[list] = mapped_column(JSON, default=list)

    # Timing
    start_time_seconds: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    end_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    fade_in_seconds: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    fade_out_seconds: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)

    # Status
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_solo: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # song = relationship("Song", back_populates="music_tracks")
    # audio_file = relationship("AudioFile", back_populates="music_tracks")

    def __repr__(self) -> str:
        return f"<MusicTrack(id={self.id}, type={self.track_type}, order={self.track_order})>"
