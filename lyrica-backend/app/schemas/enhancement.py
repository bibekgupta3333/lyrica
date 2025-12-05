"""
Schemas for voice and mixing enhancement API endpoints.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EnhancementConfig(BaseModel):
    """Unified configuration for voice and mixing enhancement."""

    # Voice Enhancement
    enable_voice_enhancement: bool = Field(default=True, description="Enable voice enhancement")
    enable_prosody_enhancement: bool = Field(
        default=True, description="Enable prosody (rhythm, stress) enhancement"
    )
    enable_auto_tune: bool = Field(default=False, description="Enable auto-tune")
    target_key: Optional[str] = Field(None, description="Target musical key for auto-tune")

    # Mixing Enhancement
    enable_intelligent_mixing: bool = Field(
        default=True, description="Enable intelligent frequency balancing"
    )
    enable_stereo_imaging: bool = Field(default=True, description="Enable stereo imaging")
    enable_genre_specific_mixing: bool = Field(
        default=True, description="Enable genre-specific mixing presets"
    )
    use_reference_track: bool = Field(default=False, description="Use reference track for matching")
    reference_track_id: Optional[UUID] = Field(None, description="Reference track ID")

    # Memory & Learning
    enable_memory_learning: bool = Field(
        default=True, description="Enable memory-based learning and optimization"
    )
    mixing_config_id: Optional[UUID] = Field(
        None, description="Specific mixing configuration ID to use"
    )

    # Quality Tracking
    track_quality_metrics: bool = Field(
        default=True, description="Track quality metrics for learning"
    )


class VoiceEnhancementRequest(BaseModel):
    """Request for voice enhancement only."""

    audio_path: str = Field(..., description="Path to audio file to enhance")
    enable_neural_vocoder: bool = Field(default=True, description="Use neural vocoder if available")
    enable_prosody: bool = Field(default=True, description="Enable prosody enhancement")
    enable_auto_tune: bool = Field(default=False, description="Enable auto-tune")
    target_key: Optional[str] = Field(None, description="Target key for auto-tune")


class MixingEnhancementRequest(BaseModel):
    """Request for mixing enhancement only."""

    vocals_path: str = Field(..., description="Path to vocals audio file")
    music_path: str = Field(..., description="Path to music audio file")
    genre: str = Field(..., description="Music genre")
    enable_frequency_balancing: bool = Field(default=True, description="Enable frequency balancing")
    enable_sidechain: bool = Field(default=True, description="Enable sidechain compression")
    enable_stereo_imaging: bool = Field(default=True, description="Enable stereo imaging")
    mixing_config_id: Optional[UUID] = Field(None, description="Specific mixing configuration ID")


class CompleteEnhancementRequest(BaseModel):
    """Request for complete song enhancement."""

    song_id: UUID = Field(..., description="Song ID to enhance")
    enhancement_config: EnhancementConfig = Field(
        default_factory=EnhancementConfig, description="Enhancement configuration"
    )


class EnhancementResponse(BaseModel):
    """Response from enhancement operations."""

    success: bool = Field(..., description="Whether enhancement succeeded")
    enhanced_audio_path: Optional[str] = Field(None, description="Path to enhanced audio")
    quality_metrics: dict = Field(default_factory=dict, description="Quality metrics")
    enhancement_applied: list[str] = Field(
        default_factory=list, description="List of enhancements applied"
    )
    warnings: list[str] = Field(default_factory=list, description="Warnings")
    errors: list[str] = Field(default_factory=list, description="Errors")
