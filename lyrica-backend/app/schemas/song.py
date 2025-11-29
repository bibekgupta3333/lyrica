"""
Pydantic schemas for Song API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# ============================================================================
# Song Generation Request Schemas
# ============================================================================


class CompleteSongGenerationRequest(BaseModel):
    """Request to generate a complete song from scratch."""

    # Lyrics parameters
    lyrics_prompt: str = Field(..., min_length=10, max_length=500, description="Song prompt")
    genre: Optional[str] = Field(None, description="Music genre (pop, rock, etc.)")
    mood: Optional[str] = Field(None, description="Song mood (happy, sad, energetic, etc.)")
    theme: Optional[str] = Field(None, description="Song theme")

    # Song metadata
    title: Optional[str] = Field(None, max_length=255, description="Song title")
    artist_name: Optional[str] = Field(None, max_length=255, description="Artist name")

    # Voice parameters
    voice_profile_id: str = Field(..., description="Voice profile to use")
    vocal_pitch_shift: int = Field(default=0, ge=-12, le=12, description="Pitch shift in semitones")
    vocal_effects: dict = Field(default_factory=dict, description="Vocal effects settings")

    # Music parameters
    bpm: Optional[int] = Field(None, ge=40, le=200, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key (C major, D minor, etc.)")
    music_style: Optional[str] = Field(None, description="Music style")
    duration_seconds: int = Field(default=180, ge=30, le=600, description="Song duration")

    # Generation options
    use_rag: bool = Field(default=True, description="Use RAG for lyrics")
    llm_provider: Optional[str] = Field(None, description="LLM provider (ollama, openai, etc.)")
    is_public: bool = Field(default=False, description="Make song public")


class SongFromLyricsRequest(BaseModel):
    """Request to generate song from existing lyrics."""

    lyrics_id: UUID = Field(..., description="Existing lyrics ID")

    # Song metadata
    title: Optional[str] = Field(None, max_length=255)
    artist_name: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None)
    mood: Optional[str] = Field(None)

    # Voice parameters
    voice_profile_id: str = Field(..., description="Voice profile")
    vocal_pitch_shift: int = Field(default=0, ge=-12, le=12)
    vocal_effects: dict = Field(default_factory=dict)

    # Music parameters
    bpm: Optional[int] = Field(None, ge=40, le=200)
    key: Optional[str] = Field(None)
    music_style: Optional[str] = Field(None)
    duration_seconds: int = Field(default=180, ge=30, le=600)

    is_public: bool = Field(default=False)


class RegenerateVocalsRequest(BaseModel):
    """Request to regenerate vocals for existing song."""

    voice_profile_id: Optional[str] = Field(
        None, description="New voice profile (keep same if None)"
    )
    vocal_pitch_shift: Optional[int] = Field(None, ge=-12, le=12, description="New pitch")
    vocal_effects: Optional[dict] = Field(None, description="New vocal effects")


class RegenerateMusicRequest(BaseModel):
    """Request to regenerate music for existing song."""

    genre: Optional[str] = Field(None, description="New genre")
    bpm: Optional[int] = Field(None, ge=40, le=200, description="New BPM")
    key: Optional[str] = Field(None, description="New key")
    music_style: Optional[str] = Field(None, description="New style")


class RemixSongRequest(BaseModel):
    """Request to remix existing song with new settings."""

    # Optional new vocals
    voice_profile_id: Optional[str] = None
    vocal_pitch_shift: Optional[int] = Field(None, ge=-12, le=12)
    vocal_effects: Optional[dict] = None

    # Optional new music
    genre: Optional[str] = None
    bpm: Optional[int] = Field(None, ge=40, le=200)
    key: Optional[str] = None
    music_style: Optional[str] = None

    # Mixing settings
    vocals_volume_db: float = Field(default=0.0, ge=-20.0, le=10.0)
    music_volume_db: float = Field(default=-5.0, ge=-30.0, le=0.0)


class UpdateSongSettingsRequest(BaseModel):
    """Request to update song settings."""

    title: Optional[str] = Field(None, max_length=255)
    artist_name: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    mood: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    vocal_pitch_shift: Optional[int] = Field(None, ge=-12, le=12)
    vocal_effects: Optional[dict] = None
    music_params: Optional[dict] = None


# ============================================================================
# Response Schemas
# ============================================================================


class SongFileInfo(BaseModel):
    """Information about song audio files."""

    final_audio_path: Optional[str] = None
    vocal_track_path: Optional[str] = None
    instrumental_track_path: Optional[str] = None
    preview_path: Optional[str] = None

    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None


class SongQualityMetrics(BaseModel):
    """Song quality metrics."""

    audio_quality_score: Optional[float] = None
    mixing_quality_score: Optional[float] = None
    overall_rating: Optional[float] = None
    loudness_lufs: Optional[float] = None
    dynamic_range_db: Optional[float] = None


class SongStatistics(BaseModel):
    """Song engagement statistics."""

    play_count: int = 0
    download_count: int = 0
    share_count: int = 0
    like_count: int = 0


class SongResponse(BaseModel):
    """Complete song response."""

    # Basic info
    id: UUID
    user_id: UUID
    lyrics_id: Optional[UUID] = None

    # Metadata
    title: str
    artist_name: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    duration_seconds: Optional[float] = None

    # Generation settings
    voice_profile_id: Optional[UUID] = None
    music_style: Optional[str] = None
    vocal_pitch_shift: int = 0
    vocal_effects: dict = Field(default_factory=dict)
    music_params: dict = Field(default_factory=dict)

    # File references
    final_audio_file_id: Optional[UUID] = None
    vocal_track_file_id: Optional[UUID] = None
    instrumental_track_file_id: Optional[UUID] = None

    # File info
    file_info: Optional[SongFileInfo] = None

    # Quality metrics
    quality_metrics: Optional[SongQualityMetrics] = None

    # Statistics
    statistics: SongStatistics

    # Status
    generation_status: str
    is_public: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SongGenerationProgressResponse(BaseModel):
    """Response for song generation progress."""

    song_id: UUID
    status: str
    current_stage: Optional[str] = None
    progress_percentage: int = 0
    estimated_time_remaining_seconds: Optional[float] = None
    message: Optional[str] = None


class SongListResponse(BaseModel):
    """Response for list of songs."""

    songs: List[SongResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GenerationHistoryResponse(BaseModel):
    """Response for song generation history."""

    id: UUID
    song_id: Optional[UUID]
    lyrics_id: Optional[UUID]

    generation_type: str
    input_params: dict

    status: str
    current_stage: Optional[str]
    progress_percentage: int
    agent_steps: List[dict]

    # Performance metrics
    total_time_seconds: Optional[float]
    vocal_generation_time: Optional[float]
    music_generation_time: Optional[float]
    mixing_time: Optional[float]

    # Error info
    error_message: Optional[str]
    retry_count: int

    # Timestamps
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Quick Generation Schemas (Simplified)
# ============================================================================


class QuickSongRequest(BaseModel):
    """Quick song generation with minimal parameters."""

    prompt: str = Field(..., min_length=10, max_length=200, description="What song to create")
    voice: str = Field(default="female_singer_1", description="Voice profile")
    genre: Optional[str] = Field(default="pop", description="Genre")
    duration: int = Field(default=120, ge=30, le=300, description="Duration in seconds")


class VoiceProfileInfo(BaseModel):
    """Voice profile information."""

    id: str
    name: str
    gender: str
    language: str
    description: Optional[str] = None
    style: Optional[str] = None


class MusicGenreInfo(BaseModel):
    """Music genre information."""

    id: str
    name: str
    description: str
    typical_bpm_range: str
    common_keys: List[str]
    typical_instruments: List[str]
