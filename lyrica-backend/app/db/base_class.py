"""
Base class for SQLAlchemy models.
"""

from datetime import datetime
from typing import Any
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Generate __tablename__ automatically from class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_') + 's'
    
    # Common columns for all models
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

