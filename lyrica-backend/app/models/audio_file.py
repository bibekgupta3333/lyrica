"""
Audio file model for storing song audio files.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AudioFile(Base):
    """Audio file storage and metadata."""

    __tablename__ = "audio_files"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # File information
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_format: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Audio properties
    duration_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer)
    bit_rate: Mapped[Optional[int]] = mapped_column(Integer)
    channels: Mapped[int] = mapped_column(Integer, default=2)

    # Metadata
    audio_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    waveform_data: Mapped[Optional[dict]] = mapped_column(JSON)
    file_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Storage
    storage_provider: Mapped[str] = mapped_column(String(50), default="s3")
    cdn_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    # user = relationship("User", back_populates="audio_files")

    def __repr__(self) -> str:
        return f"<AudioFile(id={self.id}, type={self.audio_type}, name='{self.file_name}')>"
