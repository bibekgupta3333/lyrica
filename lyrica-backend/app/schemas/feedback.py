"""
Feedback schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackBase(BaseModel):
    """Base feedback schema."""

    overall_rating: Optional[int] = Field(None, ge=1, le=5, description="Overall rating (1-5)")
    creativity_rating: Optional[int] = Field(
        None, ge=1, le=5, description="Creativity rating (1-5)"
    )
    relevance_rating: Optional[int] = Field(None, ge=1, le=5, description="Relevance rating (1-5)")
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Quality rating (1-5)")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")
    tags: list[str] = Field(default_factory=list, description="Feedback tags")
    is_liked: bool = Field(default=False, description="Whether user liked the lyrics")


class FeedbackCreate(FeedbackBase):
    """Feedback creation schema."""

    lyrics_id: UUID = Field(..., description="Related lyrics ID")


class Feedback(FeedbackBase):
    """Feedback response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    lyrics_id: UUID
    is_saved: bool
    is_shared: bool
    created_at: datetime


class FeedbackStats(BaseModel):
    """Feedback statistics response schema."""

    total_feedback: int = Field(..., description="Total number of feedback entries")
    average_rating: float = Field(..., description="Average overall rating")
    rating_distribution: dict[str, int] = Field(
        ..., description="Distribution of overall ratings (1-5)"
    )
    feedback_with_comments: int = Field(..., description="Number of feedback entries with comments")
    recent_feedback_count: int = Field(..., description="Number of feedback in the last 7 days")
