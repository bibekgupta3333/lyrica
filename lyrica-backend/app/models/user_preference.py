"""
User preferences model.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, JSON, Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserPreference(Base):
    """User preferences and settings."""

    __tablename__ = "user_preferences"
    __table_args__ = (UniqueConstraint("user_id", name="one_preference_per_user"),)

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Preferences
    preferred_genres: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    preferred_moods: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    default_structure: Mapped[dict] = mapped_column(JSON, default=dict)
    language: Mapped[str] = mapped_column(String(10), default="en")
    theme: Mapped[str] = mapped_column(String(20), default="light")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # user = relationship("User", back_populates="preferences", uselist=False)

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"
