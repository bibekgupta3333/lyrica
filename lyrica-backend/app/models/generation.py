"""
Generation history and agent logs models.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class GenerationHistory(Base):
    """Track lyrics generation history and process."""

    __tablename__ = "generation_history"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    lyrics_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lyrics.id", ondelete="SET NULL")
    )

    # Input parameters
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    mood: Mapped[Optional[str]] = mapped_column(String(100))
    theme: Mapped[Optional[str]] = mapped_column(String(255))
    custom_structure: Mapped[Optional[dict]] = mapped_column(JSON)

    # Process metadata
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    agent_steps: Mapped[list] = mapped_column(JSON, default=list)
    iterations: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Performance metrics
    total_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    llm_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    retrieval_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    # user = relationship("User", back_populates="generation_history")
    # lyrics = relationship("Lyrics")
    # agent_logs = relationship("AgentLog", back_populates="generation_history", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<GenerationHistory(id={self.id}, status={self.status})>"


class AgentLog(Base):
    """Detailed logs for each agent execution step."""

    __tablename__ = "agent_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Foreign Keys
    generation_history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generation_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Agent info
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Input/Output
    input_state: Mapped[Optional[dict]] = mapped_column(JSON)
    output_state: Mapped[Optional[dict]] = mapped_column(JSON)

    # Metadata
    execution_time_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    model_used: Mapped[Optional[str]] = mapped_column(String(100))

    # Status
    status: Mapped[str] = mapped_column(String(50), default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    # generation_history = relationship("GenerationHistory", back_populates="agent_logs")

    def __repr__(self) -> str:
        return f"<AgentLog(id={self.id}, agent={self.agent_name}, step={self.step_number})>"
