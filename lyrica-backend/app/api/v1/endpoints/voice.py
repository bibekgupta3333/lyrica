"""
Voice synthesis API endpoints.

This module provides REST API endpoints for voice synthesis,
pitch control, tempo adjustment, and vocal effects.
"""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.voice_config import (
    TTSEngine,
    VoiceGender,
    VoiceProfile,
    VoiceStyle,
    get_voice_profile,
    list_voice_profiles,
)
from app.services.voice import get_pitch_control, get_vocal_effects, get_voice_synthesis

router = APIRouter(prefix="/voice", tags=["Voice Synthesis"])


# Request/Response Models
class SynthesizeRequest(BaseModel):
    """Request to synthesize speech from text."""

    text: str = Field(..., max_length=500, description="Text to synthesize")
    voice_profile_id: str = Field(..., description="Voice profile ID")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")


class SynthesizeLyricsRequest(BaseModel):
    """Request to synthesize song lyrics."""

    lyrics: str = Field(..., max_length=2000, description="Song lyrics")
    voice_profile_id: str = Field(..., description="Voice profile ID")
    chunk_by_sentences: bool = Field(default=True, description="Chunk by lines/sentences")


class PitchAdjustRequest(BaseModel):
    """Request to adjust pitch."""

    semitones: float = Field(..., ge=-12.0, le=12.0, description="Pitch shift in semitones")


class TempoAdjustRequest(BaseModel):
    """Request to adjust tempo."""

    tempo_factor: float = Field(..., ge=0.5, le=2.0, description="Tempo multiplier (1.0 = normal)")


class VocalEffectsRequest(BaseModel):
    """Request to apply vocal effects."""

    reverb: Optional[dict] = Field(
        default=None, description="Reverb settings (room_size, damping, wet_level)"
    )
    echo: Optional[dict] = Field(default=None, description="Echo settings (delay_ms, decay)")
    compression: Optional[dict] = Field(
        default=None, description="Compression settings (threshold, ratio)"
    )
    eq: Optional[dict] = Field(default=None, description="EQ settings (low, mid, high)")
    denoise: Optional[float] = Field(default=None, description="Denoise strength (0-1)")


class VoiceProfileResponse(BaseModel):
    """Voice profile response."""

    id: str
    name: str
    gender: VoiceGender
    language: str
    accent: Optional[str]
    age_range: Optional[str]
    description: Optional[str]
    engine: TTSEngine


class SynthesisResponse(BaseModel):
    """Voice synthesis response."""

    file_path: str
    duration_seconds: float
    voice_profile_id: str
    message: str


# Endpoints
@router.get("/profiles", response_model=list[VoiceProfileResponse])
async def get_voice_profiles(
    gender: Optional[VoiceGender] = None,
    language: Optional[str] = None,
    engine: Optional[TTSEngine] = None,
):
    """
    Get available voice profiles.

    Filter by gender, language, or TTS engine.
    """
    profiles = list_voice_profiles(gender=gender, language=language, engine=engine)
    return [VoiceProfileResponse(**p.model_dump()) for p in profiles]


@router.get("/profiles/{profile_id}", response_model=VoiceProfileResponse)
async def get_profile_details(profile_id: str):
    """Get details of a specific voice profile."""
    profile = get_voice_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found",
        )
    return VoiceProfileResponse(**profile.model_dump())


@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesizeRequest):
    """
    Synthesize speech from text using specified voice profile.

    Example:
        ```json
        {
            "text": "Hello, world! This is a test.",
            "voice_profile_id": "male_narrator_1",
            "temperature": 0.7,
            "speed": 1.0
        }
        ```
    """
    # Get voice profile
    voice_profile = get_voice_profile(request.voice_profile_id)
    if not voice_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{request.voice_profile_id}' not found",
        )

    # Generate output path
    synthesis_service = get_voice_synthesis()
    output_dir = synthesis_service.config.generated_voices_path
    output_path = output_dir / f"speech_{request.voice_profile_id}.wav"

    try:
        # Synthesize
        result_path = synthesis_service.synthesize_text(
            text=request.text,
            voice_profile=voice_profile,
            output_path=output_path,
            temperature=request.temperature,
            speed=request.speed,
        )

        # Estimate duration
        duration = synthesis_service.estimate_duration(request.text)

        return SynthesisResponse(
            file_path=str(result_path),
            duration_seconds=duration,
            voice_profile_id=request.voice_profile_id,
            message="Speech synthesized successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis failed: {str(e)}",
        )


@router.post("/synthesize/lyrics", response_model=SynthesisResponse)
async def synthesize_lyrics(request: SynthesizeLyricsRequest):
    """
    Synthesize song lyrics with appropriate phrasing and timing.

    Handles long lyrics by chunking intelligently and adding pauses.

    Example:
        ```json
        {
            "lyrics": "[Verse 1]\\nIn the morning light...\\n\\n[Chorus]\\nOh yeah!",
            "voice_profile_id": "female_singer_1",
            "chunk_by_sentences": true
        }
        ```
    """
    # Get voice profile
    voice_profile = get_voice_profile(request.voice_profile_id)
    if not voice_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{request.voice_profile_id}' not found",
        )

    # Generate output path
    synthesis_service = get_voice_synthesis()
    output_dir = synthesis_service.config.generated_voices_path
    output_path = output_dir / f"lyrics_{request.voice_profile_id}.wav"

    try:
        # Synthesize lyrics
        result_path = synthesis_service.synthesize_lyrics(
            lyrics=request.lyrics,
            voice_profile=voice_profile,
            output_path=output_path,
            chunk_sentences=request.chunk_by_sentences,
        )

        # Estimate duration
        duration = synthesis_service.estimate_duration(request.lyrics)

        return SynthesisResponse(
            file_path=str(result_path),
            duration_seconds=duration,
            voice_profile_id=request.voice_profile_id,
            message="Lyrics synthesized successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lyrics synthesis failed: {str(e)}",
        )


@router.post("/adjust/pitch")
async def adjust_pitch(file: UploadFile = File(...), semitones: float = Form(...)):
    """
    Adjust pitch of uploaded audio file.

    Args:
        file: Audio file to process
        semitones: Pitch shift in semitones (-12 to +12)

    Returns:
        Processed audio file

    Example:
        Shift up one octave: semitones=+12
        Shift down perfect fifth: semitones=-7
    """
    pitch_service = get_pitch_control()

    # Save uploaded file
    temp_dir = Path("audio_files/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    input_path = temp_dir / (file.filename or "uploaded_audio.wav")
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        # Adjust pitch
        output_path = pitch_service.shift_pitch(input_path, semitones)

        # Return file
        return FileResponse(
            path=str(output_path),
            media_type="audio/wav",
            filename=output_path.name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pitch adjustment failed: {str(e)}",
        )
    finally:
        # Cleanup
        input_path.unlink(missing_ok=True)


@router.post("/adjust/tempo")
async def adjust_tempo(file: UploadFile = File(...), tempo_factor: float = Form(...)):
    """
    Adjust tempo of uploaded audio file without changing pitch.

    Args:
        file: Audio file to process
        tempo_factor: Tempo multiplier (0.5 to 2.0)

    Returns:
        Processed audio file

    Example:
        Slow down by 50%: tempo_factor=0.5
        Speed up by 50%: tempo_factor=1.5
    """
    pitch_service = get_pitch_control()

    # Save uploaded file
    temp_dir = Path("audio_files/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    input_path = temp_dir / (file.filename or "uploaded_audio.wav")
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        # Adjust tempo
        output_path = pitch_service.change_tempo(input_path, tempo_factor)

        # Return file
        return FileResponse(
            path=str(output_path),
            media_type="audio/wav",
            filename=output_path.name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tempo adjustment failed: {str(e)}",
        )
    finally:
        # Cleanup
        input_path.unlink(missing_ok=True)


@router.post("/effects")
async def apply_effects(file: UploadFile = File(...), effects: str = Form(...)):
    """
    Apply vocal effects to uploaded audio file.

    Args:
        file: Audio file to process
        effects: JSON string of effects configuration

    Returns:
        Processed audio file with effects

    Example effects JSON:
        ```json
        {
            "reverb": {"room_size": 0.7, "wet_level": 0.4},
            "echo": {"delay_ms": 500, "decay": 0.3},
            "compression": {"threshold": -20, "ratio": 4},
            "eq": {"low_shelf_db": 2, "mid_db": 0, "high_shelf_db": -2},
            "denoise": 0.5
        }
        ```
    """
    import json

    effects_service = get_vocal_effects()

    # Parse effects
    try:
        effects_config = json.loads(effects)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid effects JSON")

    # Save uploaded file
    temp_dir = Path("audio_files/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    filename = file.filename or "audio.wav"
    input_path = temp_dir / filename
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        output_path = input_path

        # Apply effects in sequence
        if "reverb" in effects_config:
            reverb = effects_config["reverb"]
            output_path = effects_service.add_reverb(
                output_path,
                room_size=reverb.get("room_size", 0.5),
                damping=reverb.get("damping", 0.5),
                wet_level=reverb.get("wet_level", 0.3),
            )

        if "echo" in effects_config:
            echo = effects_config["echo"]
            output_path = effects_service.add_echo(
                output_path,
                delay_ms=echo.get("delay_ms", 500),
                decay=echo.get("decay", 0.3),
            )

        if "compression" in effects_config:
            comp = effects_config["compression"]
            output_path = effects_service.apply_compression(
                output_path,
                threshold=comp.get("threshold", -20),
                ratio=comp.get("ratio", 4),
            )

        if "eq" in effects_config:
            eq = effects_config["eq"]
            output_path = effects_service.apply_eq(
                output_path,
                low_shelf_db=eq.get("low_shelf_db", 0),
                mid_db=eq.get("mid_db", 0),
                high_shelf_db=eq.get("high_shelf_db", 0),
            )

        if "denoise" in effects_config:
            strength = effects_config["denoise"]
            output_path = effects_service.denoise(output_path, strength)

        # Return processed file
        return FileResponse(
            path=str(output_path),
            media_type="audio/wav",
            filename=output_path.name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Effects processing failed: {str(e)}",
        )
    finally:
        # Cleanup
        input_path.unlink(missing_ok=True)


@router.post("/voice-activity-detection")
async def detect_voice_activity(
    file: UploadFile = File(...),
    threshold: float = Form(default=0.5, ge=0.0, le=1.0),
):
    """
    Detect voice activity in uploaded audio file using Silero VAD.

    Args:
        file: Audio file to analyze
        threshold: Voice activity detection threshold (0-1)

    Returns:
        List of voice activity segments with start and end times in seconds

    Example response:
        ```json
        {
            "segments": [
                {"start": 0.5, "end": 2.3},
                {"start": 3.1, "end": 5.7}
            ],
            "total_speech_duration": 4.4,
            "total_segments": 2
        }
        ```
    """
    synthesis_service = get_voice_synthesis()

    # Save uploaded file
    temp_dir = Path("audio_files/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    filename = file.filename or "audio.wav"
    input_path = temp_dir / filename
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        # Detect voice activity
        segments = synthesis_service.detect_voice_activity(input_path, threshold)

        # Calculate total speech duration
        total_duration = sum(end - start for start, end in segments)

        return {
            "segments": [{"start": start, "end": end} for start, end in segments],
            "total_speech_duration": round(total_duration, 2),
            "total_segments": len(segments),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice activity detection failed: {str(e)}",
        )
    finally:
        # Cleanup
        input_path.unlink(missing_ok=True)


@router.get("/health")
async def voice_health():
    """Voice synthesis service health check."""
    return {
        "status": "healthy",
        "service": "voice_synthesis",
        "available_profiles": len(list_voice_profiles()),
        "supported_engines": [e.value for e in TTSEngine],
    }
