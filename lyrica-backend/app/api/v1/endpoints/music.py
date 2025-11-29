"""
Music generation API endpoints.

This module provides REST API endpoints for AI-powered music generation,
chord progressions, melody creation, and music composition.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.music_config import (
    MusicGenre,
    MusicKey,
    MusicMood,
    MusicStructure,
    get_genre_bpm_range,
)
from app.services.music import get_chord_service, get_melody_service, get_music_generation

router = APIRouter(prefix="/music", tags=["Music Generation"])


# Request/Response Models
class GenerateMusicRequest(BaseModel):
    """Request to generate music from text prompt."""

    prompt: str = Field(..., max_length=200, description="Text description of music")
    duration: int = Field(default=30, ge=5, le=300, description="Duration in seconds")
    temperature: float = Field(default=1.0, ge=0.5, le=2.0, description="Creativity")


class GenerateByGenreRequest(BaseModel):
    """Request to generate genre-specific music."""

    genre: MusicGenre = Field(..., description="Music genre")
    mood: Optional[MusicMood] = Field(default=None, description="Music mood")
    key: Optional[MusicKey] = Field(default=None, description="Musical key")
    bpm: Optional[int] = Field(default=None, ge=40, le=200, description="Tempo (BPM)")
    duration: int = Field(default=30, ge=5, le=300, description="Duration in seconds")


class GenerateInstrumentalRequest(BaseModel):
    """Request to generate instrumental music."""

    instruments: list[str] = Field(..., description="List of instruments")
    genre: Optional[MusicGenre] = Field(default=None)
    duration: int = Field(default=30, ge=5, le=300)


class StructuredMusicRequest(BaseModel):
    """Request to generate structured music."""

    sections: list[tuple[str, int]] = Field(
        ..., description="List of (section_name, duration) tuples"
    )
    genre: MusicGenre
    key: Optional[MusicKey] = Field(default=None)
    bpm: Optional[int] = Field(default=None)


class ChordProgressionRequest(BaseModel):
    """Request to generate chord progression."""

    key: MusicKey = Field(..., description="Musical key")
    genre: Optional[MusicGenre] = Field(default=None)
    num_chords: int = Field(default=4, ge=2, le=16, description="Number of chords")


class MelodyGenerationRequest(BaseModel):
    """Request to generate melody."""

    key: MusicKey
    num_notes: int = Field(default=16, ge=4, le=128)
    duration: int = Field(default=8, ge=2, le=60)
    genre: Optional[MusicGenre] = Field(default=None)
    pentatonic: bool = Field(default=False, description="Use pentatonic scale (simpler)")


class MusicGenerationResponse(BaseModel):
    """Music generation response."""

    file_path: str
    duration_seconds: int
    genre: Optional[str]
    key: Optional[str]
    bpm: Optional[int]
    message: str


class ChordProgressionResponse(BaseModel):
    """Chord progression response."""

    chords: list[str]
    key: str
    analysis: dict


# Endpoints
@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(request: GenerateMusicRequest):
    """
    Generate music from text prompt using MusicGen AI.

    Example:
        ```json
        {
            "prompt": "upbeat pop music with piano and drums",
            "duration": 30,
            "temperature": 1.0
        }
        ```
    """
    music_service = get_music_generation()

    try:
        audio_path = music_service.generate_music(
            prompt=request.prompt,
            duration=request.duration,
            temperature=request.temperature,
        )

        return MusicGenerationResponse(
            file_path=str(audio_path),
            duration_seconds=request.duration,
            genre=None,
            key=None,
            bpm=None,
            message="Music generated successfully from prompt",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Music generation failed: {str(e)}",
        )


@router.post("/generate/genre", response_model=MusicGenerationResponse)
async def generate_by_genre(request: GenerateByGenreRequest):
    """
    Generate music for specific genre with mood and key control.

    Example:
        ```json
        {
            "genre": "pop",
            "mood": "happy",
            "key": "C",
            "bpm": 120,
            "duration": 30
        }
        ```
    """
    music_service = get_music_generation()

    try:
        audio_path = music_service.generate_by_genre(
            genre=request.genre,
            mood=request.mood,
            key=request.key,
            bpm=request.bpm,
            duration=request.duration,
        )

        return MusicGenerationResponse(
            file_path=str(audio_path),
            duration_seconds=request.duration,
            genre=request.genre.value,
            key=request.key.value if request.key else None,
            bpm=request.bpm,
            message=f"{request.genre.value.title()} music generated successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Genre-based generation failed: {str(e)}",
        )


@router.post("/generate/instrumental", response_model=MusicGenerationResponse)
async def generate_instrumental(request: GenerateInstrumentalRequest):
    """
    Generate instrumental music with specific instruments.

    Example:
        ```json
        {
            "instruments": ["piano", "violin", "cello"],
            "genre": "classical",
            "duration": 60
        }
        ```
    """
    music_service = get_music_generation()

    try:
        audio_path = music_service.generate_instrumental(
            instruments=request.instruments,
            genre=request.genre,
            duration=request.duration,
        )

        return MusicGenerationResponse(
            file_path=str(audio_path),
            duration_seconds=request.duration,
            genre=request.genre.value if request.genre else None,
            key=None,
            bpm=None,
            message=f"Instrumental with {', '.join(request.instruments)} generated",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Instrumental generation failed: {str(e)}",
        )


@router.post("/generate/structured", response_model=MusicGenerationResponse)
async def generate_structured_music(request: StructuredMusicRequest):
    """
    Generate structured music (intro, verse, chorus, etc.).

    Example:
        ```json
        {
            "sections": [
                ["intro", 8],
                ["verse", 16],
                ["chorus", 16],
                ["verse", 16],
                ["chorus", 16],
                ["outro", 8]
            ],
            "genre": "pop",
            "key": "C",
            "bpm": 120
        }
        ```
    """
    music_service = get_music_generation()

    try:
        audio_path = music_service.generate_structure(
            sections=request.sections, genre=request.genre
        )

        total_duration = sum(duration for _, duration in request.sections)

        return MusicGenerationResponse(
            file_path=str(audio_path),
            duration_seconds=total_duration,
            genre=request.genre.value,
            key=request.key.value if request.key else None,
            bpm=request.bpm,
            message="Structured music generated successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Structured generation failed: {str(e)}",
        )


@router.post("/generate/with-melody")
async def generate_with_melody(
    melody_file: UploadFile = File(...), genre: str = "pop", duration: int = 30
):
    """
    Generate music based on uploaded melody audio.

    Args:
        melody_file: Audio file containing melody
        genre: Music genre
        duration: Duration in seconds

    Returns:
        Generated music file
    """
    music_service = get_music_generation()

    # Save uploaded file
    temp_dir = Path("audio_files/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    melody_path = temp_dir / melody_file.filename
    with open(melody_path, "wb") as f:
        f.write(await melody_file.read())

    try:
        # Parse genre
        try:
            genre_enum = MusicGenre(genre.lower())
        except ValueError:
            genre_enum = MusicGenre.POP

        # Generate with melody
        audio_path = music_service.generate_with_melody(
            melody_audio_path=melody_path,
            genre=genre_enum,
            duration=duration,
        )

        return FileResponse(path=str(audio_path), media_type="audio/wav", filename=audio_path.name)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Melody-based generation failed: {str(e)}",
        )
    finally:
        melody_path.unlink(missing_ok=True)


@router.post("/chords/generate", response_model=ChordProgressionResponse)
async def generate_chord_progression(request: ChordProgressionRequest):
    """
    Generate chord progression for given key and genre.

    Example:
        ```json
        {
            "key": "C",
            "genre": "pop",
            "num_chords": 4
        }
        ```

    Response:
        ```json
        {
            "chords": ["C", "G", "Am", "F"],
            "key": "C",
            "analysis": {
                "num_chords": 4,
                "unique_chords": 4,
                "complexity": "simple"
            }
        }
        ```
    """
    chord_service = get_chord_service()

    try:
        chords = chord_service.generate_progression(
            key=request.key, genre=request.genre, num_chords=request.num_chords
        )

        analysis = chord_service.analyze_progression(chords)

        return ChordProgressionResponse(chords=chords, key=request.key.value, analysis=analysis)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chord generation failed: {str(e)}",
        )


@router.post("/melody/generate")
async def generate_melody(request: MelodyGenerationRequest):
    """
    Generate MIDI melody file.

    Example:
        ```json
        {
            "key": "C",
            "num_notes": 16,
            "duration": 8,
            "genre": "pop",
            "pentatonic": false
        }
        ```

    Returns:
        MIDI file
    """
    melody_service = get_melody_service()

    try:
        if request.pentatonic:
            midi_path = melody_service.generate_pentatonic_melody(
                key=request.key, num_notes=request.num_notes
            )
        else:
            midi_path = melody_service.generate_melody(
                key=request.key,
                num_notes=request.num_notes,
                duration_seconds=request.duration,
                genre=request.genre,
            )

        return FileResponse(path=str(midi_path), media_type="audio/midi", filename=midi_path.name)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Melody generation failed: {str(e)}",
        )


@router.get("/genres")
async def list_genres():
    """Get list of available music genres."""
    return {
        "genres": [genre.value for genre in MusicGenre],
        "count": len(MusicGenre),
    }


@router.get("/keys")
async def list_keys():
    """Get list of available musical keys."""
    return {"keys": [key.value for key in MusicKey], "count": len(MusicKey)}


@router.get("/moods")
async def list_moods():
    """Get list of available music moods."""
    return {"moods": [mood.value for mood in MusicMood], "count": len(MusicMood)}


@router.get("/genres/{genre}/info")
async def get_genre_info(genre: str):
    """
    Get information about a specific genre.

    Returns BPM range, typical instruments, and chord progressions.
    """
    try:
        genre_enum = MusicGenre(genre.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Genre '{genre}' not found"
        )

    min_bpm, max_bpm = get_genre_bpm_range(genre_enum)

    return {
        "genre": genre_enum.value,
        "bpm_range": {"min": min_bpm, "max": max_bpm, "typical": (min_bpm + max_bpm) // 2},
        "description": f"{genre_enum.value.title()} music",
    }


@router.get("/health")
async def music_health():
    """Music generation service health check."""
    return {
        "status": "healthy",
        "service": "music_generation",
        "available_genres": len(MusicGenre),
        "available_keys": len(MusicKey),
    }
