"""
Song model for complete song generation.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Song(Base):
    """Main song entity with vocals and music."""

    __tablename__ = "songs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    lyrics_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lyrics.id", ondelete="SET NULL"), index=True
    )

    # Song metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist_name: Mapped[Optional[str]] = mapped_column(String(255))
    genre: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    mood: Mapped[Optional[str]] = mapped_column(String(100))
    bpm: Mapped[Optional[int]] = mapped_column(Integer)
    key: Mapped[Optional[str]] = mapped_column(String(10))
    duration_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Generation settings
    voice_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voice_profiles.id")
    )
    music_style: Mapped[Optional[str]] = mapped_column(String(100))
    vocal_pitch_shift: Mapped[int] = mapped_column(Integer, default=0)
    vocal_effects: Mapped[dict] = mapped_column(JSON, default=dict)
    music_params: Mapped[dict] = mapped_column(JSON, default=dict)

    # File references
    final_audio_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id")
    )
    vocal_track_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id")
    )
    instrumental_track_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id")
    )

    # Quality metrics
    audio_quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    mixing_quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    overall_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))

    # Statistics
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    generation_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    # user = relationship("User", back_populates="songs")
    # lyrics = relationship("Lyrics", back_populates="songs")
    # voice_profile = relationship("VoiceProfile", back_populates="songs")
    # final_audio_file = relationship("AudioFile", foreign_keys=[final_audio_file_id])
    # vocal_track_file = relationship("AudioFile", foreign_keys=[vocal_track_file_id])
    # instrumental_track_file = relationship("AudioFile", foreign_keys=[instrumental_track_file_id])
    # music_tracks = relationship("MusicTrack", back_populates="song", cascade="all, delete-orphan")
    # generation_history = relationship("SongGenerationHistory", back_populates="song")

    def __repr__(self) -> str:
        return f"<Song(id={self.id}, title='{self.title}', status={self.generation_status})>"
