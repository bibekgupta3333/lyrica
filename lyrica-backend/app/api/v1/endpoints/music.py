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

from app.core.music_config import MusicGenre, MusicKey, MusicMood, get_genre_bpm_range
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
@router.post(
    "/generate",
    response_model=MusicGenerationResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "upbeat_pop": {
                            "summary": "Upbeat Pop Music",
                            "value": {
                                "prompt": "upbeat pop music with piano and drums",
                                "duration": 30,
                                "temperature": 1.0,
                            },
                        },
                        "ambient_chill": {
                            "summary": "Ambient Chill",
                            "value": {
                                "prompt": "calming ambient music with soft synthesizers",
                                "duration": 60,
                                "temperature": 0.8,
                            },
                        },
                        "rock_anthem": {
                            "summary": "Rock Anthem",
                            "value": {
                                "prompt": "powerful rock anthem with electric guitar and heavy drums",
                                "duration": 45,
                                "temperature": 1.2,
                            },
                        },
                        "jazz_smooth": {
                            "summary": "Smooth Jazz",
                            "value": {
                                "prompt": "smooth jazz with saxophone and piano",
                                "duration": 90,
                                "temperature": 0.9,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/generate/genre",
    response_model=MusicGenerationResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "happy_pop": {
                            "summary": "Happy Pop",
                            "value": {
                                "genre": "pop",
                                "mood": "happy",
                                "key": "C",
                                "bpm": 120,
                                "duration": 30,
                            },
                        },
                        "sad_ballad": {
                            "summary": "Sad Ballad",
                            "value": {
                                "genre": "pop",
                                "mood": "sad",
                                "key": "Am",
                                "bpm": 80,
                                "duration": 60,
                            },
                        },
                        "energetic_rock": {
                            "summary": "Energetic Rock",
                            "value": {
                                "genre": "rock",
                                "mood": "energetic",
                                "key": "E",
                                "bpm": 140,
                                "duration": 45,
                            },
                        },
                        "calm_jazz": {
                            "summary": "Calm Jazz",
                            "value": {
                                "genre": "jazz",
                                "mood": "calm",
                                "key": "F",
                                "bpm": 100,
                                "duration": 90,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/generate/instrumental",
    response_model=MusicGenerationResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "classical_trio": {
                            "summary": "Classical Trio",
                            "value": {
                                "instruments": ["piano", "violin", "cello"],
                                "genre": "classical",
                                "duration": 60,
                            },
                        },
                        "rock_band": {
                            "summary": "Rock Band",
                            "value": {
                                "instruments": ["guitar", "bass", "drums"],
                                "genre": "rock",
                                "duration": 45,
                            },
                        },
                        "jazz_combo": {
                            "summary": "Jazz Combo",
                            "value": {
                                "instruments": ["piano", "saxophone", "bass", "drums"],
                                "genre": "jazz",
                                "duration": 90,
                            },
                        },
                        "electronic_synth": {
                            "summary": "Electronic Synth",
                            "value": {
                                "instruments": ["synth", "drums"],
                                "genre": "electronic",
                                "duration": 60,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/generate/structured",
    response_model=MusicGenerationResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "standard_song": {
                            "summary": "Standard Song Structure",
                            "value": {
                                "sections": [
                                    ["intro", 8],
                                    ["verse", 16],
                                    ["chorus", 16],
                                    ["verse", 16],
                                    ["chorus", 16],
                                    ["outro", 8],
                                ],
                                "genre": "pop",
                                "key": "C",
                                "bpm": 120,
                            },
                        },
                        "simple_structure": {
                            "summary": "Simple Structure",
                            "value": {
                                "sections": [
                                    ["intro", 4],
                                    ["verse", 8],
                                    ["chorus", 8],
                                ],
                                "genre": "pop",
                                "key": None,
                                "bpm": None,
                            },
                        },
                        "complex_structure": {
                            "summary": "Complex Structure",
                            "value": {
                                "sections": [
                                    ["intro", 8],
                                    ["verse", 16],
                                    ["chorus", 16],
                                    ["bridge", 8],
                                    ["verse", 16],
                                    ["chorus", 16],
                                    ["solo", 8],
                                    ["chorus", 16],
                                    ["outro", 8],
                                ],
                                "genre": "rock",
                                "key": "E",
                                "bpm": 140,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/generate/with-melody",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "melody_file": {
                                "type": "string",
                                "format": "binary",
                                "description": "Audio file containing melody",
                            },
                            "genre": {
                                "type": "string",
                                "description": "Music genre",
                                "default": "pop",
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Duration in seconds",
                                "default": 30,
                                "minimum": 5,
                                "maximum": 300,
                            },
                        },
                        "required": ["melody_file"],
                    },
                    "examples": {
                        "pop_melody": {
                            "summary": "Pop Genre",
                            "value": {
                                "melody_file": "(binary)",
                                "genre": "pop",
                                "duration": 30,
                            },
                        },
                        "rock_melody": {
                            "summary": "Rock Genre",
                            "value": {
                                "melody_file": "(binary)",
                                "genre": "rock",
                                "duration": 45,
                            },
                        },
                        "jazz_melody": {
                            "summary": "Jazz Genre",
                            "value": {
                                "melody_file": "(binary)",
                                "genre": "jazz",
                                "duration": 60,
                            },
                        },
                    },
                }
            }
        }
    },
)
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


@router.post(
    "/chords/generate",
    response_model=ChordProgressionResponse,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_progression": {
                            "summary": "Pop Chord Progression",
                            "value": {
                                "key": "C",
                                "genre": "pop",
                                "num_chords": 4,
                            },
                        },
                        "jazz_progression": {
                            "summary": "Jazz Chord Progression",
                            "value": {
                                "key": "Am",
                                "genre": "jazz",
                                "num_chords": 8,
                            },
                        },
                        "rock_progression": {
                            "summary": "Rock Chord Progression",
                            "value": {
                                "key": "E",
                                "genre": "rock",
                                "num_chords": 4,
                            },
                        },
                        "long_progression": {
                            "summary": "Long Progression",
                            "value": {
                                "key": "G",
                                "genre": None,
                                "num_chords": 12,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.post(
    "/melody/generate",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "pop_melody": {
                            "summary": "Pop Melody",
                            "value": {
                                "key": "C",
                                "num_notes": 16,
                                "duration": 8,
                                "genre": "pop",
                                "pentatonic": False,
                            },
                        },
                        "pentatonic_simple": {
                            "summary": "Pentatonic Scale",
                            "value": {
                                "key": "Am",
                                "num_notes": 8,
                                "duration": 4,
                                "genre": None,
                                "pentatonic": True,
                            },
                        },
                        "jazz_melody": {
                            "summary": "Jazz Melody",
                            "value": {
                                "key": "F",
                                "num_notes": 32,
                                "duration": 16,
                                "genre": "jazz",
                                "pentatonic": False,
                            },
                        },
                        "long_melody": {
                            "summary": "Long Melody",
                            "value": {
                                "key": "G",
                                "num_notes": 64,
                                "duration": 30,
                                "genre": "classical",
                                "pentatonic": False,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.get(
    "/genres/{genre}/info",
    openapi_extra={
        "parameters": [
            {
                "name": "genre",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "examples": {
                    "pop": {"summary": "Pop Genre", "value": "pop"},
                    "rock": {"summary": "Rock Genre", "value": "rock"},
                    "jazz": {"summary": "Jazz Genre", "value": "jazz"},
                    "electronic": {"summary": "Electronic Genre", "value": "electronic"},
                },
            }
        ]
    },
)
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
