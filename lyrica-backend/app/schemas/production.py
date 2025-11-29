"""Pydantic schemas for song production."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SongAssemblyRequest(BaseModel):
    """Request schema for assembling a song."""

    vocals_path: str = Field(..., description="Path to vocals audio file")
    music_path: str = Field(..., description="Path to instrumental music file")
    vocals_volume_db: float = Field(0.0, ge=-20, le=20, description="Vocals volume (dB)")
    music_volume_db: float = Field(-3.0, ge=-20, le=20, description="Music volume (dB)")
    crossfade_ms: int = Field(0, ge=0, le=5000, description="Crossfade duration (ms)")

    class Config:
        json_schema_extra = {
            "example": {
                "vocals_path": "audio_files/vocals/my_vocals.wav",
                "music_path": "audio_files/music/my_music.wav",
                "vocals_volume_db": 0.0,
                "music_volume_db": -5.0,
                "crossfade_ms": 500,
            }
        }


class SongSectionRequest(BaseModel):
    """Request schema for a song section."""

    type: str = Field(..., description="Section type (intro, verse, chorus, bridge, outro)")
    vocals_path: Optional[str] = Field(None, description="Path to vocals (optional)")
    music_path: str = Field(..., description="Path to music")
    duration: Optional[int] = Field(None, description="Section duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "verse",
                "vocals_path": "audio_files/vocals/verse1.wav",
                "music_path": "audio_files/music/verse_music.wav",
                "duration": 16,
            }
        }


class StructuredSongRequest(BaseModel):
    """Request schema for structured song creation."""

    sections: list[SongSectionRequest] = Field(..., description="List of song sections")

    class Config:
        json_schema_extra = {
            "example": {
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
            }
        }


class LyricsSyncSection(BaseModel):
    """Schema for lyrics section with timing."""

    text: str = Field(..., description="Lyrics text")
    start_time: float = Field(..., ge=0, description="Start time (seconds)")
    duration: Optional[float] = Field(None, description="Duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {"text": "Verse 1 lyrics here...", "start_time": 0, "duration": 16}
        }


class LyricsSyncRequest(BaseModel):
    """Request schema for lyrics synchronization."""

    lyrics_sections: list[LyricsSyncSection] = Field(..., description="Lyrics sections")
    music_path: str = Field(..., description="Path to music")

    class Config:
        json_schema_extra = {
            "example": {
                "lyrics_sections": [
                    {"text": "Verse 1 lyrics...", "start_time": 0, "duration": 16},
                    {"text": "Chorus lyrics...", "start_time": 16, "duration": 16},
                ],
                "music_path": "audio_files/music/song.wav",
            }
        }


class SongMasteringRequest(BaseModel):
    """Request schema for song mastering."""

    song_path: str = Field(..., description="Path to song audio")
    target_loudness: float = Field(-14.0, ge=-30, le=-5, description="Target LUFS")
    genre: Optional[str] = Field(None, description="Genre for genre-specific mastering")

    class Config:
        json_schema_extra = {
            "example": {
                "song_path": "audio_files/songs/my_song.wav",
                "target_loudness": -14.0,
                "genre": "pop",
            }
        }


class SongPreviewRequest(BaseModel):
    """Request schema for song preview."""

    song_path: str = Field(..., description="Path to full song")
    preview_duration: int = Field(30, ge=10, le=60, description="Preview duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {"song_path": "audio_files/songs/my_song.wav", "preview_duration": 30}
        }


class MultiFormatExportRequest(BaseModel):
    """Request schema for multi-format export."""

    song_path: str = Field(..., description="Path to song audio")
    formats: list[str] = Field(..., description="List of formats (mp3, wav, ogg, flac, m4a)")

    class Config:
        json_schema_extra = {
            "example": {
                "song_path": "audio_files/songs/my_song.wav",
                "formats": ["mp3", "wav", "ogg", "flac"],
            }
        }


class RadioEditRequest(BaseModel):
    """Request schema for radio edit."""

    song_path: str = Field(..., description="Path to full song")
    target_duration: int = Field(180, ge=60, le=300, description="Target duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {"song_path": "audio_files/songs/my_song.wav", "target_duration": 180}
        }


class SongProductionResponse(BaseModel):
    """Response schema for song production."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Status message")
    output_path: Optional[str] = Field(None, description="Path to output file")
    output_paths: Optional[dict[str, str]] = Field(None, description="Multiple output paths")
    duration: Optional[float] = Field(None, description="Audio duration (seconds)")
    file_size: Optional[int] = Field(None, description="File size (bytes)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Song assembled successfully",
                "output_path": "audio_files/songs/assembled_song.wav",
                "duration": 180.5,
                "file_size": 31850000,
            }
        }


class CompleteSongRequest(BaseModel):
    """Request schema for complete song generation."""

    lyrics_text: str = Field(..., min_length=50, description="Lyrics text")
    genre: str = Field(..., description="Music genre")
    bpm: int = Field(120, ge=40, le=200, description="Tempo (BPM)")
    key: str = Field("C major", description="Musical key")
    voice_profile: str = Field("female_singer_1", description="Voice profile")
    duration: int = Field(180, ge=30, le=600, description="Target duration (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "lyrics_text": "Verse 1...\n\nChorus...\n\nVerse 2...",
                "genre": "pop",
                "bpm": 120,
                "key": "C major",
                "voice_profile": "female_singer_1",
                "duration": 180,
            }
        }


class CompleteSongResponse(BaseModel):
    """Response schema for complete song generation."""

    success: bool = Field(..., description="Whether generation succeeded")
    message: str = Field(..., description="Status message")
    song_id: Optional[str] = Field(None, description="Song ID")
    song_path: Optional[str] = Field(None, description="Path to final song")
    vocals_path: Optional[str] = Field(None, description="Path to vocals")
    music_path: Optional[str] = Field(None, description="Path to music")
    preview_path: Optional[str] = Field(None, description="Path to preview")
    duration: Optional[float] = Field(None, description="Song duration (seconds)")
    file_size: Optional[int] = Field(None, description="File size (bytes)")
    generation_time: Optional[float] = Field(None, description="Generation time (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Complete song generated successfully",
                "song_id": "song_12345",
                "song_path": "audio_files/songs/song_12345.wav",
                "vocals_path": "audio_files/vocals/song_12345_vocals.wav",
                "music_path": "audio_files/music/song_12345_music.wav",
                "preview_path": "audio_files/songs/song_12345_preview.wav",
                "duration": 185.3,
                "file_size": 32400000,
                "generation_time": 45.2,
            }
        }
