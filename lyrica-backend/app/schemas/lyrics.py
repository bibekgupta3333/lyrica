"""
Lyrics schemas for API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


# Lyrics Section Schemas
class LyricsSectionBase(BaseModel):
    """Base lyrics section schema."""

    section_type: str = Field(..., description="Type of section (verse, chorus, bridge, etc.)")
    section_order: int = Field(..., ge=0, description="Order of the section")
    content: str = Field(..., min_length=1, description="Section content")
    rhyme_scheme: Optional[str] = Field(None, description="Rhyme scheme (e.g., ABAB)")
    line_count: Optional[int] = Field(None, ge=1, description="Number of lines")


class LyricsSectionCreate(LyricsSectionBase):
    """Lyrics section creation schema."""

    pass


class LyricsSection(LyricsSectionBase):
    """Lyrics section response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lyrics_id: uuid.UUID
    generation_attempts: int
    refinement_count: int
    created_at: datetime
    updated_at: datetime


# Lyrics Schemas
class LyricsBase(BaseModel):
    """Base lyrics schema."""

    title: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)
    structure: Dict[str, Any] = Field(..., description="Song structure")
    genre: Optional[str] = Field(None, max_length=100)
    mood: Optional[str] = Field(None, max_length=100)
    theme: Optional[str] = Field(None, max_length=255)
    language: str = Field(default="en", max_length=10)


class LyricsCreate(LyricsBase):
    """Lyrics creation schema."""

    prompt: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LyricsUpdate(BaseModel):
    """Lyrics update schema."""

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    status: Optional[str] = None
    is_public: Optional[bool] = None


class Lyrics(LyricsBase):
    """Lyrics response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    prompt: Optional[str] = None
    generation_params: Dict[str, Any]
    model_used: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    quality_score: Optional[float] = None
    rhyme_score: Optional[float] = None
    creativity_score: Optional[float] = None
    coherence_score: Optional[float] = None
    status: str
    is_public: bool
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime


class LyricsWithSections(Lyrics):
    """Lyrics with sections response schema."""

    sections: list[LyricsSection] = []
