"""
Mixing feedback model for learning system.

Stores user feedback specifically for mixing configurations and audio quality.
"""

import uuid
from typing import Optional

from sqlalchemy import ARRAY, JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class MixingFeedback(Base):
    """User feedback for mixing configurations and audio quality."""

    __tablename__ = "mixing_feedback"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    song_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), index=True
    )
    mixing_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mixing_configurations.id", ondelete="SET NULL"),
        index=True,
    )

    # Mixing Quality Ratings (1-5)
    overall_mixing_rating: Mapped[Optional[int]] = mapped_column(Integer)
    vocals_clarity_rating: Mapped[Optional[int]] = mapped_column(Integer)
    music_balance_rating: Mapped[Optional[int]] = mapped_column(Integer)
    stereo_width_rating: Mapped[Optional[int]] = mapped_column(Integer)
    eq_quality_rating: Mapped[Optional[int]] = mapped_column(Integer)
    reverb_quality_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Audio Quality Metrics (from automated evaluation)
    pesq_score: Mapped[Optional[float]] = mapped_column(Float)
    stoi_score: Mapped[Optional[float]] = mapped_column(Float)
    mos_score: Mapped[Optional[float]] = mapped_column(Float)
    overall_quality_score: Mapped[Optional[float]] = mapped_column(Float)

    # Feedback
    comment: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    improvement_suggestions: Mapped[dict] = mapped_column(JSON, default=dict)

    # Actions
    is_liked: Mapped[bool] = mapped_column(Boolean, default=False)
    would_use_again: Mapped[bool] = mapped_column(Boolean, default=False)

    # Context
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    mood: Mapped[Optional[str]] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"<MixingFeedback(id={self.id}, rating={self.overall_mixing_rating})>"


class QualityMetricHistory(Base):
    """Tracks quality metrics over time for mixing configurations."""

    __tablename__ = "quality_metric_history"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    mixing_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mixing_configurations.id", ondelete="CASCADE"),
        index=True,
    )
    song_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), index=True
    )

    # Quality Metrics
    pesq_score: Mapped[Optional[float]] = mapped_column(Float)
    stoi_score: Mapped[Optional[float]] = mapped_column(Float)
    mos_score: Mapped[Optional[float]] = mapped_column(Float)
    overall_score: Mapped[Optional[float]] = mapped_column(Float)

    # User Feedback Aggregates
    avg_user_rating: Mapped[Optional[float]] = mapped_column(Float)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0)

    # Context
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=1)

    def __repr__(self) -> str:
        return (
            f"<QualityMetricHistory(id={self.id}, "
            f"overall_score={self.overall_score}, sample_count={self.sample_count})>"
        )
