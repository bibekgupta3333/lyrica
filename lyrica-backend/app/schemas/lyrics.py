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

    section_type: str = Field(
        ...,
        description="Type of section: 'verse', 'chorus', 'bridge', 'intro', 'outro', etc.",
    )
    section_order: int = Field(
        ..., ge=0, description="Order/position of the section in the song (1-based)"
    )
    content: str = Field(..., min_length=1, description="Section lyrics content")
    rhyme_scheme: Optional[str] = Field(
        None, description="Rhyme scheme pattern (e.g., 'ABAB', 'AABB', 'ABCB')"
    )
    line_count: Optional[int] = Field(None, ge=1, description="Number of lines in the section")


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

    title: Optional[str] = Field(
        None, max_length=255, description="Song title (optional, can be auto-generated)"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Full lyrics content with section markers like [VERSE], [CHORUS]",
    )
    structure: Dict[str, Any] = Field(
        ...,
        description="Song structure definition (sections, counts, lengths, moods)",
    )
    genre: Optional[str] = Field(
        None, max_length=100, description="Music genre (pop, rock, hip-hop, etc.)"
    )
    mood: Optional[str] = Field(
        None, max_length=100, description="Mood/emotion (happy, sad, energetic, etc.)"
    )
    theme: Optional[str] = Field(
        None, max_length=255, description="Song theme or topic (love, freedom, etc.)"
    )
    language: str = Field(
        default="en", max_length=10, description="Language code (ISO 639-1, e.g., 'en', 'es')"
    )


class LyricsCreate(LyricsBase):
    """Lyrics creation schema."""

    prompt: Optional[str] = Field(
        None,
        description="Generation prompt (if not provided, built from genre/mood/theme)",
    )
    generation_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional generation parameters (temperature, max_length, etc.)",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "title": "Summer Dreams",
                    "content": "[Verse 1]\nWalking down the beach at sunset\nYour hand in mine feels so right\n[Chorus]\nSummer dreams and ocean breeze\nWith you is where I want to be",
                    "structure": {
                        "sections": [
                            {"type": "verse", "count": 2},
                            {"type": "chorus", "count": 2},
                            {"type": "bridge", "count": 1},
                        ]
                    },
                    "genre": "pop",
                    "mood": "happy",
                    "theme": "love",
                    "language": "en",
                    "prompt": "Write a happy pop song about summer love",
                    "generation_params": {"temperature": 0.8, "max_length": 500},
                }
            ]
        }


class LyricsUpdate(BaseModel):
    """Lyrics update schema."""

    title: Optional[str] = Field(None, max_length=255, description="Updated song title")
    content: Optional[str] = Field(
        None, description="Updated lyrics content (with section markers)"
    )
    status: Optional[str] = Field(None, description="Status: 'draft', 'published', or 'archived'")
    is_public: Optional[bool] = Field(None, description="Whether lyrics are publicly visible")

    class Config:
        json_schema_extra = {
            "examples": [
                {"title": "My Awesome Song (Remix)"},
                {
                    "content": "[Verse 1]\nUpdated first verse\nWith new amazing lyrics\n[Chorus]\nThis is the updated chorus"
                },
                {"status": "published", "is_public": True},
                {"is_public": False},
            ]
        }


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
