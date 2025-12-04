"""
API endpoints for song production.

This module provides endpoints for:
- Song assembly (vocals + music)
- Structured song creation
- Lyrics synchronization
- Final mastering
- Multi-format export
- Complete song generation workflow
"""

import time
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.schemas.production import (
    CompleteSongRequest,
    CompleteSongResponse,
    LyricsSyncRequest,
    MultiFormatExportRequest,
    RadioEditRequest,
    SongAssemblyRequest,
    SongMasteringRequest,
    SongPreviewRequest,
    SongProductionResponse,
    StructuredSongRequest,
)
from app.services.music import MusicGenerationService, get_music_generation
from app.services.production import get_song_assembly, get_song_mastering
from app.services.voice import get_voice_synthesis

router = APIRouter()


@router.post(
    "/assemble",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "balanced_mix": {
                            "summary": "Balanced Mix",
                            "value": {
                                "vocals_path": "audio_files/vocals/my_vocals.wav",
                                "music_path": "audio_files/music/my_music.wav",
                                "vocals_volume_db": 0.0,
                                "music_volume_db": -5.0,
                                "crossfade_ms": 500,
                            },
                        },
                        "vocals_forward": {
                            "summary": "Vocals Forward",
                            "value": {
                                "vocals_path": "audio_files/vocals/vocals.wav",
                                "music_path": "audio_files/music/music.wav",
                                "vocals_volume_db": 2.0,
                                "music_volume_db": -8.0,
                                "crossfade_ms": 300,
                            },
                        },
                        "music_forward": {
                            "summary": "Music Forward",
                            "value": {
                                "vocals_path": "audio_files/vocals/vocals.wav",
                                "music_path": "audio_files/music/music.wav",
                                "vocals_volume_db": -3.0,
                                "music_volume_db": 0.0,
                                "crossfade_ms": 700,
                            },
                        },
                        "no_crossfade": {
                            "summary": "No Crossfade",
                            "value": {
                                "vocals_path": "audio_files/vocals/vocals.wav",
                                "music_path": "audio_files/music/music.wav",
                                "vocals_volume_db": 0.0,
                                "music_volume_db": -5.0,
                                "crossfade_ms": 0,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def assemble_song(request: SongAssemblyRequest):
    """
    Assemble complete song by mixing vocals with instrumental music.

    This endpoint combines vocals and music into a single mixed track
    with volume balancing and optional crossfade effects.

    Args:
        request: Song assembly parameters

    Returns:
        Path to assembled song with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/assemble" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "vocals_path": "audio_files/vocals/my_vocals.wav",
                 "music_path": "audio_files/music/my_music.wav",
                 "vocals_volume_db": 0,
                 "music_volume_db": -5,
                 "crossfade_ms": 500
             }'
        ```
    """
    try:
        logger.info("Assembling song from vocals and music")

        service = get_song_assembly()

        # Validate paths
        vocals_path = Path(request.vocals_path)
        music_path = Path(request.music_path)

        if not vocals_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vocals file not found: {request.vocals_path}",
            )

        if not music_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music file not found: {request.music_path}",
            )

        # Assemble song
        output_path = service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            vocals_volume_db=request.vocals_volume_db,
            music_volume_db=request.music_volume_db,
            crossfade_ms=request.crossfade_ms,
        )

        # Get file info
        file_size = output_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0  # Convert to seconds

        return SongProductionResponse(
            success=True,
            message="Song assembled successfully",
            output_path=str(output_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assembling song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assemble song: {str(e)}",
        )


@router.post(
    "/structured",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "standard_structure": {
                            "summary": "Standard Song Structure",
                            "value": {
                                "sections": [
                                    {
                                        "type": "intro",
                                        "music_path": "audio_files/music/intro.wav",
                                        "duration": 8,
                                    },
                                    {
                                        "type": "verse",
                                        "vocals_path": "audio_files/vocals/verse1.wav",
                                        "music_path": "audio_files/music/verse.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "chorus",
                                        "vocals_path": "audio_files/vocals/chorus.wav",
                                        "music_path": "audio_files/music/chorus.wav",
                                        "duration": 16,
                                    },
                                ]
                            },
                        },
                        "full_structure": {
                            "summary": "Full Song Structure",
                            "value": {
                                "sections": [
                                    {
                                        "type": "intro",
                                        "music_path": "audio_files/music/intro.wav",
                                        "duration": 8,
                                    },
                                    {
                                        "type": "verse",
                                        "vocals_path": "audio_files/vocals/verse1.wav",
                                        "music_path": "audio_files/music/verse.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "chorus",
                                        "vocals_path": "audio_files/vocals/chorus.wav",
                                        "music_path": "audio_files/music/chorus.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "verse",
                                        "vocals_path": "audio_files/vocals/verse2.wav",
                                        "music_path": "audio_files/music/verse.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "chorus",
                                        "vocals_path": "audio_files/vocals/chorus.wav",
                                        "music_path": "audio_files/music/chorus.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "bridge",
                                        "vocals_path": "audio_files/vocals/bridge.wav",
                                        "music_path": "audio_files/music/bridge.wav",
                                        "duration": 8,
                                    },
                                    {
                                        "type": "chorus",
                                        "vocals_path": "audio_files/vocals/chorus.wav",
                                        "music_path": "audio_files/music/chorus.wav",
                                        "duration": 16,
                                    },
                                    {
                                        "type": "outro",
                                        "music_path": "audio_files/music/outro.wav",
                                        "duration": 8,
                                    },
                                ]
                            },
                        },
                        "simple_structure": {
                            "summary": "Simple Structure",
                            "value": {
                                "sections": [
                                    {
                                        "type": "intro",
                                        "music_path": "audio_files/music/intro.wav",
                                        "duration": 4,
                                    },
                                    {
                                        "type": "verse",
                                        "vocals_path": "audio_files/vocals/verse.wav",
                                        "music_path": "audio_files/music/verse.wav",
                                        "duration": 8,
                                    },
                                    {
                                        "type": "chorus",
                                        "vocals_path": "audio_files/vocals/chorus.wav",
                                        "music_path": "audio_files/music/chorus.wav",
                                        "duration": 8,
                                    },
                                ]
                            },
                        },
                    }
                }
            }
        }
    },
)
async def create_structured_song(request: StructuredSongRequest):
    """
    Create song with multi-section structure.

    This endpoint creates a complete song with multiple sections
    (intro, verse, chorus, bridge, outro) stitched together with
    crossfade transitions.

    Args:
        request: Structured song parameters with sections

    Returns:
        Path to structured song with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/structured" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "sections": [
                     {"type": "intro", "music_path": "audio_files/music/intro.wav"},
                     {
                         "type": "verse",
                         "vocals_path": "audio_files/vocals/verse1.wav",
                         "music_path": "audio_files/music/verse.wav"
                     },
                     {
                         "type": "chorus",
                         "vocals_path": "audio_files/vocals/chorus.wav",
                         "music_path": "audio_files/music/chorus.wav"
                     }
                 ]
             }'
        ```
    """
    try:
        logger.info(f"Creating structured song with {len(request.sections)} sections")

        service = get_song_assembly()

        # Validate paths
        for section in request.sections:
            music_path = Path(section.music_path)
            if not music_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Music file not found: {section.music_path}",
                )

            if section.vocals_path:
                vocals_path = Path(section.vocals_path)
                if not vocals_path.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Vocals file not found: {section.vocals_path}",
                    )

        # Convert to dict format
        sections_dict = [
            {
                "type": s.type,
                "vocals_path": Path(s.vocals_path) if s.vocals_path else None,
                "music_path": Path(s.music_path),
                "duration": s.duration,
            }
            for s in request.sections
        ]

        # Create structured song
        output_path = service.create_song_with_structure(sections=sections_dict)

        # Get file info
        file_size = output_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0

        return SongProductionResponse(
            success=True,
            message="Structured song created successfully",
            output_path=str(output_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating structured song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create structured song: {str(e)}",
        )


@router.post(
    "/sync-lyrics",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "simple_sync": {
                            "summary": "Simple Sync",
                            "value": {
                                "lyrics_sections": [
                                    {
                                        "text": "Verse 1 lyrics here...",
                                        "start_time": 0,
                                        "duration": 16,
                                    },
                                    {
                                        "text": "Chorus lyrics here...",
                                        "start_time": 16,
                                        "duration": 16,
                                    },
                                ],
                                "music_path": "audio_files/music/song.wav",
                            },
                        },
                        "full_song_sync": {
                            "summary": "Full Song Sync",
                            "value": {
                                "lyrics_sections": [
                                    {
                                        "text": "Intro music playing...",
                                        "start_time": 0,
                                        "duration": 8,
                                    },
                                    {
                                        "text": "Verse 1: Walking down the street",
                                        "start_time": 8,
                                        "duration": 16,
                                    },
                                    {
                                        "text": "Chorus: This is our song",
                                        "start_time": 24,
                                        "duration": 16,
                                    },
                                    {
                                        "text": "Verse 2: Music fills the air",
                                        "start_time": 40,
                                        "duration": 16,
                                    },
                                    {
                                        "text": "Chorus: This is our song",
                                        "start_time": 56,
                                        "duration": 16,
                                    },
                                    {
                                        "text": "Bridge: Time moves on",
                                        "start_time": 72,
                                        "duration": 8,
                                    },
                                    {
                                        "text": "Chorus: This is our song",
                                        "start_time": 80,
                                        "duration": 16,
                                    },
                                ],
                                "music_path": "audio_files/music/full_song.wav",
                            },
                        },
                        "ballad_sync": {
                            "summary": "Ballad Sync",
                            "value": {
                                "lyrics_sections": [
                                    {
                                        "text": "In the quiet of the night",
                                        "start_time": 0,
                                        "duration": 8,
                                    },
                                    {"text": "I think of you", "start_time": 8, "duration": 8},
                                    {
                                        "text": "All the moments we shared",
                                        "start_time": 16,
                                        "duration": 8,
                                    },
                                    {"text": "So few, so true", "start_time": 24, "duration": 8},
                                ],
                                "music_path": "audio_files/music/ballad.wav",
                            },
                        },
                    }
                }
            }
        }
    },
)
async def sync_lyrics_to_music(request: LyricsSyncRequest):
    """
    Synchronize lyrics sections with music timing.

    This endpoint generates vocals for each lyrics section and places them
    at specified timestamps in the music timeline.

    Args:
        request: Lyrics synchronization parameters

    Returns:
        Path to synchronized vocals with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/sync-lyrics" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "lyrics_sections": [
                     {"text": "Verse 1 lyrics...", "start_time": 0},
                     {"text": "Chorus lyrics...", "start_time": 16}
                 ],
                 "music_path": "audio_files/music/song.wav"
             }'
        ```
    """
    try:
        logger.info(f"Synchronizing {len(request.lyrics_sections)} lyrics sections")

        service = get_song_assembly()

        # Validate music path
        music_path = Path(request.music_path)
        if not music_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music file not found: {request.music_path}",
            )

        # Convert to dict format
        sections_dict = [
            {"text": s.text, "start_time": s.start_time, "duration": s.duration}
            for s in request.lyrics_sections
        ]

        # Output path
        output_path = Path("audio_files/vocals") / "synced_vocals.wav"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sync lyrics
        result_path = service.sync_lyrics_to_music(
            lyrics_sections=sections_dict, music_path=music_path, output_vocals_path=output_path
        )

        # Get file info
        file_size = result_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(result_path))
        duration = len(audio) / 1000.0

        return SongProductionResponse(
            success=True,
            message="Lyrics synchronized successfully",
            output_path=str(result_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synchronizing lyrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synchronize lyrics: {str(e)}",
        )


@router.post(
    "/master",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_mastering": {
                            "summary": "Pop Mastering",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "target_loudness": -14.0,
                                "genre": "pop",
                            },
                        },
                        "rock_mastering": {
                            "summary": "Rock Mastering",
                            "value": {
                                "song_path": "audio_files/songs/rock_song.wav",
                                "target_loudness": -12.0,
                                "genre": "rock",
                            },
                        },
                        "jazz_mastering": {
                            "summary": "Jazz Mastering",
                            "value": {
                                "song_path": "audio_files/songs/jazz_song.wav",
                                "target_loudness": -16.0,
                                "genre": "jazz",
                            },
                        },
                        "generic_mastering": {
                            "summary": "Generic Mastering",
                            "value": {
                                "song_path": "audio_files/songs/song.wav",
                                "target_loudness": -14.0,
                                "genre": None,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def master_song(request: SongMasteringRequest):
    """
    Apply final mastering to song.

    This endpoint applies professional mastering including loudness
    normalization, peak limiting, and genre-specific processing.

    Args:
        request: Mastering parameters

    Returns:
        Path to mastered song with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/master" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "song_path": "audio_files/songs/my_song.wav",
                 "target_loudness": -14.0,
                 "genre": "pop"
             }'
        ```
    """
    try:
        logger.info("Mastering song")

        service = get_song_mastering()

        # Validate path
        song_path = Path(request.song_path)
        if not song_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song file not found: {request.song_path}",
            )

        # Master song
        output_path = service.master_song(
            song_path=song_path, target_loudness=request.target_loudness, genre=request.genre
        )

        # Get file info
        file_size = output_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0

        return SongProductionResponse(
            success=True,
            message="Song mastered successfully",
            output_path=str(output_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mastering song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to master song: {str(e)}",
        )


@router.post(
    "/preview",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "standard_preview": {
                            "summary": "Standard Preview (30s)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "preview_duration": 30,
                            },
                        },
                        "short_preview": {
                            "summary": "Short Preview (15s)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "preview_duration": 15,
                            },
                        },
                        "long_preview": {
                            "summary": "Long Preview (60s)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "preview_duration": 60,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def create_song_preview(request: SongPreviewRequest):
    """
    Create preview/sample of song (typically 30 seconds).

    This endpoint extracts a preview from the full song with fade out.

    Args:
        request: Preview parameters

    Returns:
        Path to preview with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/preview" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "song_path": "audio_files/songs/my_song.wav",
                 "preview_duration": 30
             }'
        ```
    """
    try:
        logger.info(f"Creating {request.preview_duration}s preview")

        service = get_song_assembly()

        # Validate path
        song_path = Path(request.song_path)
        if not song_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song file not found: {request.song_path}",
            )

        # Create preview
        output_path = service.create_song_preview(
            song_path=song_path, preview_duration=request.preview_duration
        )

        # Get file info
        file_size = output_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0

        return SongProductionResponse(
            success=True,
            message="Preview created successfully",
            output_path=str(output_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create preview: {str(e)}",
        )


@router.post(
    "/export",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "all_formats": {
                            "summary": "All Formats",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "formats": ["mp3", "wav", "ogg", "flac", "m4a"],
                            },
                        },
                        "web_formats": {
                            "summary": "Web Formats",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "formats": ["mp3", "ogg"],
                            },
                        },
                        "lossless_formats": {
                            "summary": "Lossless Formats",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "formats": ["wav", "flac"],
                            },
                        },
                        "single_format": {
                            "summary": "Single Format (MP3)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "formats": ["mp3"],
                            },
                        },
                    }
                }
            }
        }
    },
)
async def export_multi_format(request: MultiFormatExportRequest):
    """
    Export song in multiple formats (MP3, WAV, OGG, FLAC, M4A).

    This endpoint converts the song to multiple formats simultaneously.

    Args:
        request: Export parameters

    Returns:
        Dictionary of format to file path mappings

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/export" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "song_path": "audio_files/songs/my_song.wav",
                 "formats": ["mp3", "wav", "ogg", "flac"]
             }'
        ```
    """
    try:
        logger.info(f"Exporting song in {len(request.formats)} formats")

        service = get_song_assembly()

        # Validate path
        song_path = Path(request.song_path)
        if not song_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song file not found: {request.song_path}",
            )

        # Validate formats
        valid_formats = {"mp3", "wav", "ogg", "flac", "m4a"}
        invalid_formats = set(request.formats) - valid_formats
        if invalid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid formats: {invalid_formats}. Valid: {valid_formats}",
            )

        # Export
        output_paths = service.export_multi_format(song_path=song_path, formats=request.formats)

        # Convert Path objects to strings
        output_paths_str = {fmt: str(path) for fmt, path in output_paths.items()}

        return SongProductionResponse(
            success=True,
            message=f"Song exported in {len(output_paths)} formats",
            output_paths=output_paths_str,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export song: {str(e)}",
        )


@router.post(
    "/radio-edit",
    response_model=SongProductionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "standard_radio_edit": {
                            "summary": "Standard Radio Edit (3 min)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "target_duration": 180,
                            },
                        },
                        "short_radio_edit": {
                            "summary": "Short Radio Edit (2 min)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "target_duration": 120,
                            },
                        },
                        "extended_radio_edit": {
                            "summary": "Extended Radio Edit (4 min)",
                            "value": {
                                "song_path": "audio_files/songs/my_song.wav",
                                "target_duration": 240,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def create_radio_edit(request: RadioEditRequest):
    """
    Create radio edit version (typically 3 minutes).

    This endpoint creates a shortened version of the song suitable for radio.

    Args:
        request: Radio edit parameters

    Returns:
        Path to radio edit with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/radio-edit" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "song_path": "audio_files/songs/my_song.wav",
                 "target_duration": 180
             }'
        ```
    """
    try:
        logger.info(f"Creating radio edit ({request.target_duration}s)")

        service = get_song_mastering()

        # Validate path
        song_path = Path(request.song_path)
        if not song_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song file not found: {request.song_path}",
            )

        # Create radio edit
        output_path = service.create_radio_edit(
            song_path=song_path, target_duration=request.target_duration
        )

        # Get file info
        file_size = output_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(output_path))
        duration = len(audio) / 1000.0

        return SongProductionResponse(
            success=True,
            message="Radio edit created successfully",
            output_path=str(output_path),
            duration=duration,
            file_size=file_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating radio edit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create radio edit: {str(e)}",
        )


@router.post(
    "/generate-complete",
    response_model=CompleteSongResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_song": {
                            "summary": "Pop Song",
                            "value": {
                                "lyrics_text": "[Verse 1]\nWalking down the street\nFeeling the beat\n\n[Chorus]\nDancing in the moonlight\nEverything feels right\n\n[Verse 2]\nMusic fills the air\nNo time for a care\n\n[Chorus]\nDancing in the moonlight\nEverything feels right",
                                "genre": "pop",
                                "bpm": 120,
                                "key": "C major",
                                "voice_profile": "female_singer_1",
                                "duration": 180,
                            },
                        },
                        "rock_song": {
                            "summary": "Rock Song",
                            "value": {
                                "lyrics_text": "[Verse 1]\nTurn up the volume\nFeel the power\n\n[Chorus]\nRock and roll forever\nWe'll never surrender\n\n[Verse 2]\nGuitars are screaming\nDrums are beating\n\n[Chorus]\nRock and roll forever\nWe'll never surrender",
                                "genre": "rock",
                                "bpm": 140,
                                "key": "E major",
                                "voice_profile": "male_singer_1",
                                "duration": 200,
                            },
                        },
                        "ballad_song": {
                            "summary": "Ballad Song",
                            "value": {
                                "lyrics_text": "[Verse]\nIn the quiet of the night\nI think of you\nAll the moments we shared\nSo few, so true\n\n[Bridge]\nTime moves on\nBut memories stay\nIn my heart forever\nThey'll never fade away",
                                "genre": "pop",
                                "bpm": 80,
                                "key": "Am",
                                "voice_profile": "female_singer_1",
                                "duration": 150,
                            },
                        },
                        "jazz_song": {
                            "summary": "Jazz Song",
                            "value": {
                                "lyrics_text": "[Verse]\nSmooth jazz in the air\nSaxophone playing\nPiano keys dancing\nNight is calling\n\n[Bridge]\nFeel the rhythm\nMove with the beat\nJazz is flowing\nSo sweet",
                                "genre": "jazz",
                                "bpm": 100,
                                "key": "F major",
                                "voice_profile": "female_singer_1",
                                "duration": 240,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def generate_complete_song(request: CompleteSongRequest):
    """
    Generate complete song from lyrics (end-to-end pipeline).

    This is the master endpoint that orchestrates the entire song
    generation pipeline:
    1. Generate vocals from lyrics
    2. Generate instrumental music
    3. Mix vocals and music
    4. Apply mastering
    5. Create preview

    Args:
        request: Complete song generation parameters

    Returns:
        Complete song with all variants and metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/production/generate-complete" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "lyrics_text": "Verse 1...\\n\\nChorus...\\n\\nVerse 2...",
                 "genre": "pop",
                 "bpm": 120,
                 "key": "C major",
                 "voice_profile": "female_singer_1",
                 "duration": 180
             }'
        ```
    """
    try:
        start_time = time.time()
        logger.info("Starting complete song generation")

        # Generate unique song ID
        song_id = f"song_{uuid.uuid4().hex[:8]}"
        base_path = Path("audio_files/songs") / song_id
        base_path.mkdir(parents=True, exist_ok=True)

        # Initialize services
        voice_service = get_voice_synthesis()
        music_service = get_music_generation()
        assembly_service = get_song_assembly()
        mastering_service = get_song_mastering()

        # Step 1: Generate vocals
        logger.info("Step 1/5: Generating vocals")
        from app.core.voice_config import get_voice_profile

        voice_profile = get_voice_profile(request.voice_profile)
        vocals_path = base_path / "vocals.wav"
        voice_service.synthesize_text(
            text=request.lyrics_text, voice_profile=voice_profile, output_path=vocals_path
        )

        # Step 2: Generate music
        logger.info("Step 2/5: Generating instrumental music")
        music_prompt = f"{request.genre} instrumental at {request.bpm} BPM"
        music_path = base_path / "music.wav"
        music_service.generate_music(
            prompt=music_prompt, duration=request.duration, output_path=music_path
        )

        # Step 3: Mix vocals and music
        logger.info("Step 3/5: Mixing vocals and music")
        mixed_path = base_path / "mixed.wav"
        assembly_service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            output_path=mixed_path,
            vocals_volume_db=0.0,
            music_volume_db=-5.0,
            crossfade_ms=500,
        )

        # Step 4: Master song
        logger.info("Step 4/5: Applying final mastering")
        final_path = base_path / f"{song_id}.wav"
        mastering_service.master_song(
            song_path=mixed_path, output_path=final_path, genre=request.genre
        )

        # Step 5: Create preview
        logger.info("Step 5/5: Creating preview")
        preview_path = base_path / f"{song_id}_preview.wav"
        assembly_service.create_song_preview(
            song_path=final_path, preview_duration=30, output_path=preview_path
        )

        # Get file info
        file_size = final_path.stat().st_size
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(final_path))
        duration = len(audio) / 1000.0

        generation_time = time.time() - start_time

        logger.success(f"Complete song generated in {generation_time:.2f}s: {song_id}")

        return CompleteSongResponse(
            success=True,
            message="Complete song generated successfully",
            song_id=song_id,
            song_path=str(final_path),
            vocals_path=str(vocals_path),
            music_path=str(music_path),
            preview_path=str(preview_path),
            duration=duration,
            file_size=file_size,
            generation_time=generation_time,
        )

    except Exception as e:
        logger.error(f"Error generating complete song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate complete song: {str(e)}",
        )
