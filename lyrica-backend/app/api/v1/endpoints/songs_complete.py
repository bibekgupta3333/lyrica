"""
Complete Song Generation API Endpoints.

This module implements all song generation endpoints as specified in WBS 2.14:
- Generate complete songs (lyrics + vocals + music)
- Retrieve, download, and stream songs
- Regenerate vocals or music
- Update settings and remix songs
- List available voices and genres
"""

import time
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import get_orchestrator
from app.core.music_config import MusicGenre, MusicKey, get_genre_bpm_range, get_genre_instruments
from app.core.voice_config import list_voice_profiles
from app.crud.song import crud_song
from app.db.session import get_db
from app.schemas.song import (
    CompleteSongGenerationRequest,
    MusicGenreInfo,
    QuickSongRequest,
    RegenerateMusicRequest,
    RegenerateVocalsRequest,
    RemixSongRequest,
    SongListResponse,
    SongResponse,
    UpdateSongSettingsRequest,
    VoiceProfileInfo,
)
from app.services.music import get_music_generation
from app.services.production import get_song_assembly, get_song_mastering
from app.services.voice import get_voice_synthesis

router = APIRouter(prefix="/songs", tags=["Complete Songs"])


# ============================================================================
# Helper Functions
# ============================================================================


def get_current_user_id() -> uuid.UUID:
    """
    Get current authenticated user ID.

    TODO: Replace with actual auth dependency
    """
    # Placeholder - replace with actual auth
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


async def _generate_song_files(
    song_id: uuid.UUID,
    lyrics_text: str,
    voice_profile_id: str,
    genre: str,
    bpm: int,
    key: str,
    duration: int,
    vocal_pitch_shift: int = 0,
    vocal_effects: Optional[dict] = None,
) -> dict:
    """Internal function to generate all song audio files."""
    base_path = Path("audio_files/songs") / str(song_id)
    base_path.mkdir(parents=True, exist_ok=True)

    # Initialize services
    voice_service = get_voice_synthesis()
    music_service = get_music_generation()
    assembly_service = get_song_assembly()
    mastering_service = get_song_mastering()

    # Step 1: Generate vocals
    logger.info(f"Step 1/5: Generating vocals for song {song_id}")
    from app.core.voice_config import get_voice_profile

    voice_profile = get_voice_profile(voice_profile_id)
    vocals_path = base_path / "vocals.wav"
    voice_service.synthesize_lyrics(
        lyrics=lyrics_text,
        voice_profile=voice_profile,
        output_path=vocals_path,
        chunk_by_sentences=True,
    )

    # Apply vocal effects if specified
    if vocal_effects or vocal_pitch_shift != 0:
        from app.services.voice import get_pitch_control, get_vocal_effects

        # Apply pitch shift
        if vocal_pitch_shift != 0:
            pitch_service = get_pitch_control()
            vocals_path = pitch_service.adjust_pitch(
                audio_path=vocals_path, semitones=vocal_pitch_shift, output_path=vocals_path
            )

        # Apply effects
        if vocal_effects:
            effects_service = get_vocal_effects()
            effects_service.apply_effects(
                audio_path=vocals_path, effects=vocal_effects, output_path=vocals_path
            )

    # Step 2: Generate music
    logger.info(f"Step 2/5: Generating instrumental music for song {song_id}")
    music_path = base_path / "music.wav"
    music_service.generate_by_genre(
        genre=genre, mood=None, key=key, bpm=bpm, duration=duration, output_path=music_path
    )

    # Step 3: Mix vocals and music
    logger.info(f"Step 3/5: Mixing vocals and music for song {song_id}")
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
    logger.info(f"Step 4/5: Applying final mastering for song {song_id}")
    final_path = base_path / f"{song_id}.wav"
    mastering_service.master_song(song_path=mixed_path, output_path=final_path, genre=genre)

    # Step 5: Create preview
    logger.info(f"Step 5/5: Creating preview for song {song_id}")
    preview_path = base_path / f"{song_id}_preview.wav"
    assembly_service.create_song_preview(
        song_path=final_path, preview_duration=30, output_path=preview_path
    )

    # Get file info
    from pydub import AudioSegment

    audio = AudioSegment.from_file(str(final_path))

    return {
        "final_path": str(final_path),
        "vocals_path": str(vocals_path),
        "music_path": str(music_path),
        "preview_path": str(preview_path),
        "duration": len(audio) / 1000.0,
        "file_size": final_path.stat().st_size,
    }


# ============================================================================
# WBS 2.14.1: POST /api/v1/songs/generate - Generate complete song
# ============================================================================


@router.post(
    "/generate",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate complete song from scratch",
    description="Generate lyrics, vocals, and music in one workflow (WBS 2.14.1)",
)
async def generate_complete_song(
    request: CompleteSongGenerationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a complete song from scratch.

    This is the master endpoint that generates:
    1. Song lyrics using AI agents (LangGraph)
    2. Vocals from lyrics (TTS + effects)
    3. Instrumental music (MusicGen)
    4. Mixed and mastered final song

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/songs/generate" \\
             -H "Content-Type: application/json" \\
             -d '{
                 "lyrics_prompt": "Write a sad song about lost love",
                 "genre": "pop",
                 "mood": "melancholic",
                 "voice_profile_id": "female_singer_1",
                 "bpm": 80,
                 "key": "C minor",
                 "duration_seconds": 180
             }'
        ```
    """
    try:
        start_time = time.time()
        user_id = get_current_user_id()

        logger.info(f"Starting complete song generation for user {user_id}")

        # Step 1: Generate lyrics using agents
        logger.info("Step 1/6: Generating lyrics with AI agents")
        orchestrator = get_orchestrator(
            llm_provider=request.llm_provider, quality_threshold=6.5, max_refinement_iterations=2
        )

        lyrics_result = await orchestrator.generate_song(
            user_id=int(user_id.int & 0xFFFFFFFF),  # Convert UUID to int for agent
            prompt=request.lyrics_prompt,
            genre=request.genre,
            mood=request.mood,
            theme=request.theme,
            use_rag=request.use_rag,
            max_retries=2,
        )

        if not lyrics_result.final_lyrics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate lyrics",
            )

        lyrics_text = lyrics_result.final_lyrics

        # Step 2: Create song record
        logger.info("Step 2/6: Creating song record")
        song = await crud_song.create(db=db, user_id=user_id, obj_in=request, lyrics_id=None)

        # Update title
        if request.title:
            song.title = request.title
        elif lyrics_result.title:
            song.title = lyrics_result.title

        # Set defaults
        genre = request.genre or "pop"
        bpm = request.bpm or 120
        key = request.key or "C major"

        # Step 3-6: Generate all audio files
        logger.info("Steps 3-6/6: Generating audio files")
        file_info = await _generate_song_files(
            song_id=song.id,
            lyrics_text=lyrics_text,
            voice_profile_id=request.voice_profile_id,
            genre=genre,
            bpm=bpm,
            key=key,
            duration=request.duration_seconds,
            vocal_pitch_shift=request.vocal_pitch_shift,
            vocal_effects=request.vocal_effects,
        )

        # Update song with file info
        song.duration_seconds = file_info["duration"]
        song.bpm = bpm
        song.key = key
        song.genre = genre

        # Update status
        await crud_song.update_status(db, song.id, "completed", completed=True)

        generation_time = time.time() - start_time

        logger.success(
            f"Complete song generated in {generation_time:.2f}s: {song.id} - {song.title}"
        )

        # Build response
        from app.schemas.song import SongFileInfo, SongQualityMetrics, SongStatistics

        return SongResponse(
            id=song.id,
            user_id=song.user_id,
            lyrics_id=song.lyrics_id,
            title=song.title,
            artist_name=song.artist_name,
            genre=song.genre,
            mood=song.mood,
            bpm=song.bpm,
            key=song.key,
            duration_seconds=song.duration_seconds,
            voice_profile_id=song.voice_profile_id,
            music_style=song.music_style,
            vocal_pitch_shift=song.vocal_pitch_shift,
            vocal_effects=song.vocal_effects,
            music_params=song.music_params,
            final_audio_file_id=song.final_audio_file_id,
            vocal_track_file_id=song.vocal_track_file_id,
            instrumental_track_file_id=song.instrumental_track_file_id,
            file_info=SongFileInfo(
                final_audio_path=file_info["final_path"],
                vocal_track_path=file_info["vocals_path"],
                instrumental_track_path=file_info["music_path"],
                preview_path=file_info["preview_path"],
                file_size_bytes=file_info["file_size"],
                duration_seconds=file_info["duration"],
            ),
            quality_metrics=SongQualityMetrics(
                audio_quality_score=song.audio_quality_score,
                mixing_quality_score=song.mixing_quality_score,
                overall_rating=song.overall_rating,
            ),
            statistics=SongStatistics(
                play_count=song.play_count,
                download_count=song.download_count,
                share_count=song.share_count,
                like_count=song.like_count,
            ),
            generation_status=song.generation_status,
            is_public=song.is_public,
            created_at=song.created_at,
            updated_at=song.updated_at,
            completed_at=song.completed_at,
            published_at=song.published_at,
        )

    except Exception as e:
        logger.error(f"Error generating complete song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate complete song: {str(e)}",
        )


# ============================================================================
# Quick Generation (Simplified)
# ============================================================================


@router.post(
    "/generate-quick",
    response_model=SongResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Quick song generation with minimal parameters",
)
async def generate_quick_song(
    request: QuickSongRequest,
    db: AsyncSession = Depends(get_db),
):
    """Quick song generation with simplified parameters."""
    # Convert to full request
    full_request = CompleteSongGenerationRequest(
        lyrics_prompt=request.prompt,
        genre=request.genre,
        voice_profile_id=request.voice,
        duration_seconds=request.duration,
        bpm=None,
        key=None,
    )

    return await generate_complete_song(full_request, db)


# ============================================================================
# WBS 2.14.5: GET /api/v1/songs/{id} - Retrieve song
# ============================================================================


@router.get(
    "/{song_id}",
    response_model=SongResponse,
    summary="Retrieve song by ID",
    description="Get complete song information including metadata and file paths (WBS 2.14.5)",
)
async def get_song(
    song_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve song by ID."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    # Check permissions
    if song.user_id != user_id and not song.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this song"
        )

    from app.schemas.song import SongFileInfo, SongQualityMetrics, SongStatistics

    # Build file paths
    base_path = Path("audio_files/songs") / str(song.id)
    final_path = base_path / f"{song.id}.wav"
    vocals_path = base_path / "vocals.wav"
    music_path = base_path / "music.wav"
    preview_path = base_path / f"{song.id}_preview.wav"

    return SongResponse(
        id=song.id,
        user_id=song.user_id,
        lyrics_id=song.lyrics_id,
        title=song.title,
        artist_name=song.artist_name,
        genre=song.genre,
        mood=song.mood,
        bpm=song.bpm,
        key=song.key,
        duration_seconds=song.duration_seconds,
        voice_profile_id=song.voice_profile_id,
        music_style=song.music_style,
        vocal_pitch_shift=song.vocal_pitch_shift,
        vocal_effects=song.vocal_effects,
        music_params=song.music_params,
        final_audio_file_id=song.final_audio_file_id,
        vocal_track_file_id=song.vocal_track_file_id,
        instrumental_track_file_id=song.instrumental_track_file_id,
        file_info=SongFileInfo(
            final_audio_path=str(final_path) if final_path.exists() else None,
            vocal_track_path=str(vocals_path) if vocals_path.exists() else None,
            instrumental_track_path=str(music_path) if music_path.exists() else None,
            preview_path=str(preview_path) if preview_path.exists() else None,
            file_size_bytes=final_path.stat().st_size if final_path.exists() else None,
            duration_seconds=song.duration_seconds,
        ),
        quality_metrics=SongQualityMetrics(
            audio_quality_score=song.audio_quality_score,
            mixing_quality_score=song.mixing_quality_score,
            overall_rating=song.overall_rating,
        ),
        statistics=SongStatistics(
            play_count=song.play_count,
            download_count=song.download_count,
            share_count=song.share_count,
            like_count=song.like_count,
        ),
        generation_status=song.generation_status,
        is_public=song.is_public,
        created_at=song.created_at,
        updated_at=song.updated_at,
        completed_at=song.completed_at,
        published_at=song.published_at,
    )


# ============================================================================
# WBS 2.14.6: GET /api/v1/songs/{id}/download - Download song file
# ============================================================================


@router.get(
    "/{song_id}/download",
    summary="Download song file",
    description="Download the final song audio file (WBS 2.14.6)",
    response_class=FileResponse,
)
async def download_song(
    song_id: uuid.UUID,
    format: str = Query(default="wav", description="Audio format (wav, mp3, ogg, flac, m4a)"),
    db: AsyncSession = Depends(get_db),
):
    """Download song file in specified format."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    # Check permissions
    if song.user_id != user_id and not song.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this song"
        )

    # Get file path
    base_path = Path("audio_files/songs") / str(song.id)
    audio_file = base_path / f"{song.id}.wav"

    if not audio_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song audio file not found"
        )

    # Convert format if needed
    if format != "wav":
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(audio_file))
        output_file = base_path / f"{song.id}.{format}"

        # Export in requested format
        audio.export(str(output_file), format=format, bitrate="320k" if format == "mp3" else None)

        audio_file = output_file

    # Increment download count
    await crud_song.increment_download_count(db, song_id)

    # Sanitize filename
    safe_title = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in song.title)
    filename = f"{safe_title}.{format}"

    return FileResponse(
        path=audio_file,
        media_type=f"audio/{format}",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================================
# WBS 2.14.7: GET /api/v1/songs/{id}/stream - Stream song
# ============================================================================


@router.get(
    "/{song_id}/stream",
    summary="Stream song audio",
    description="Stream song audio file (WBS 2.14.7)",
)
async def stream_song(
    song_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Stream song audio."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    # Check permissions
    if song.user_id != user_id and not song.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this song"
        )

    # Get file path
    base_path = Path("audio_files/songs") / str(song.id)
    audio_file = base_path / f"{song.id}.wav"

    if not audio_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song audio file not found"
        )

    # Increment play count
    await crud_song.increment_play_count(db, song_id)

    # Stream file
    def iter_file():
        with open(audio_file, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(iter_file(), media_type="audio/wav")


# ============================================================================
# WBS 2.14.8: POST /api/v1/songs/{id}/regenerate-vocals - Re-generate vocals
# ============================================================================


@router.post(
    "/{song_id}/regenerate-vocals",
    response_model=SongResponse,
    summary="Regenerate song vocals",
    description="Regenerate vocals with new voice or settings (WBS 2.14.8)",
)
async def regenerate_vocals(
    song_id: uuid.UUID,
    request: RegenerateVocalsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Regenerate vocals for existing song."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    if song.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        logger.info(f"Regenerating vocals for song {song_id}")

        # Get lyrics (placeholder - would fetch from database)
        # For now, use a sample
        lyrics_text = "Sample lyrics for regeneration"

        # Use current or new settings
        voice_profile_id = request.voice_profile_id or "female_singer_1"
        vocal_pitch_shift = (
            request.vocal_pitch_shift
            if request.vocal_pitch_shift is not None
            else song.vocal_pitch_shift
        )
        vocal_effects = request.vocal_effects if request.vocal_effects else song.vocal_effects

        # Regenerate vocals
        base_path = Path("audio_files/songs") / str(song.id)
        voice_service = get_voice_synthesis()
        from app.core.voice_config import get_voice_profile

        voice_profile = get_voice_profile(voice_profile_id)
        vocals_path = base_path / "vocals.wav"

        voice_service.synthesize_lyrics(
            lyrics=lyrics_text,
            voice_profile=voice_profile,
            output_path=vocals_path,
            chunk_by_sentences=True,
        )

        # Apply effects
        if vocal_pitch_shift != 0:
            from app.services.voice import get_pitch_control

            pitch_service = get_pitch_control()
            pitch_service.adjust_pitch(
                audio_path=vocals_path, semitones=vocal_pitch_shift, output_path=vocals_path
            )

        # Remix with new vocals
        music_path = base_path / "music.wav"
        mixed_path = base_path / "mixed.wav"

        assembly_service = get_song_assembly()
        assembly_service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            output_path=mixed_path,
            vocals_volume_db=0.0,
            music_volume_db=-5.0,
        )

        # Remaster
        final_path = base_path / f"{song.id}.wav"
        mastering_service = get_song_mastering()
        mastering_service.master_song(
            song_path=mixed_path, output_path=final_path, genre=song.genre or "pop"
        )

        # Update song
        song.vocal_pitch_shift = vocal_pitch_shift
        song.vocal_effects = vocal_effects
        await db.commit()

        logger.success(f"Vocals regenerated for song {song_id}")

        return await get_song(song_id, db)

    except Exception as e:
        logger.error(f"Error regenerating vocals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate vocals: {str(e)}",
        )


# ============================================================================
# WBS 2.14.9: POST /api/v1/songs/{id}/regenerate-music - Re-generate music
# ============================================================================


@router.post(
    "/{song_id}/regenerate-music",
    response_model=SongResponse,
    summary="Regenerate song music",
    description="Regenerate instrumental music with new settings (WBS 2.14.9)",
)
async def regenerate_music(
    song_id: uuid.UUID,
    request: RegenerateMusicRequest,
    db: AsyncSession = Depends(get_db),
):
    """Regenerate music for existing song."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    if song.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        logger.info(f"Regenerating music for song {song_id}")

        # Use current or new settings
        genre = request.genre or song.genre or "pop"
        bpm = request.bpm or song.bpm or 120
        key = request.key or song.key or "C major"
        duration = int(song.duration_seconds or 180)

        # Regenerate music
        base_path = Path("audio_files/songs") / str(song.id)
        music_service = get_music_generation()
        music_path = base_path / "music.wav"

        music_service.generate_by_genre(
            genre=genre, mood=None, key=key, bpm=bpm, duration=duration, output_path=music_path
        )

        # Remix with new music
        vocals_path = base_path / "vocals.wav"
        mixed_path = base_path / "mixed.wav"

        assembly_service = get_song_assembly()
        assembly_service.assemble_song(
            vocals_path=vocals_path,
            music_path=music_path,
            output_path=mixed_path,
            vocals_volume_db=0.0,
            music_volume_db=-5.0,
        )

        # Remaster
        final_path = base_path / f"{song.id}.wav"
        mastering_service = get_song_mastering()
        mastering_service.master_song(song_path=mixed_path, output_path=final_path, genre=genre)

        # Update song
        song.genre = genre
        song.bpm = bpm
        song.key = key
        await db.commit()

        logger.success(f"Music regenerated for song {song_id}")

        return await get_song(song_id, db)

    except Exception as e:
        logger.error(f"Error regenerating music: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate music: {str(e)}",
        )


# ============================================================================
# WBS 2.14.10: PUT /api/v1/songs/{id}/settings - Update audio settings
# ============================================================================


@router.put(
    "/{song_id}/settings",
    response_model=SongResponse,
    summary="Update song settings",
    description="Update song metadata and settings (WBS 2.14.10)",
)
async def update_song_settings(
    song_id: uuid.UUID,
    request: UpdateSongSettingsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update song settings."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    if song.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Update song
    updated_song = await crud_song.update(db, song_id, request)

    if not updated_song:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update song"
        )

    logger.info(f"Updated settings for song {song_id}")

    return await get_song(song_id, db)


# ============================================================================
# WBS 2.14.13: POST /api/v1/songs/{id}/remix - Remix existing song
# ============================================================================


@router.post(
    "/{song_id}/remix",
    response_model=SongResponse,
    summary="Remix existing song",
    description="Create a remix with new vocals and/or music (WBS 2.14.13)",
)
async def remix_song(
    song_id: uuid.UUID,
    request: RemixSongRequest,
    db: AsyncSession = Depends(get_db),
):
    """Remix existing song with new settings."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    if song.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        logger.info(f"Remixing song {song_id}")

        # Regenerate vocals if requested
        if request.voice_profile_id or request.vocal_effects:
            regen_vocals_req = RegenerateVocalsRequest(
                voice_profile_id=request.voice_profile_id,
                vocal_pitch_shift=request.vocal_pitch_shift,
                vocal_effects=request.vocal_effects,
            )
            await regenerate_vocals(song_id, regen_vocals_req, db)

        # Regenerate music if requested
        if request.genre or request.bpm or request.key:
            regen_music_req = RegenerateMusicRequest(
                genre=request.genre, bpm=request.bpm, key=request.key
            )
            await regenerate_music(song_id, regen_music_req, db)

        # Apply custom mixing if specified
        if request.vocals_volume_db != 0.0 or request.music_volume_db != -5.0:
            base_path = Path("audio_files/songs") / str(song.id)
            vocals_path = base_path / "vocals.wav"
            music_path = base_path / "music.wav"
            mixed_path = base_path / "mixed.wav"
            final_path = base_path / f"{song.id}.wav"

            assembly_service = get_song_assembly()
            assembly_service.assemble_song(
                vocals_path=vocals_path,
                music_path=music_path,
                output_path=mixed_path,
                vocals_volume_db=request.vocals_volume_db,
                music_volume_db=request.music_volume_db,
            )

            mastering_service = get_song_mastering()
            mastering_service.master_song(
                song_path=mixed_path, output_path=final_path, genre=song.genre or "pop"
            )

        logger.success(f"Song {song_id} remixed successfully")

        return await get_song(song_id, db)

    except Exception as e:
        logger.error(f"Error remixing song: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remix song: {str(e)}",
        )


# ============================================================================
# List Endpoints
# ============================================================================


@router.get(
    "",
    response_model=SongListResponse,
    summary="List user songs",
    description="Get list of user's songs with pagination",
)
async def list_user_songs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    genre: Optional[str] = Query(default=None, description="Filter by genre"),
    db: AsyncSession = Depends(get_db),
):
    """List user's songs."""
    user_id = get_current_user_id()

    songs = await crud_song.get_by_user(
        db, user_id, skip=skip, limit=limit, status=status, genre=genre
    )
    total = await crud_song.count_by_user(db, user_id, status=status)

    from app.schemas.song import SongFileInfo, SongQualityMetrics, SongStatistics

    song_responses = [
        SongResponse(
            id=song.id,
            user_id=song.user_id,
            lyrics_id=song.lyrics_id,
            title=song.title,
            artist_name=song.artist_name,
            genre=song.genre,
            mood=song.mood,
            bpm=song.bpm,
            key=song.key,
            duration_seconds=song.duration_seconds,
            voice_profile_id=song.voice_profile_id,
            music_style=song.music_style,
            vocal_pitch_shift=song.vocal_pitch_shift,
            vocal_effects=song.vocal_effects,
            music_params=song.music_params,
            final_audio_file_id=song.final_audio_file_id,
            vocal_track_file_id=song.vocal_track_file_id,
            instrumental_track_file_id=song.instrumental_track_file_id,
            file_info=SongFileInfo(),
            quality_metrics=SongQualityMetrics(),
            statistics=SongStatistics(
                play_count=song.play_count,
                download_count=song.download_count,
                share_count=song.share_count,
                like_count=song.like_count,
            ),
            generation_status=song.generation_status,
            is_public=song.is_public,
            created_at=song.created_at,
            updated_at=song.updated_at,
            completed_at=song.completed_at,
            published_at=song.published_at,
        )
        for song in songs
    ]

    return SongListResponse(
        songs=song_responses,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.get(
    "/public/trending",
    response_model=List[SongResponse],
    summary="Get trending public songs",
)
async def get_trending_songs(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get trending public songs."""
    songs = await crud_song.get_trending(db, limit=limit)

    from app.schemas.song import SongFileInfo, SongQualityMetrics, SongStatistics

    return [
        SongResponse(
            id=song.id,
            user_id=song.user_id,
            lyrics_id=song.lyrics_id,
            title=song.title,
            artist_name=song.artist_name,
            genre=song.genre,
            mood=song.mood,
            bpm=song.bpm,
            key=song.key,
            duration_seconds=song.duration_seconds,
            voice_profile_id=song.voice_profile_id,
            music_style=song.music_style,
            vocal_pitch_shift=song.vocal_pitch_shift,
            vocal_effects=song.vocal_effects,
            music_params=song.music_params,
            final_audio_file_id=song.final_audio_file_id,
            vocal_track_file_id=song.vocal_track_file_id,
            instrumental_track_file_id=song.instrumental_track_file_id,
            file_info=SongFileInfo(),
            quality_metrics=SongQualityMetrics(),
            statistics=SongStatistics(
                play_count=song.play_count,
                download_count=song.download_count,
                share_count=song.share_count,
                like_count=song.like_count,
            ),
            generation_status=song.generation_status,
            is_public=song.is_public,
            created_at=song.created_at,
            updated_at=song.updated_at,
            completed_at=song.completed_at,
            published_at=song.published_at,
        )
        for song in songs
    ]


# ============================================================================
# WBS 2.14.11: GET /api/v1/voice/profiles - List available voices
# (Note: This is actually better placed in the voice endpoints, but included
# here for WBS 2.14 completeness)
# ============================================================================


@router.get(
    "/metadata/voices",
    response_model=List[VoiceProfileInfo],
    summary="List available voice profiles",
    description="Get list of available voice profiles for song generation (WBS 2.14.11)",
)
async def list_voices():
    """List available voice profiles."""
    profiles = list_voice_profiles()

    return [
        VoiceProfileInfo(
            id=profile.id,
            name=profile.name,
            gender=profile.gender.value,
            language=profile.language,
            description=profile.description,
            style=profile.style.value if profile.style else None,
        )
        for profile in profiles
    ]


# ============================================================================
# WBS 2.14.12: GET /api/v1/music/genres - List available music genres
# (Note: This is better placed in music endpoints, but included here for
# WBS 2.14 completeness)
# ============================================================================


@router.get(
    "/metadata/genres",
    response_model=List[MusicGenreInfo],
    summary="List available music genres",
    description="Get list of available music genres for song generation (WBS 2.14.12)",
)
async def list_genres():
    """List available music genres."""
    genres = []

    for genre in MusicGenre:
        bpm_range = get_genre_bpm_range(genre)
        instruments = get_genre_instruments(genre)
        keys = list(MusicKey)[:5]  # First 5 keys as common

        genres.append(
            MusicGenreInfo(
                id=genre.value,
                name=genre.value.title(),
                description=f"{genre.value.title()} music style",
                typical_bpm_range=f"{bpm_range[0]}-{bpm_range[1]} BPM",
                common_keys=[k.value for k in keys],
                typical_instruments=instruments,
            )
        )

    return genres


@router.delete(
    "/{song_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete song",
    description="Delete a song and all its associated files",
)
async def delete_song(
    song_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete song."""
    user_id = get_current_user_id()
    song = await crud_song.get(db, song_id)

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found"
        )

    if song.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Delete files
    base_path = Path("audio_files/songs") / str(song.id)
    if base_path.exists():
        import shutil

        shutil.rmtree(base_path)

    # Delete from database
    await crud_song.delete(db, song_id)

    logger.info(f"Deleted song {song_id}")
