"""
Audio Quality & Optimization API Endpoints.

This module implements WBS 2.15 - Audio Quality & Optimization:
- Audio quality validation
- Noise reduction
- Dynamic range compression
- Stereo widening
- Audio analysis (loudness, clarity, spectral)
- Enhancement algorithms
- Performance metrics
"""

import time
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.audio_quality import (
    AudioValidationRequest,
    AudioValidationResponse,
    BatchEnhancementRequest,
    BatchEnhancementResponse,
    BatchValidationRequest,
    BatchValidationResponse,
    ClarityAnalysisResponse,
    ComprehensiveAnalysisResponse,
    CompressionRequest,
    EnhancementRequest,
    EnhancementResponse,
    LoudnessAnalysisResponse,
    LoudnessNormalizationRequest,
    NoiseReductionRequest,
    OverallQualityResponse,
    PerformanceMetricsResponse,
    QualityScoreResponse,
    SpectralAnalysisResponse,
    StereoWideningRequest,
)
from app.services.audio_quality import (
    get_audio_analysis,
    get_audio_enhancement,
    get_audio_validation,
)

router = APIRouter(prefix="/audio-quality", tags=["Audio Quality & Optimization"])


# ============================================================================
# Validation Endpoints
# ============================================================================


@router.post(
    "/validate",
    response_model=AudioValidationResponse,
    summary="Validate audio quality",
    description="Validate audio file against quality standards (WBS 2.15.1)",
)
async def validate_audio(request: AudioValidationRequest):
    """
    Validate audio file for quality issues.

    Checks:
    - Duration within acceptable range
    - Sample rate meets minimum
    - File size within limits
    - Clipping detection
    - Silence detection
    - Dynamic range analysis
    - DC offset check

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/audio-quality/validate" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "audio_path": "audio_files/my_song.wav",
                 "min_duration_seconds": 30,
                 "max_duration_seconds": 300
             }'
        ```
    """
    try:
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        validation_service = get_audio_validation()

        results = validation_service.validate_audio_file(
            audio_path=audio_path,
            min_duration_seconds=request.min_duration_seconds,
            max_duration_seconds=request.max_duration_seconds,
            min_sample_rate=request.min_sample_rate,
            max_file_size_mb=request.max_file_size_mb,
        )

        return AudioValidationResponse(**results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate audio: {str(e)}",
        )


@router.post(
    "/quality-score",
    response_model=QualityScoreResponse,
    summary="Calculate quality score",
    description="Calculate overall audio quality score (0-100)",
)
async def get_quality_score(audio_path: str):
    """Calculate overall quality score for audio file."""
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        validation_service = get_audio_validation()
        result = validation_service.check_quality_score(path)

        return QualityScoreResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating quality score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate quality score: {str(e)}",
        )


@router.post(
    "/validate-batch",
    response_model=BatchValidationResponse,
    summary="Validate multiple audio files",
)
async def validate_audio_batch(request: BatchValidationRequest):
    """Validate multiple audio files."""
    try:
        validation_service = get_audio_validation()
        results = []
        passed = 0
        failed = 0
        warnings_count = 0

        for audio_path_str in request.audio_paths:
            audio_path = Path(audio_path_str)

            if not audio_path.exists():
                results.append(
                    AudioValidationResponse(
                        is_valid=False,
                        errors=[f"File not found: {audio_path_str}"],
                        warnings=[],
                        metrics={},
                    )
                )
                failed += 1
                continue

            validation = validation_service.validate_audio_file(
                audio_path=audio_path,
                min_duration_seconds=request.min_duration_seconds,
                max_duration_seconds=request.max_duration_seconds,
            )

            results.append(AudioValidationResponse(**validation))

            if validation["is_valid"]:
                passed += 1
            else:
                failed += 1

            warnings_count += len(validation.get("warnings", []))

        return BatchValidationResponse(
            results=results,
            summary={
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "total_warnings": warnings_count,
            },
        )

    except Exception as e:
        logger.error(f"Error in batch validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch validation failed: {str(e)}",
        )


# ============================================================================
# Enhancement Endpoints
# ============================================================================


@router.post(
    "/reduce-noise",
    response_model=EnhancementResponse,
    summary="Reduce background noise",
    description="Apply noise reduction to audio file (WBS 2.15.2)",
)
async def reduce_noise(request: NoiseReductionRequest):
    """
    Reduce background noise from audio.

    Uses spectral gating to remove noise while preserving signal quality.

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/audio-quality/reduce-noise" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "audio_path": "audio_files/noisy_recording.wav",
                 "strength": 0.7
             }'
        ```
    """
    try:
        start_time = time.time()
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_audio_enhancement()
        output_path = enhancement_service.reduce_noise(
            audio_path=audio_path,
            noise_reduction_strength=request.strength,
        )

        processing_time = time.time() - start_time

        return EnhancementResponse(
            success=True,
            output_path=str(output_path),
            message=f"Noise reduction applied successfully (strength: {request.strength})",
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reducing noise: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reduce noise: {str(e)}",
        )


@router.post(
    "/compress",
    response_model=EnhancementResponse,
    summary="Apply dynamic range compression",
    description="Compress audio dynamic range (WBS 2.15.3)",
)
async def compress_audio(request: CompressionRequest):
    """
    Apply dynamic range compression to audio.

    Reduces the difference between loud and quiet parts,
    resulting in more consistent loudness.

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/audio-quality/compress" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "audio_path": "audio_files/dynamic_song.wav",
                 "threshold_db": -20,
                 "ratio": 4.0
             }'
        ```
    """
    try:
        start_time = time.time()
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_audio_enhancement()
        output_path = enhancement_service.compress_dynamic_range(
            audio_path=audio_path,
            threshold_db=request.threshold_db,
            ratio=request.ratio,
            attack_ms=request.attack_ms,
            release_ms=request.release_ms,
        )

        processing_time = time.time() - start_time

        return EnhancementResponse(
            success=True,
            output_path=str(output_path),
            message=f"Compression applied (ratio: {request.ratio}:1, threshold: {request.threshold_db}dB)",
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error compressing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compress audio: {str(e)}",
        )


@router.post(
    "/widen-stereo",
    response_model=EnhancementResponse,
    summary="Apply stereo widening",
    description="Widen stereo image (WBS 2.15.4)",
)
async def widen_stereo(request: StereoWideningRequest):
    """
    Apply stereo widening effect to audio.

    Makes the stereo image wider for a more spacious sound.
    Works best on stereo content with distinct L/R information.

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/audio-quality/widen-stereo" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "audio_path": "audio_files/narrow_mix.wav",
                 "width": 1.5
             }'
        ```
    """
    try:
        start_time = time.time()
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_audio_enhancement()
        output_path = enhancement_service.widen_stereo(
            audio_path=audio_path,
            width=request.width,
        )

        processing_time = time.time() - start_time

        return EnhancementResponse(
            success=True,
            output_path=str(output_path),
            message=f"Stereo widening applied (width: {request.width}x)",
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error widening stereo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to widen stereo: {str(e)}",
        )


@router.post(
    "/enhance",
    response_model=EnhancementResponse,
    summary="Apply audio enhancement",
    description="Apply multiple enhancement algorithms (WBS 2.15.6)",
)
async def enhance_audio(request: EnhancementRequest):
    """
    Apply multiple enhancement algorithms to audio.

    Combines noise reduction, compression, stereo widening,
    and normalization in an optimized pipeline.

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/audio-quality/enhance" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "audio_path": "audio_files/raw_recording.wav",
                 "reduce_noise": true,
                 "compress": true,
                 "widen_stereo": false,
                 "normalize": true
             }'
        ```
    """
    try:
        start_time = time.time()
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_audio_enhancement()
        output_path = enhancement_service.enhance_audio(
            audio_path=audio_path,
            reduce_noise=request.reduce_noise,
            compress=request.compress,
            widen_stereo=request.widen_stereo,
            normalize=request.normalize,
        )

        processing_time = time.time() - start_time

        enhancements = []
        if request.reduce_noise:
            enhancements.append("noise reduction")
        if request.compress:
            enhancements.append("compression")
        if request.widen_stereo:
            enhancements.append("stereo widening")
        if request.normalize:
            enhancements.append("normalization")

        return EnhancementResponse(
            success=True,
            output_path=str(output_path),
            message=f"Enhancement complete: {', '.join(enhancements)}",
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enhancing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance audio: {str(e)}",
        )


@router.post(
    "/normalize-loudness",
    response_model=EnhancementResponse,
    summary="Normalize audio loudness",
    description="Normalize audio to target LUFS",
)
async def normalize_loudness(request: LoudnessNormalizationRequest):
    """Normalize audio loudness to target LUFS."""
    try:
        start_time = time.time()
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_audio_enhancement()
        output_path = enhancement_service.normalize_loudness(
            audio_path=audio_path,
            target_lufs=request.target_lufs,
        )

        processing_time = time.time() - start_time

        return EnhancementResponse(
            success=True,
            output_path=str(output_path),
            message=f"Loudness normalized to {request.target_lufs} LUFS",
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error normalizing loudness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to normalize loudness: {str(e)}",
        )


@router.post(
    "/enhance-batch",
    response_model=BatchEnhancementResponse,
    summary="Enhance multiple audio files",
)
async def enhance_audio_batch(request: BatchEnhancementRequest):
    """Enhance multiple audio files in batch."""
    try:
        enhancement_service = get_audio_enhancement()
        results = []
        successful = 0
        failed = 0

        for audio_path_str in request.audio_paths:
            try:
                audio_path = Path(audio_path_str)

                if not audio_path.exists():
                    results.append(
                        EnhancementResponse(
                            success=False,
                            output_path="",
                            message=f"File not found: {audio_path_str}",
                        )
                    )
                    failed += 1
                    continue

                start_time = time.time()
                output_path = enhancement_service.enhance_audio(
                    audio_path=audio_path,
                    reduce_noise=request.reduce_noise,
                    compress=request.compress,
                    normalize=request.normalize,
                )
                processing_time = time.time() - start_time

                results.append(
                    EnhancementResponse(
                        success=True,
                        output_path=str(output_path),
                        message="Enhancement complete",
                        processing_time_seconds=processing_time,
                    )
                )
                successful += 1

            except Exception as e:
                results.append(
                    EnhancementResponse(
                        success=False,
                        output_path="",
                        message=f"Error: {str(e)}",
                    )
                )
                failed += 1

        return BatchEnhancementResponse(
            results=results,
            total_processed=len(results),
            successful=successful,
            failed=failed,
        )

    except Exception as e:
        logger.error(f"Error in batch enhancement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch enhancement failed: {str(e)}",
        )


# ============================================================================
# Analysis Endpoints
# ============================================================================


@router.get(
    "/analyze/loudness",
    response_model=LoudnessAnalysisResponse,
    summary="Analyze audio loudness",
    description="Analyze loudness metrics (RMS, peak, LUFS) (WBS 2.15.5)",
)
async def analyze_loudness(audio_path: str):
    """
    Analyze audio loudness metrics.

    Returns comprehensive loudness analysis including:
    - RMS (Root Mean Square) level
    - Peak level
    - True peak (inter-sample)
    - Estimated LUFS (Loudness Units Full Scale)
    - Crest factor
    - Loudness range
    - Clipping detection
    - Headroom

    Example:
        ```bash
        curl "http://localhost:8000/api/v1/audio-quality/analyze/loudness?audio_path=audio_files/my_song.wav"
        ```
    """
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        analysis_service = get_audio_analysis()
        result = analysis_service.analyze_loudness(path)

        return LoudnessAnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing loudness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze loudness: {str(e)}",
        )


@router.get(
    "/analyze/clarity",
    response_model=ClarityAnalysisResponse,
    summary="Analyze audio clarity",
    description="Analyze clarity and quality metrics (WBS 2.15.5)",
)
async def analyze_clarity(audio_path: str):
    """
    Analyze audio clarity and quality.

    Returns spectral and quality metrics including:
    - Spectral centroid (brightness)
    - Spectral rolloff
    - Spectral bandwidth
    - Zero crossing rate (noisiness)
    - Signal-to-noise ratio
    - Spectral contrast
    - Overall clarity score (0-100)
    - Quality grade

    Example:
        ```bash
        curl "http://localhost:8000/api/v1/audio-quality/analyze/clarity?audio_path=audio_files/my_song.wav"
        ```
    """
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        analysis_service = get_audio_analysis()
        result = analysis_service.analyze_clarity(path)

        return ClarityAnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing clarity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze clarity: {str(e)}",
        )


@router.get(
    "/analyze/spectral",
    response_model=SpectralAnalysisResponse,
    summary="Analyze audio spectrum",
    description="Analyze frequency spectrum and distribution",
)
async def analyze_spectral(audio_path: str):
    """
    Analyze audio frequency spectrum.

    Returns spectral characteristics:
    - Energy distribution across frequency bands
    - Spectral flatness (tonal vs noisy)
    - Frequency range analysis

    Example:
        ```bash
        curl "http://localhost:8000/api/v1/audio-quality/analyze/spectral?audio_path=audio_files/my_song.wav"
        ```
    """
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        analysis_service = get_audio_analysis()
        result = analysis_service.analyze_spectral(path)

        return SpectralAnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing spectrum: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze spectrum: {str(e)}",
        )


@router.get(
    "/analyze/performance",
    response_model=PerformanceMetricsResponse,
    summary="Analyze audio performance metrics",
    description="Analyze encoding quality and file metrics (WBS 2.15.8)",
)
async def analyze_performance(audio_path: str):
    """
    Analyze audio file performance metrics.

    Returns file and encoding metrics:
    - File size
    - Duration
    - Sample rate
    - Bit depth
    - Channels
    - Estimated bitrate
    - High frequency preservation
    - Overall encoding quality

    Example:
        ```bash
        curl "http://localhost:8000/api/v1/audio-quality/analyze/performance?audio_path=audio_files/my_song.wav"
        ```
    """
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        analysis_service = get_audio_analysis()
        result = analysis_service.analyze_performance(path)

        return PerformanceMetricsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance: {str(e)}",
        )


@router.get(
    "/analyze/comprehensive",
    response_model=ComprehensiveAnalysisResponse,
    summary="Comprehensive audio analysis",
    description="Complete analysis with all metrics and overall quality score",
)
async def analyze_comprehensive(audio_path: str):
    """
    Perform comprehensive audio analysis.

    Returns complete analysis including:
    - All loudness metrics
    - Clarity and quality analysis
    - Spectral analysis
    - Performance metrics
    - Overall quality score and grade

    This is the most complete analysis available, combining
    all individual analysis methods.

    Example:
        ```bash
        curl "http://localhost:8000/api/v1/audio-quality/analyze/comprehensive?audio_path=audio_files/my_song.wav"
        ```
    """
    try:
        path = Path(audio_path)

        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {audio_path}",
            )

        analysis_service = get_audio_analysis()
        result = analysis_service.comprehensive_analysis(path)

        return ComprehensiveAnalysisResponse(
            file_path=result["file_path"],
            loudness=LoudnessAnalysisResponse(**result["loudness"]),
            clarity=ClarityAnalysisResponse(**result["clarity"]),
            spectral=SpectralAnalysisResponse(**result["spectral"]),
            performance=PerformanceMetricsResponse(**result["performance"]),
            overall=OverallQualityResponse(**result["overall"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comprehensive analysis failed: {str(e)}",
        )
