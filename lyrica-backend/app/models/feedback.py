"""
User feedback model.
"""

import uuid
from typing import Optional

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserFeedback(Base):
    """User feedback and ratings for generated lyrics."""

    __tablename__ = "user_feedback"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    lyrics_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lyrics.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Ratings (1-5)
    overall_rating: Mapped[Optional[int]] = mapped_column(Integer)
    creativity_rating: Mapped[Optional[int]] = mapped_column(Integer)
    relevance_rating: Mapped[Optional[int]] = mapped_column(Integer)
    quality_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Feedback
    comment: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Actions
    is_liked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    # user = relationship("User", back_populates="feedback")
    # lyrics = relationship("Lyrics", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<UserFeedback(id={self.id}, rating={self.overall_rating})>"
