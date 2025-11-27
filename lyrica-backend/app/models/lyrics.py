"""
Lyrics models.
"""

import uuid
from typing import Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Lyrics(Base):
    """Lyrics model for storing generated song lyrics."""

    __tablename__ = "lyrics"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Content
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structure: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Metadata
    genre: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    mood: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    theme: Mapped[Optional[str]] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Generation metadata
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    generation_params: Mapped[dict] = mapped_column(JSON, default=dict)
    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    rhyme_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    creativity_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    coherence_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    # user = relationship("User", back_populates="lyrics")
    # sections = relationship("LyricsSection", back_populates="lyrics", cascade="all, delete-orphan")
    # feedback = relationship("UserFeedback", back_populates="lyrics")

    def __repr__(self) -> str:
        return f"<Lyrics(id={self.id}, title={self.title}, genre={self.genre})>"


class LyricsSection(Base):
    """Individual sections of lyrics (verse, chorus, bridge, etc.)."""

    __tablename__ = "lyrics_sections"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    lyrics_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lyrics.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Content
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rhyme_scheme: Mapped[Optional[str]] = mapped_column(String(50))
    line_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Metadata
    generation_attempts: Mapped[int] = mapped_column(Integer, default=1)
    refinement_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    # lyrics = relationship("Lyrics", back_populates="sections")

    def __repr__(self) -> str:
        return (
            f"<LyricsSection(id={self.id}, type={self.section_type}, order={self.section_order})>"
        )
