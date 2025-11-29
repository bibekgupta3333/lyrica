"""
Pydantic schemas for Audio Quality API endpoints.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# Validation Schemas
class AudioValidationRequest(BaseModel):
    """Request for audio validation."""

    audio_path: str = Field(..., description="Path to audio file to validate")
    min_duration_seconds: float = Field(default=1.0, ge=0.1, le=3600)
    max_duration_seconds: float = Field(default=600.0, ge=1.0, le=7200)
    min_sample_rate: int = Field(default=16000, ge=8000, le=192000)
    max_file_size_mb: float = Field(default=100.0, ge=1.0, le=1000.0)


class AudioValidationResponse(BaseModel):
    """Response for audio validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: Dict = Field(default_factory=dict)


class QualityScoreResponse(BaseModel):
    """Response for quality score."""

    quality_score: float = Field(..., ge=0.0, le=100.0, description="Quality score 0-100")
    grade: str = Field(..., description="Letter grade (A-F)")
    validation: AudioValidationResponse


# Enhancement Schemas
class NoiseReductionRequest(BaseModel):
    """Request for noise reduction."""

    audio_path: str = Field(..., description="Path to audio file")
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Noise reduction strength")


class CompressionRequest(BaseModel):
    """Request for dynamic range compression."""

    audio_path: str = Field(..., description="Path to audio file")
    threshold_db: float = Field(default=-20.0, ge=-60.0, le=0.0)
    ratio: float = Field(default=4.0, ge=1.0, le=20.0, description="Compression ratio")
    attack_ms: float = Field(default=5.0, ge=0.1, le=100.0)
    release_ms: float = Field(default=100.0, ge=10.0, le=1000.0)


class StereoWideningRequest(BaseModel):
    """Request for stereo widening."""

    audio_path: str = Field(..., description="Path to audio file")
    width: float = Field(default=1.5, ge=0.0, le=3.0, description="Stereo width multiplier")


class EnhancementRequest(BaseModel):
    """Request for audio enhancement."""

    audio_path: str = Field(..., description="Path to audio file")
    reduce_noise: bool = Field(default=True, description="Apply noise reduction")
    compress: bool = Field(default=True, description="Apply compression")
    widen_stereo: bool = Field(default=False, description="Apply stereo widening")
    normalize: bool = Field(default=True, description="Normalize loudness")


class LoudnessNormalizationRequest(BaseModel):
    """Request for loudness normalization."""

    audio_path: str = Field(..., description="Path to audio file")
    target_lufs: float = Field(default=-14.0, ge=-30.0, le=-5.0, description="Target LUFS")


class EnhancementResponse(BaseModel):
    """Response for enhancement operations."""

    success: bool
    output_path: str
    message: str
    processing_time_seconds: Optional[float] = None


# Analysis Schemas
class LoudnessAnalysisResponse(BaseModel):
    """Response for loudness analysis."""

    rms_db: float
    peak_db: float
    true_peak_db: float
    estimated_lufs: float
    crest_factor_db: float
    loudness_range_db: float
    is_clipping: bool
    headroom_db: float


class ClarityAnalysisResponse(BaseModel):
    """Response for clarity analysis."""

    spectral_centroid_hz: float
    spectral_rolloff_hz: float
    spectral_bandwidth_hz: float
    zero_crossing_rate: float
    estimated_snr_db: float
    spectral_contrast_db: float
    clarity_score: float
    quality_grade: str


class SpectralAnalysisResponse(BaseModel):
    """Response for spectral analysis."""

    frequency_band_energy_db: Dict[str, float]
    spectral_flatness: float
    is_tonal: bool
    is_noisy: bool


class PerformanceMetricsResponse(BaseModel):
    """Response for performance metrics."""

    file_size_mb: float
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    bit_depth: int
    estimated_bitrate_kbps: float
    high_frequency_preservation: float
    encoding_quality: str


class OverallQualityResponse(BaseModel):
    """Overall quality assessment."""

    quality_score: float
    grade: str
    loudness_score: float
    clarity_score: float
    spectral_score: float


class ComprehensiveAnalysisResponse(BaseModel):
    """Response for comprehensive analysis."""

    file_path: str
    loudness: LoudnessAnalysisResponse
    clarity: ClarityAnalysisResponse
    spectral: SpectralAnalysisResponse
    performance: PerformanceMetricsResponse
    overall: OverallQualityResponse


# Batch Operations
class BatchValidationRequest(BaseModel):
    """Request for batch validation."""

    audio_paths: List[str] = Field(..., min_items=1, max_items=10)
    min_duration_seconds: float = Field(default=1.0)
    max_duration_seconds: float = Field(default=600.0)


class BatchValidationResponse(BaseModel):
    """Response for batch validation."""

    results: List[AudioValidationResponse]
    summary: Dict = Field(
        default_factory=dict,
        description="Summary statistics (passed, failed, warnings)",
    )


class BatchEnhancementRequest(BaseModel):
    """Request for batch enhancement."""

    audio_paths: List[str] = Field(..., min_items=1, max_items=10)
    reduce_noise: bool = Field(default=True)
    compress: bool = Field(default=True)
    normalize: bool = Field(default=True)


class BatchEnhancementResponse(BaseModel):
    """Response for batch enhancement."""

    results: List[EnhancementResponse]
    total_processed: int
    successful: int
    failed: int
