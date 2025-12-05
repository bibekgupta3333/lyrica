"""
Mixing configuration models for memory system.

Stores mixing configurations, genre presets, and reference track analyses.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class MixingConfiguration(Base):
    """Stores mixing configurations for songs."""

    __tablename__ = "mixing_configurations"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    song_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), index=True
    )

    # Configuration Type
    config_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'manual', 'genre_preset', 'reference_match'

    # Genre (if applicable)
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)

    # Mixing Settings
    eq_settings: Mapped[dict] = mapped_column(JSON, default=dict)  # EQ bands for vocals/music
    compression_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    stereo_width_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    reverb_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    delay_settings: Mapped[dict] = mapped_column(JSON, default=dict)
    sidechain_settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metadata
    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Usage Statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<MixingConfiguration(id={self.id}, type={self.config_type}, genre={self.genre})>"


class ReferenceTrack(Base):
    """Stores reference track analyses."""

    __tablename__ = "reference_tracks"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    # Track Information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    album: Mapped[Optional[str]] = mapped_column(String(255))
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)

    # Audio File Reference
    audio_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audio_files.id", ondelete="SET NULL")
    )

    # Analysis Results
    frequency_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    stereo_width_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    dynamic_range: Mapped[Optional[float]] = mapped_column(Float)
    avg_loudness: Mapped[Optional[float]] = mapped_column(Float)
    eq_profile: Mapped[dict] = mapped_column(JSON, default=dict)

    # Recommendations
    recommendations: Mapped[list[dict]] = mapped_column(ARRAY(JSON), default=list)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<ReferenceTrack(id={self.id}, title={self.title}, artist={self.artist})>"


class AudioFeatureVector(Base):
    """Stores audio feature vectors for similarity search."""

    __tablename__ = "audio_feature_vectors"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    audio_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audio_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reference_track_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reference_tracks.id", ondelete="CASCADE")
    )

    # Vector Storage
    chromadb_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    vector_dimension: Mapped[int] = mapped_column(Integer, nullable=False)

    # Feature Metadata
    feature_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'frequency', 'spectral', 'rhythm', 'full'

    # Extracted Features
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    spectral_centroid: Mapped[Optional[float]] = mapped_column(Float)
    spectral_rolloff: Mapped[Optional[float]] = mapped_column(Float)
    zero_crossing_rate: Mapped[Optional[float]] = mapped_column(Float)
    mfcc_features: Mapped[list[float]] = mapped_column(ARRAY(Float), default=list)
    frequency_bands: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metadata
    sample_rate: Mapped[int] = mapped_column(Integer, default=22050)
    duration: Mapped[Optional[float]] = mapped_column(Float)

    def __repr__(self) -> str:
        return (
            f"<AudioFeatureVector(id={self.id}, type={self.feature_type}, "
            f"chromadb_id={self.chromadb_id})>"
        )
