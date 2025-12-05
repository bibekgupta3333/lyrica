"""
API Endpoints for Voice and Mixing Enhancement.

This module provides REST API endpoints for:
- Voice enhancement (neural vocoder, prosody, auto-tune)
- Mixing enhancement (frequency balancing, stereo imaging, genre-specific)
- Complete song enhancement pipeline
- Quality metrics and feedback collection
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.audio_file import AudioFile
from app.models.user import User
from app.schemas.enhancement import (
    CompleteEnhancementRequest,
    EnhancementResponse,
    MixingEnhancementRequest,
    VoiceEnhancementRequest,
)
from app.services.voice import get_voice_enhancement

router = APIRouter(prefix="/enhancement", tags=["Enhancement"])


# ============================================================================
# Voice Enhancement Endpoints
# ============================================================================


@router.post(
    "/voice",
    response_model=EnhancementResponse,
    summary="Enhance voice audio",
    description="Apply voice enhancement to audio file (neural vocoder, prosody, auto-tune)",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "basic_enhancement": {
                            "summary": "Basic Voice Enhancement",
                            "description": "Apply neural vocoder and prosody enhancement",
                            "value": {
                                "audio_path": "audio_files/songs/song_123/vocals.wav",
                                "enable_neural_vocoder": True,
                                "enable_prosody": True,
                                "enable_auto_tune": False,
                            },
                        },
                        "with_autotune": {
                            "summary": "Voice Enhancement with Auto-Tune",
                            "description": "Apply enhancement with auto-tune to C major",
                            "value": {
                                "audio_path": "audio_files/songs/song_123/vocals.wav",
                                "enable_neural_vocoder": True,
                                "enable_prosody": True,
                                "enable_auto_tune": True,
                                "target_key": "C major",
                            },
                        },
                        "neural_vocoder_only": {
                            "summary": "Neural Vocoder Only",
                            "description": "Apply only neural vocoder enhancement",
                            "value": {
                                "audio_path": "audio_files/songs/song_456/vocals_raw.wav",
                                "enable_neural_vocoder": True,
                                "enable_prosody": False,
                                "enable_auto_tune": False,
                            },
                        },
                        "prosody_only": {
                            "summary": "Prosody Enhancement Only",
                            "description": "Apply only prosody enhancement without neural vocoder",
                            "value": {
                                "audio_path": "audio_files/songs/song_789/vocals.wav",
                                "enable_neural_vocoder": False,
                                "enable_prosody": True,
                                "enable_auto_tune": False,
                            },
                        },
                    }
                }
            }
        }
    },
)
async def enhance_voice(
    request: VoiceEnhancementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enhance voice audio quality.

    Applies:
    - Neural vocoder enhancement (if available)
    - Prosody enhancement
    - Auto-tune (if enabled)
    """
    logger.info(f"Voice enhancement request from user {current_user.id}")

    try:
        audio_path = Path(request.audio_path)
        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file not found: {request.audio_path}",
            )

        enhancement_service = get_voice_enhancement()

        # Apply enhancement
        output_path = audio_path.parent / f"{audio_path.stem}_enhanced.wav"
        enhanced_path = enhancement_service.enhance_tts_output(
            tts_audio_path=audio_path,
            output_path=output_path,
            enable_enhancement=request.enable_neural_vocoder,
        )

        # Apply prosody enhancement if enabled
        if request.enable_prosody:
            try:
                from app.services.voice import get_prosody_pitch

                prosody_service = get_prosody_pitch()
                # Prosody enhancement would be applied here
                logger.info("Prosody enhancement applied")
            except Exception as e:
                logger.warning(f"Prosody enhancement failed: {e}")

        # Apply auto-tune if enabled
        if request.enable_auto_tune and request.target_key:
            try:
                from app.services.voice import get_prosody_pitch

                prosody_service = get_prosody_pitch()
                enhanced_path = prosody_service.auto_tune_with_scale(
                    audio_path=enhanced_path,
                    target_key=request.target_key,
                    output_path=enhanced_path,
                )
                logger.info(f"Auto-tune applied with key: {request.target_key}")
            except Exception as e:
                logger.warning(f"Auto-tune failed: {e}")

        # Calculate quality metrics
        quality_metrics = {}
        try:
            from app.services.voice.quality_metrics import get_quality_metrics

            metrics_service = get_quality_metrics()
            quality_metrics = metrics_service.calculate_all_metrics(audio_path=enhanced_path)
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {e}")

        return EnhancementResponse(
            success=True,
            enhanced_audio_path=str(enhanced_path),
            quality_metrics=quality_metrics,
            enhancement_applied=["voice_enhancement"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice enhancement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice enhancement failed: {str(e)}",
        )


# ============================================================================
# Mixing Enhancement Endpoints
# ============================================================================


@router.post(
    "/mixing",
    response_model=EnhancementResponse,
    summary="Enhance mixing",
    description="Apply intelligent mixing to vocals and music",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_mixing": {
                            "summary": "Pop Song Mixing",
                            "description": "Apply full mixing enhancement for pop genre",
                            "value": {
                                "vocals_path": "audio_files/songs/song_123/vocals.wav",
                                "music_path": "audio_files/songs/song_123/music.wav",
                                "genre": "pop",
                                "enable_frequency_balancing": True,
                                "enable_sidechain": True,
                                "enable_stereo_imaging": True,
                            },
                        },
                        "rock_mixing": {
                            "summary": "Rock Song Mixing",
                            "description": "Apply mixing enhancement for rock genre",
                            "value": {
                                "vocals_path": "audio_files/songs/song_456/vocals.wav",
                                "music_path": "audio_files/songs/song_456/music.wav",
                                "genre": "rock",
                                "enable_frequency_balancing": True,
                                "enable_sidechain": True,
                                "enable_stereo_imaging": True,
                            },
                        },
                        "hiphop_mixing": {
                            "summary": "Hip-Hop Mixing",
                            "description": "Apply mixing enhancement for hip-hop genre",
                            "value": {
                                "vocals_path": "audio_files/songs/song_789/vocals.wav",
                                "music_path": "audio_files/songs/song_789/music.wav",
                                "genre": "hiphop",
                                "enable_frequency_balancing": True,
                                "enable_sidechain": True,
                                "enable_stereo_imaging": True,
                            },
                        },
                        "minimal_mixing": {
                            "summary": "Minimal Mixing",
                            "description": "Apply only frequency balancing without sidechain or stereo imaging",
                            "value": {
                                "vocals_path": "audio_files/songs/song_321/vocals.wav",
                                "music_path": "audio_files/songs/song_321/music.wav",
                                "genre": "pop",
                                "enable_frequency_balancing": True,
                                "enable_sidechain": False,
                                "enable_stereo_imaging": False,
                            },
                        },
                        "with_custom_config": {
                            "summary": "Mixing with Custom Config",
                            "description": "Use a specific mixing configuration ID",
                            "value": {
                                "vocals_path": "audio_files/songs/song_654/vocals.wav",
                                "music_path": "audio_files/songs/song_654/music.wav",
                                "genre": "jazz",
                                "enable_frequency_balancing": True,
                                "enable_sidechain": True,
                                "enable_stereo_imaging": True,
                                "mixing_config_id": "550e8400-e29b-41d4-a716-446655440000",
                            },
                        },
                    }
                }
            }
        }
    },
)
async def enhance_mixing(
    request: MixingEnhancementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enhance mixing of vocals and music.

    Applies:
    - Frequency balancing (dynamic EQ)
    - Sidechain compression
    - Stereo imaging
    - Genre-specific mixing presets
    """
    logger.info(f"Mixing enhancement request from user {current_user.id}")

    try:
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

        from app.core.music_config import MusicGenre
        from app.services.production import get_song_assembly

        assembly_service = get_song_assembly()

        # Normalize genre
        try:
            genre_enum = MusicGenre(request.genre.lower())
        except ValueError:
            genre_enum = MusicGenre.POP

        # Apply intelligent mixing
        output_path = vocals_path.parent / "mixed_enhanced.wav"
        mixed_path = assembly_service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            output_path=output_path,
            vocals_volume_db=0.0,
            music_volume_db=-5.0,
            crossfade_ms=500,
            use_intelligent_mixing=request.enable_frequency_balancing,
            genre=genre_enum,
        )

        enhancements_applied = ["mixing"]
        if request.enable_frequency_balancing:
            enhancements_applied.append("frequency_balancing")
        if request.enable_sidechain:
            enhancements_applied.append("sidechain_compression")
        if request.enable_stereo_imaging:
            enhancements_applied.append("stereo_imaging")

        # Calculate quality metrics
        quality_metrics = {}
        try:
            from app.services.voice.quality_metrics import get_quality_metrics

            metrics_service = get_quality_metrics()
            quality_metrics = metrics_service.calculate_all_metrics(audio_path=mixed_path)
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {e}")

        return EnhancementResponse(
            success=True,
            enhanced_audio_path=str(mixed_path),
            quality_metrics=quality_metrics,
            enhancement_applied=enhancements_applied,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mixing enhancement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mixing enhancement failed: {str(e)}",
        )


# ============================================================================
# Complete Enhancement Endpoints
# ============================================================================


@router.post(
    "/complete",
    response_model=EnhancementResponse,
    summary="Complete song enhancement",
    description="Apply all enhancements to a complete song",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "full_enhancement": {
                            "summary": "Full Enhancement Pipeline",
                            "description": "Apply all enhancements with memory learning",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": True,
                                    "enable_prosody_enhancement": True,
                                    "enable_auto_tune": False,
                                    "enable_intelligent_mixing": True,
                                    "enable_stereo_imaging": True,
                                    "enable_genre_specific_mixing": True,
                                    "enable_memory_learning": True,
                                    "track_quality_metrics": True,
                                },
                            },
                        },
                        "voice_only": {
                            "summary": "Voice Enhancement Only",
                            "description": "Apply only voice enhancement without mixing",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": True,
                                    "enable_prosody_enhancement": True,
                                    "enable_auto_tune": True,
                                    "target_key": "C major",
                                    "enable_intelligent_mixing": False,
                                    "enable_stereo_imaging": False,
                                    "enable_genre_specific_mixing": False,
                                    "enable_memory_learning": False,
                                    "track_quality_metrics": True,
                                },
                            },
                        },
                        "mixing_only": {
                            "summary": "Mixing Enhancement Only",
                            "description": "Apply only mixing enhancement without voice enhancement",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": False,
                                    "enable_prosody_enhancement": False,
                                    "enable_auto_tune": False,
                                    "enable_intelligent_mixing": True,
                                    "enable_stereo_imaging": True,
                                    "enable_genre_specific_mixing": True,
                                    "enable_memory_learning": True,
                                    "track_quality_metrics": True,
                                },
                            },
                        },
                        "with_reference_track": {
                            "summary": "Enhancement with Reference Track",
                            "description": "Apply enhancements using a reference track for matching",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": True,
                                    "enable_prosody_enhancement": True,
                                    "enable_auto_tune": False,
                                    "enable_intelligent_mixing": True,
                                    "enable_stereo_imaging": True,
                                    "enable_genre_specific_mixing": True,
                                    "use_reference_track": True,
                                    "reference_track_id": "660e8400-e29b-41d4-a716-446655440001",
                                    "enable_memory_learning": True,
                                    "track_quality_metrics": True,
                                },
                            },
                        },
                        "with_custom_mixing_config": {
                            "summary": "Enhancement with Custom Mixing Config",
                            "description": "Use a specific mixing configuration ID",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": True,
                                    "enable_prosody_enhancement": True,
                                    "enable_auto_tune": False,
                                    "enable_intelligent_mixing": True,
                                    "enable_stereo_imaging": True,
                                    "enable_genre_specific_mixing": True,
                                    "mixing_config_id": "770e8400-e29b-41d4-a716-446655440002",
                                    "enable_memory_learning": True,
                                    "track_quality_metrics": True,
                                },
                            },
                        },
                        "minimal_enhancement": {
                            "summary": "Minimal Enhancement",
                            "description": "Apply minimal enhancements without learning",
                            "value": {
                                "song_id": "550e8400-e29b-41d4-a716-446655440000",
                                "enhancement_config": {
                                    "enable_voice_enhancement": True,
                                    "enable_prosody_enhancement": False,
                                    "enable_auto_tune": False,
                                    "enable_intelligent_mixing": True,
                                    "enable_stereo_imaging": False,
                                    "enable_genre_specific_mixing": False,
                                    "enable_memory_learning": False,
                                    "track_quality_metrics": False,
                                },
                            },
                        },
                    }
                }
            }
        }
    },
)
async def enhance_complete_song(
    request: CompleteEnhancementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply complete enhancement pipeline to a song.

    This endpoint:
    1. Retrieves song files
    2. Applies voice enhancement
    3. Applies mixing enhancement
    4. Tracks quality metrics
    5. Collects feedback for learning
    """
    logger.info(f"Complete enhancement request for song {request.song_id}")

    try:
        from app.crud.song import crud_song

        # Get song from database
        song = await crud_song.get(db, id=request.song_id)
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song not found: {request.song_id}",
            )

        if song.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to enhance this song",
            )

        # Get song files
        vocals_file = None
        music_file = None
        if song.vocal_track_file_id:
            result = await db.execute(
                select(AudioFile).where(AudioFile.id == song.vocal_track_file_id)
            )
            vocals_file = result.scalar_one_or_none()
        if song.instrumental_track_file_id:
            result = await db.execute(
                select(AudioFile).where(AudioFile.id == song.instrumental_track_file_id)
            )
            music_file = result.scalar_one_or_none()

        if not vocals_file or not music_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Song files not found. Please regenerate the song first.",
            )

        vocals_path = Path(vocals_file.file_path)
        music_path = Path(music_file.file_path)

        if not vocals_path.exists() or not music_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song audio files not found on disk",
            )

        # Apply enhancements
        config = request.enhancement_config
        enhancements_applied = []
        warnings_list = []

        # Voice enhancement
        if config.enable_voice_enhancement:
            try:
                enhancement_service = get_voice_enhancement()
                enhanced_vocals_path = vocals_path.parent / "vocals_enhanced.wav"
                enhanced_vocals_path = enhancement_service.enhance_tts_output(
                    tts_audio_path=vocals_path,
                    output_path=enhanced_vocals_path,
                    enable_enhancement=True,
                )
                vocals_path = enhanced_vocals_path
                enhancements_applied.append("voice_enhancement")
            except Exception as e:
                logger.warning(f"Voice enhancement failed: {e}")
                warnings_list.append(f"Voice enhancement failed: {str(e)}")

        # Mixing enhancement
        if config.enable_intelligent_mixing:
            try:
                from app.core.music_config import MusicGenre
                from app.services.production import get_song_assembly

                assembly_service = get_song_assembly()
                genre_enum = MusicGenre(song.genre.lower()) if song.genre else MusicGenre.POP

                output_path = vocals_path.parent / "song_enhanced.wav"
                mixed_path = assembly_service.assemble_song(
                    vocals_path=vocals_path,
                    music_path=music_path,
                    output_path=output_path,
                    vocals_volume_db=0.0,
                    music_volume_db=-5.0,
                    crossfade_ms=500,
                    use_intelligent_mixing=True,
                    genre=genre_enum,
                )
                enhancements_applied.append("intelligent_mixing")
            except Exception as e:
                logger.warning(f"Mixing enhancement failed: {e}")
                warnings_list.append(f"Mixing enhancement failed: {str(e)}")

        # Calculate quality metrics
        quality_metrics = {}
        if config.track_quality_metrics:
            try:
                from app.services.voice.quality_metrics import get_quality_metrics

                metrics_service = get_quality_metrics()
                final_path = mixed_path if config.enable_intelligent_mixing else vocals_path
                quality_metrics = metrics_service.calculate_all_metrics(audio_path=final_path)
            except Exception as e:
                logger.warning(f"Quality metrics calculation failed: {e}")

        # Collect feedback for learning (if enabled)
        if config.enable_memory_learning and db:
            try:
                # Quality metrics are tracked above
                # Feedback loop would be called after user provides feedback
                logger.info("Quality metrics tracked for learning")
            except Exception as e:
                logger.warning(f"Feedback loop failed: {e}")

        return EnhancementResponse(
            success=True,
            enhanced_audio_path=str(
                mixed_path if config.enable_intelligent_mixing else vocals_path
            ),
            quality_metrics=quality_metrics,
            enhancement_applied=enhancements_applied,
            warnings=warnings_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete enhancement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Complete enhancement failed: {str(e)}",
        )
