"""
Audio processing API endpoints.

This module provides RESTful endpoints for audio operations including:
- File upload and storage
- Format conversion
- Metadata extraction
- Waveform generation
- Audio mixing
- Mastering and normalization
"""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel, Field

from app.core.audio_config import AudioFormat, AudioQuality
from app.services.audio import (
    get_audio_converter,
    get_audio_mastering,
    get_audio_metadata,
    get_audio_storage,
    get_audio_waveform,
)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class AudioUploadResponse(BaseModel):
    """Response after audio upload."""

    filename: str
    path: str
    size_mb: float
    format: str


class AudioMetadataResponse(BaseModel):
    """Audio metadata response."""

    filename: str
    format: str
    duration_seconds: float
    sample_rate: int
    channels: int
    file_size_mb: float
    audio_features: Optional[dict] = None


class ConversionRequest(BaseModel):
    """Audio conversion request."""

    target_format: AudioFormat
    quality: AudioQuality = AudioQuality.HIGH


class MixRequest(BaseModel):
    """Audio mixing request."""

    track_ids: List[str] = Field(..., min_items=2)
    volumes: Optional[List[float]] = None
    output_filename: str


class MasteringRequest(BaseModel):
    """Audio mastering request."""

    target_loudness: float = Field(default=-14.0, ge=-30.0, le=0.0)
    peak_limit: float = Field(default=-1.0, ge=-6.0, le=0.0)
    apply_compression: bool = True


# ============================================================================
# Upload & Storage Endpoints
# ============================================================================


@router.post(
    "/upload",
    response_model=AudioUploadResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "description": "Audio file (WAV, MP3, OGG, FLAC, etc.)",
                            },
                            "category": {
                                "type": "string",
                                "description": "Storage category",
                                "default": "songs",
                                "enum": ["songs", "voices", "music", "temp"],
                            },
                        },
                        "required": ["file"],
                    },
                    "examples": {
                        "song_upload": {
                            "summary": "Upload Song",
                            "value": {
                                "file": "(binary)",
                                "category": "songs",
                            },
                        },
                        "voice_upload": {
                            "summary": "Upload Voice",
                            "value": {
                                "file": "(binary)",
                                "category": "voices",
                            },
                        },
                        "music_upload": {
                            "summary": "Upload Music",
                            "value": {
                                "file": "(binary)",
                                "category": "music",
                            },
                        },
                    },
                }
            }
        }
    },
)
async def upload_audio(
    file: UploadFile = File(...),
    category: str = Form(default="songs"),
):
    """
    Upload an audio file.

    Args:
        file: Audio file to upload
        category: Storage category (songs/voices/music/temp)

    Returns:
        Upload confirmation with file details
    """
    try:
        storage = get_audio_storage()

        # Save file
        saved_path = storage.save_audio(
            file_data=file.file, filename=file.filename, category=category
        )

        # Get file info
        file_info = storage.get_file_info(saved_path)

        return AudioUploadResponse(
            filename=file_info["filename"],
            path=file_info["path"],
            size_mb=file_info["size_mb"],
            format=Path(file.filename).suffix[1:],
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed",
        )


@router.get(
    "/download/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "song_file": {
                        "summary": "Song File",
                        "value": "my_song.wav",
                    },
                    "voice_file": {
                        "summary": "Voice File",
                        "value": "vocals.mp3",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
                "examples": {
                    "songs": {"summary": "Songs Category", "value": "songs"},
                    "voices": {"summary": "Voices Category", "value": "voices"},
                },
            },
        ]
    },
)
async def download_audio(filename: str, category: str = "songs"):
    """
    Download an audio file.

    Args:
        filename: Audio filename
        category: Storage category

    Returns:
        Audio file for download
    """
    try:
        storage = get_audio_storage()
        filepath = storage.base_path / category / filename

        if not filepath.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        return FileResponse(
            path=str(filepath),
            media_type="audio/mpeg",
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Download failed",
        )


# ============================================================================
# Metadata Endpoints
# ============================================================================


@router.get(
    "/metadata/{filename}",
    response_model=AudioMetadataResponse,
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "song_metadata": {
                        "summary": "Song Metadata",
                        "value": "my_song.wav",
                    },
                    "voice_metadata": {
                        "summary": "Voice Metadata",
                        "value": "vocals.mp3",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
                "examples": {
                    "songs": {"summary": "Songs Category", "value": "songs"},
                    "music": {"summary": "Music Category", "value": "music"},
                },
            },
        ]
    },
)
async def get_metadata(filename: str, category: str = "songs"):
    """
    Get audio file metadata.

    Args:
        filename: Audio filename
        category: Storage category

    Returns:
        Audio metadata
    """
    try:
        storage = get_audio_storage()
        metadata_service = get_audio_metadata()

        filepath = storage.base_path / category / filename

        if not filepath.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        metadata = metadata_service.extract_metadata(filepath)

        return AudioMetadataResponse(**metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metadata extraction failed",
        )


# ============================================================================
# Conversion Endpoints
# ============================================================================


@router.post(
    "/convert/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "convert_song": {
                        "summary": "Convert Song",
                        "value": "my_song.wav",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "to_mp3": {
                            "summary": "Convert to MP3",
                            "value": {
                                "target_format": "mp3",
                                "quality": "high",
                            },
                        },
                        "to_wav": {
                            "summary": "Convert to WAV",
                            "value": {
                                "target_format": "wav",
                                "quality": "high",
                            },
                        },
                        "to_ogg": {
                            "summary": "Convert to OGG",
                            "value": {
                                "target_format": "ogg",
                                "quality": "medium",
                            },
                        },
                        "to_flac": {
                            "summary": "Convert to FLAC",
                            "value": {
                                "target_format": "flac",
                                "quality": "high",
                            },
                        },
                    }
                }
            }
        },
    },
)
async def convert_audio(
    filename: str,
    conversion: ConversionRequest,
    category: str = "songs",
):
    """
    Convert audio to different format.

    Args:
        filename: Audio filename
        conversion: Conversion parameters
        category: Storage category

    Returns:
        Converted file details
    """
    try:
        storage = get_audio_storage()
        converter = get_audio_converter()

        input_path = storage.base_path / category / filename

        if not input_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        # Convert
        output_path = converter.convert(
            input_path=input_path,
            output_format=conversion.target_format,
            quality=conversion.quality,
        )

        # Get file info
        file_info = storage.get_file_info(output_path)

        return {
            "original_filename": filename,
            "converted_filename": file_info["filename"],
            "format": conversion.target_format,
            "quality": conversion.quality,
            "size_mb": file_info["size_mb"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversion failed",
        )


# ============================================================================
# Waveform Endpoints
# ============================================================================


@router.get(
    "/waveform/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "song_waveform": {
                        "summary": "Song Waveform",
                        "value": "my_song.wav",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
            },
        ]
    },
)
async def generate_waveform(filename: str, category: str = "songs"):
    """
    Generate waveform image for audio file.

    Args:
        filename: Audio filename
        category: Storage category

    Returns:
        Waveform image file
    """
    try:
        storage = get_audio_storage()
        waveform_service = get_audio_waveform()

        audio_path = storage.base_path / category / filename

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        # Generate waveform
        waveform_path = waveform_service.generate_waveform(audio_path)

        return FileResponse(
            path=str(waveform_path),
            media_type="image/png",
            filename=waveform_path.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Waveform generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Waveform generation failed",
        )


@router.get(
    "/waveform-data/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "song_data": {
                        "summary": "Song Waveform Data",
                        "value": "my_song.wav",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
            },
            {
                "name": "samples",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "default": 1000, "minimum": 100, "maximum": 10000},
                "examples": {
                    "low_res": {"summary": "Low Resolution", "value": 500},
                    "default": {"summary": "Default", "value": 1000},
                    "high_res": {"summary": "High Resolution", "value": 5000},
                },
            },
        ]
    },
)
async def get_waveform_data(filename: str, category: str = "songs", samples: int = 1000):
    """
    Get waveform data points (for frontend visualization).

    Args:
        filename: Audio filename
        category: Storage category
        samples: Number of data points

    Returns:
        Waveform data points
    """
    try:
        storage = get_audio_storage()
        waveform_service = get_audio_waveform()

        audio_path = storage.base_path / category / filename

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        data = waveform_service.generate_waveform_data(audio_path, samples=samples)

        return data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Waveform data generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Waveform data generation failed",
        )


# ============================================================================
# Mastering Endpoints
# ============================================================================


@router.post(
    "/master/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "master_song": {
                        "summary": "Master Song",
                        "value": "my_song.wav",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "standard_mastering": {
                            "summary": "Standard Mastering",
                            "value": {
                                "target_loudness": -14.0,
                                "peak_limit": -1.0,
                                "apply_compression": True,
                            },
                        },
                        "loud_mastering": {
                            "summary": "Loud Mastering",
                            "value": {
                                "target_loudness": -12.0,
                                "peak_limit": -0.5,
                                "apply_compression": True,
                            },
                        },
                        "gentle_mastering": {
                            "summary": "Gentle Mastering",
                            "value": {
                                "target_loudness": -16.0,
                                "peak_limit": -2.0,
                                "apply_compression": False,
                            },
                        },
                    }
                }
            }
        },
    },
)
async def master_audio(
    filename: str,
    mastering: MasteringRequest,
    category: str = "songs",
):
    """
    Apply professional mastering to audio.

    Args:
        filename: Audio filename
        mastering: Mastering parameters
        category: Storage category

    Returns:
        Mastered file details
    """
    try:
        storage = get_audio_storage()
        mastering_service = get_audio_mastering()

        audio_path = storage.base_path / category / filename

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        # Master audio
        mastered_path = mastering_service.master_audio(
            audio_path=audio_path,
            target_loudness=mastering.target_loudness,
            peak_limit=mastering.peak_limit,
            apply_compression=mastering.apply_compression,
        )

        # Get file info
        file_info = storage.get_file_info(mastered_path)

        return {
            "original_filename": filename,
            "mastered_filename": file_info["filename"],
            "target_loudness": mastering.target_loudness,
            "peak_limit": mastering.peak_limit,
            "size_mb": file_info["size_mb"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mastering failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mastering failed",
        )


@router.get(
    "/analyze/{filename}",
    openapi_extra={
        "parameters": [
            {
                "name": "filename",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "analyze_song": {
                        "summary": "Analyze Song",
                        "value": "my_song.wav",
                    },
                },
            },
            {
                "name": "category",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "default": "songs"},
            },
        ]
    },
)
async def analyze_audio(filename: str, category: str = "songs"):
    """
    Analyze audio loudness and quality metrics.

    Args:
        filename: Audio filename
        category: Storage category

    Returns:
        Loudness analysis
    """
    try:
        storage = get_audio_storage()
        mastering_service = get_audio_mastering()

        audio_path = storage.base_path / category / filename

        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found"
            )

        analysis = mastering_service.analyze_loudness(audio_path)

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed",
        )


# ============================================================================
# Storage Stats Endpoint
# ============================================================================


@router.get("/stats")
async def get_storage_stats():
    """
    Get audio storage statistics.

    Returns:
        Storage stats (file counts, sizes, etc.)
    """
    try:
        storage = get_audio_storage()
        stats = storage.get_storage_stats()
        return stats

    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get storage stats",
        )
