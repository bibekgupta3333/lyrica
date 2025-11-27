"""
Document model for RAG system.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Document(Base):
    """Documents for RAG (Retrieval-Augmented Generation) system."""

    __tablename__ = "documents"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Content
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    genre: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    mood: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    album: Mapped[Optional[str]] = mapped_column(String(255))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Categorization
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    custom_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Vector store reference
    chromadb_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    # Status
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title}, genre={self.genre})>"
