# Song Production & Assembly Guide

Complete guide to the Song Production system in Lyrica backend.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Song Assembly](#song-assembly)
4. [Structured Song Creation](#structured-song-creation)
5. [Lyrics Synchronization](#lyrics-synchronization)
6. [Final Mastering](#final-mastering)
7. [Song Variants](#song-variants)
8. [Complete Song Generation](#complete-song-generation)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)
11. [Workflow Examples](#workflow-examples)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Song Production system is the **final stage** of the Lyrica pipeline that combines all generated components (lyrics, vocals, and music) into a complete, professionally produced song.

### What It Does

- ✅ **Mix vocals with instrumental music**
- ✅ **Create multi-section songs** (intro, verse, chorus, bridge, outro)
- ✅ **Synchronize lyrics with music timing**
- ✅ **Apply professional mastering** (loudness normalization, peak limiting)
- ✅ **Generate song variants** (previews, radio edits)
- ✅ **Export in multiple formats** (MP3, WAV, OGG, FLAC, M4A)

### Key Features

```
┌─────────────┐     ┌─────────────┐
│   Vocals    │     │    Music    │
│   (WAV)     │     │    (WAV)    │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
        ┌────────────────┐
        │  Song Assembly │
        │  - Mixing      │
        │  - Balancing   │
        │  - Crossfading │
        └────────┬───────┘
                 ▼
        ┌────────────────┐
        │   Mastering    │
        │  - Loudness    │
        │  - Limiting    │
        │  - EQ          │
        └────────┬───────┘
                 ▼
        ┌────────────────┐
        │  Final Song    │
        │  - Song.wav    │
        │  - Preview.wav │
        │  - Exports     │
        └────────────────┘
```

---

## Architecture

### Core Services

#### 1. Song Assembly Service

**File:** `app/services/production/song_assembly.py`

Handles:

- Mixing vocals and music
- Multi-section song creation
- Lyrics synchronization
- Preview generation
- Multi-format export

#### 2. Song Mastering Service

**File:** `app/services/production/mastering.py`

Handles:

- Final mastering pipeline
- Genre-specific loudness targets
- Radio edit creation
- Instrumental/acapella extraction (placeholder)

---

## Song Assembly

### Basic Song Assembly

Combine vocals and music into a single mixed track:

```python
from app.services.production import get_song_assembly
from pathlib import Path

service = get_song_assembly()

song_path = service.assemble_song(
    vocals_path=Path("audio_files/vocals/my_vocals.wav"),
    music_path=Path("audio_files/music/my_music.wav"),
    vocals_volume_db=0.0,      # Vocal volume (dB)
    music_volume_db=-5.0,      # Music quieter than vocals
    crossfade_ms=500          # 500ms crossfade
)
```

### Volume Balancing

Typical volume relationships:

```python
# Pop/Rock - vocals prominent
vocals_volume_db=0.0
music_volume_db=-5.0

# Electronic - music louder
vocals_volume_db=-3.0
music_volume_db=0.0

# Jazz/Classical - balanced
vocals_volume_db=-2.0
music_volume_db=-2.0

# Hip-Hop - vocals very prominent
vocals_volume_db=2.0
music_volume_db=-6.0
```

### Length Synchronization

The service automatically handles length mismatches:

- **Music longer than vocals:** Trims music to vocals length
- **Music shorter than vocals:** Loops music to match vocals length

---

## Structured Song Creation

### Multi-Section Songs

Create songs with multiple sections (intro, verse, chorus, bridge, outro):

```python
sections = [
    {
        "type": "intro",
        "music_path": Path("audio_files/music/intro.wav"),
        "duration": 8  # 8 seconds
    },
    {
        "type": "verse",
        "vocals_path": Path("audio_files/vocals/verse1.wav"),
        "music_path": Path("audio_files/music/verse.wav"),
        "duration": 16
    },
    {
        "type": "chorus",
        "vocals_path": Path("audio_files/vocals/chorus.wav"),
        "music_path": Path("audio_files/music/chorus.wav"),
        "duration": 16
    },
    {
        "type": "verse",
        "vocals_path": Path("audio_files/vocals/verse2.wav"),
        "music_path": Path("audio_files/music/verse.wav"),
        "duration": 16
    },
    {
        "type": "chorus",
        "vocals_path": Path("audio_files/vocals/chorus.wav"),
        "music_path": Path("audio_files/music/chorus.wav"),
        "duration": 16
    },
    {
        "type": "bridge",
        "vocals_path": Path("audio_files/vocals/bridge.wav"),
        "music_path": Path("audio_files/music/bridge.wav"),
        "duration": 12
    },
    {
        "type": "chorus",
        "vocals_path": Path("audio_files/vocals/chorus.wav"),
        "music_path": Path("audio_files/music/chorus.wav"),
        "duration": 16
    },
    {
        "type": "outro",
        "music_path": Path("audio_files/music/outro.wav"),
        "duration": 8
    }
]

song_path = service.create_song_with_structure(sections=sections)
```

### Section Types

Standard song structure section types:

- **intro:** Instrumental introduction (8-16s)
- **verse:** Storytelling section with vocals (12-16s)
- **chorus:** Main hook/refrain (12-16s)
- **bridge:** Contrasting section (8-16s)
- **outro:** Ending section (8-16s)

### Crossfade Transitions

All sections are automatically connected with 500ms crossfades for smooth transitions.

---

## Lyrics Synchronization

### Time-Based Lyrics Placement

Synchronize lyrics sections with specific timestamps:

```python
lyrics_sections = [
    {
        "text": "First verse lyrics here...",
        "start_time": 0,      # Start at 0 seconds
        "duration": 16        # 16 seconds long
    },
    {
        "text": "Chorus lyrics here...",
        "start_time": 16,     # Start at 16 seconds
        "duration": 16
    },
    {
        "text": "Second verse lyrics...",
        "start_time": 32,
        "duration": 16
    },
    {
        "text": "Final chorus...",
        "start_time": 48,
        "duration": 16
    }
]

vocals_path = service.sync_lyrics_to_music(
    lyrics_sections=lyrics_sections,
    music_path=Path("audio_files/music/instrumental.wav"),
    output_vocals_path=Path("audio_files/vocals/synced.wav")
)
```

### How It Works

1. **Load music** to determine total duration
2. **Create silent track** matching music length
3. **Generate vocals** for each section
4. **Place vocals** at specified timestamps
5. **Export synchronized vocals**

---

## Final Mastering

### Professional Mastering Chain

Apply final mastering to make the song radio-ready:

```python
from app.services.production import get_song_mastering

service = get_song_mastering()

mastered_path = service.master_song(
    song_path=Path("audio_files/songs/raw_song.wav"),
    target_loudness=-14.0,  # LUFS loudness target
    genre="pop"             # Genre-specific processing
)
```

### Loudness Targets by Genre

The service automatically adjusts loudness based on genre:

| Genre        | LUFS Target | Description                    |
|--------------|-------------|--------------------------------|
| Pop          | -14.0       | Streaming platform standard    |
| Rock         | -12.0       | Louder, more aggressive        |
| Electronic   | -11.0       | Very loud, club-ready          |
| Hip-Hop      | -13.0       | Moderately loud                |
| Jazz         | -18.0       | Quieter, more dynamic range    |
| Classical    | -20.0       | Very dynamic, natural sound    |
| Country      | -15.0       | Moderate loudness              |
| R&B          | -14.0       | Streaming standard             |
| Indie        | -16.0       | Quieter, organic sound         |
| Metal        | -10.0       | Very loud, intense             |
| Ambient      | -16.0       | Quieter, atmospheric           |

### What Mastering Does

```
Raw Song
   ↓
[EQ] - Frequency balancing
   ↓
[Compression] - Dynamic range control
   ↓
[Limiting] - Peak control (-1.0 dB)
   ↓
[Loudness Normalization] - LUFS target
   ↓
Mastered Song
```

---

## Song Variants

### 1. Preview Generation

Create 30-second preview/sample:

```python
preview_path = service.create_song_preview(
    song_path=Path("audio_files/songs/full_song.wav"),
    preview_duration=30  # 30 seconds
)
```

Features:

- Extracts first N seconds
- Adds 2-second fade out at the end
- Perfect for sharing/promotion

### 2. Radio Edit

Create radio-friendly 3-minute version:

```python
radio_path = mastering_service.create_radio_edit(
    song_path=Path("audio_files/songs/full_song.wav"),
    target_duration=180  # 3 minutes
)
```

Features:

- Trims to target duration
- Adds 3-second fade out
- Standard radio format

### 3. Multi-Format Export

Export song in multiple formats simultaneously:

```python
exported_files = service.export_multi_format(
    song_path=Path("audio_files/songs/my_song.wav"),
    formats=["mp3", "wav", "ogg", "flac", "m4a"]
)

# Returns:
# {
#     "mp3": Path("my_song.mp3"),   # 320kbps
#     "wav": Path("my_song.wav"),   # Lossless
#     "ogg": Path("my_song.ogg"),   # High quality
#     "flac": Path("my_song.flac"), # Lossless compressed
#     "m4a": Path("my_song.m4a")    # AAC codec
# }
```

#### Format Specifications

| Format | Quality      | Codec      | Use Case               |
|--------|--------------|------------|------------------------|
| MP3    | 320kbps      | MPEG       | Universal streaming    |
| WAV    | Lossless     | PCM        | Professional use       |
| OGG    | High (q=10)  | Vorbis     | Open-source streaming  |
| FLAC   | Lossless     | FLAC       | Archival, audiophiles  |
| M4A    | AAC          | AAC        | Apple ecosystem        |

---

## Complete Song Generation

### End-to-End Pipeline

Generate a complete song from lyrics in one call:

```python
from app.services.production import get_song_assembly, get_song_mastering
from app.services.voice import get_voice_synthesis
from app.services.music import get_music_generation
from app.core.voice_config import get_voice_profile
from pathlib import Path
import uuid

# Generate unique song ID
song_id = f"song_{uuid.uuid4().hex[:8]}"
base_path = Path("audio_files/songs") / song_id
base_path.mkdir(parents=True, exist_ok=True)

# Initialize services
voice_service = get_voice_synthesis()
music_service = get_music_generation()
assembly_service = get_song_assembly()
mastering_service = get_song_mastering()

# 1. Generate vocals
voice_profile = get_voice_profile("female_singer_1")
vocals_path = base_path / "vocals.wav"
voice_service.synthesize_text(
    text="Your full lyrics here...",
    voice_profile=voice_profile,
    output_path=vocals_path
)

# 2. Generate music
music_prompt = "Pop instrumental at 120 BPM"
music_path = base_path / "music.wav"
music_service.generate_music(
    prompt=music_prompt,
    duration=180,
    output_path=music_path
)

# 3. Mix vocals and music
mixed_path = base_path / "mixed.wav"
assembly_service.assemble_song(
    vocals_path=vocals_path,
    music_path=music_path,
    output_path=mixed_path,
    vocals_volume_db=0.0,
    music_volume_db=-5.0,
    crossfade_ms=500
)

# 4. Master song
final_path = base_path / f"{song_id}.wav"
mastering_service.master_song(
    song_path=mixed_path,
    output_path=final_path,
    genre="pop"
)

# 5. Create preview
preview_path = base_path / f"{song_id}_preview.wav"
assembly_service.create_song_preview(
    song_path=final_path,
    preview_duration=30,
    output_path=preview_path
)

# 6. Export multiple formats
exported = assembly_service.export_multi_format(
    song_path=final_path,
    formats=["mp3", "wav", "ogg"]
)
```

---

## API Reference

### Endpoints

Base URL: `/api/v1/production`

#### 1. Assemble Song

```http
POST /api/v1/production/assemble
Content-Type: application/json

{
    "vocals_path": "audio_files/vocals/my_vocals.wav",
    "music_path": "audio_files/music/my_music.wav",
    "vocals_volume_db": 0.0,
    "music_volume_db": -5.0,
    "crossfade_ms": 500
}
```

**Response:**

```json
{
    "success": true,
    "message": "Song assembled successfully",
    "output_path": "audio_files/songs/assembled_song.wav",
    "duration": 185.3,
    "file_size": 32500000
}
```

#### 2. Create Structured Song

```http
POST /api/v1/production/structured
Content-Type: application/json

{
    "sections": [
        {
            "type": "intro",
            "music_path": "audio_files/music/intro.wav"
        },
        {
            "type": "verse",
            "vocals_path": "audio_files/vocals/verse1.wav",
            "music_path": "audio_files/music/verse.wav"
        }
    ]
}
```

#### 3. Synchronize Lyrics

```http
POST /api/v1/production/sync-lyrics
Content-Type: application/json

{
    "lyrics_sections": [
        {"text": "Verse 1 lyrics...", "start_time": 0},
        {"text": "Chorus lyrics...", "start_time": 16}
    ],
    "music_path": "audio_files/music/song.wav"
}
```

#### 4. Master Song

```http
POST /api/v1/production/master
Content-Type: application/json

{
    "song_path": "audio_files/songs/my_song.wav",
    "target_loudness": -14.0,
    "genre": "pop"
}
```

#### 5. Create Preview

```http
POST /api/v1/production/preview
Content-Type: application/json

{
    "song_path": "audio_files/songs/my_song.wav",
    "preview_duration": 30
}
```

#### 6. Export Multi-Format

```http
POST /api/v1/production/export
Content-Type: application/json

{
    "song_path": "audio_files/songs/my_song.wav",
    "formats": ["mp3", "wav", "ogg", "flac"]
}
```

**Response:**

```json
{
    "success": true,
    "message": "Song exported in 4 formats",
    "output_paths": {
        "mp3": "audio_files/songs/my_song.mp3",
        "wav": "audio_files/songs/my_song.wav",
        "ogg": "audio_files/songs/my_song.ogg",
        "flac": "audio_files/songs/my_song.flac"
    }
}
```

#### 7. Create Radio Edit

```http
POST /api/v1/production/radio-edit
Content-Type: application/json

{
    "song_path": "audio_files/songs/my_song.wav",
    "target_duration": 180
}
```

#### 8. Generate Complete Song

**Master endpoint that orchestrates the entire pipeline:**

```http
POST /api/v1/production/generate-complete
Content-Type: application/json

{
    "lyrics_text": "Verse 1...\n\nChorus...\n\nVerse 2...",
    "genre": "pop",
    "bpm": 120,
    "key": "C major",
    "voice_profile": "female_singer_1",
    "duration": 180
}
```

**Response:**

```json
{
    "success": true,
    "message": "Complete song generated successfully",
    "song_id": "song_a3f2c8d1",
    "song_path": "audio_files/songs/song_a3f2c8d1/song_a3f2c8d1.wav",
    "vocals_path": "audio_files/songs/song_a3f2c8d1/vocals.wav",
    "music_path": "audio_files/songs/song_a3f2c8d1/music.wav",
    "preview_path": "audio_files/songs/song_a3f2c8d1/song_a3f2c8d1_preview.wav",
    "duration": 185.3,
    "file_size": 32500000,
    "generation_time": 42.5
}
```

---

## Best Practices

### 1. Volume Balancing

**DO:**

- Keep vocals between 0 dB and +2 dB
- Reduce music by 3-6 dB for vocal prominence
- Test on multiple playback systems

**DON'T:**

- Boost vocals above +3 dB (causes clipping)
- Mix vocals and music at the same volume (muddy)
- Ignore genre conventions

### 2. Crossfading

**Recommended Durations:**

- **Pop/Rock:** 300-500ms
- **Electronic:** 500-1000ms (longer transitions)
- **Jazz/Classical:** 200-400ms (subtle)
- **Hip-Hop:** 100-300ms (tight transitions)

### 3. Mastering

**Best Practices:**

- Use genre-appropriate loudness targets
- Don't over-compress (preserve dynamics)
- Leave headroom for streaming platform normalization
- Test on reference tracks

### 4. Multi-Format Export

**Distribution Recommendations:**

- **Streaming services:** MP3 320kbps or M4A AAC
- **Downloads:** FLAC (lossless)
- **Backup/archive:** WAV (uncompressed)
- **Web players:** OGG (open-source, efficient)

---

## Workflow Examples

### Example 1: Simple Song Assembly

```python
# Mix vocals with music
service = get_song_assembly()

song = service.assemble_song(
    vocals_path=Path("vocals.wav"),
    music_path=Path("music.wav"),
    vocals_volume_db=0,
    music_volume_db=-5,
    crossfade_ms=500
)

# Master
mastering = get_song_mastering()
final = mastering.master_song(
    song_path=song,
    genre="pop"
)
```

### Example 2: Structured Song

```python
# Define song structure
sections = [
    {"type": "intro", "music_path": Path("intro.wav")},
    {"type": "verse", "vocals_path": Path("v1.wav"), "music_path": Path("verse.wav")},
    {"type": "chorus", "vocals_path": Path("c1.wav"), "music_path": Path("chorus.wav")},
    {"type": "verse", "vocals_path": Path("v2.wav"), "music_path": Path("verse.wav")},
    {"type": "chorus", "vocals_path": Path("c1.wav"), "music_path": Path("chorus.wav")},
    {"type": "bridge", "vocals_path": Path("bridge.wav"), "music_path": Path("bridge_music.wav")},
    {"type": "chorus", "vocals_path": Path("c1.wav"), "music_path": Path("chorus.wav")},
    {"type": "outro", "music_path": Path("outro.wav")}
]

# Create song
service = get_song_assembly()
song = service.create_song_with_structure(sections)

# Master
mastering = get_song_mastering()
final = mastering.master_song(song, genre="rock")

# Create variants
preview = service.create_song_preview(final, preview_duration=30)
radio = mastering.create_radio_edit(final, target_duration=180)
exports = service.export_multi_format(final, formats=["mp3", "wav", "flac"])
```

### Example 3: Complete Generation via API

```bash
curl -X POST "http://localhost:8000/api/v1/production/generate-complete" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
         "lyrics_text": "Walking down the street...\n\nChorus...",
         "genre": "indie",
         "bpm": 95,
         "key": "G major",
         "voice_profile": "male_singer_2",
         "duration": 200
     }'
```

---

## Troubleshooting

### Issue: Volume Clipping

**Symptoms:** Distorted audio, harsh sound

**Solutions:**

```python
# Reduce vocal volume
vocals_volume_db=-2.0  # Instead of 0.0

# Or reduce music less
music_volume_db=-3.0  # Instead of -6.0
```

### Issue: Vocals Too Quiet

**Symptoms:** Can't hear vocals clearly

**Solutions:**

```python
# Increase vocal-music difference
vocals_volume_db=0.0
music_volume_db=-8.0  # Reduce music more
```

### Issue: Sections Don't Line Up

**Symptoms:** Abrupt transitions, timing issues

**Solutions:**

```python
# Increase crossfade
crossfade_ms=1000  # Longer fade

# Or ensure sections have correct durations
{"duration": 16, ...}  # Explicit duration
```

### Issue: Song Too Loud/Quiet

**Symptoms:** Inconsistent loudness across platforms

**Solutions:**

```python
# Use genre-appropriate loudness
target_loudness=-14.0  # Streaming standard

# Or use specific genre preset
genre="pop"  # Auto-applies -14.0 LUFS
```

### Issue: File Format Not Supported

**Symptoms:** Export fails for certain formats

**Solutions:**

```python
# Use standard formats
formats=["mp3", "wav", "ogg"]  # Well-supported

# Avoid: formats=["mp4", "avi"]  # Not audio formats
```

---

## Advanced Features

### 1. Custom Volume Envelopes

Future enhancement: Time-varying volume control

```python
# Planned feature
volume_envelope = [
    {"time": 0, "vocals_db": 0, "music_db": -5},
    {"time": 60, "vocals_db": -2, "music_db": -3},  # Music louder at 60s
    {"time": 120, "vocals_db": 0, "music_db": -5}
]
```

### 2. Source Separation

Future enhancement: Extract vocals/instruments from mixed songs

```python
# Planned: Demucs/Spleeter integration
instrumental = mastering.create_instrumental_version(song_path)
acapella = mastering.create_acapella_version(song_path)
```

### 3. Stem Export

Future enhancement: Export individual tracks

```python
# Planned feature
stems = service.export_stems(
    song_path=Path("song.wav"),
    tracks=["vocals", "drums", "bass", "other"]
)
```

---

## Integration with Other Systems

### 1. With Voice Synthesis

```python
from app.services.voice import get_voice_synthesis
from app.services.production import get_song_assembly

# Generate vocals
voice = get_voice_synthesis()
vocals = voice.synthesize_text(text="...", voice_profile=profile)

# Assemble with music
assembly = get_song_assembly()
song = assembly.assemble_song(vocals_path=vocals, music_path=music)
```

### 2. With Music Generation

```python
from app.services.music import get_music_generation
from app.services.production import get_song_assembly

# Generate music
music_gen = get_music_generation()
music = music_gen.generate_music(prompt="Pop instrumental", duration=180)

# Assemble with vocals
assembly = get_song_assembly()
song = assembly.assemble_song(vocals_path=vocals, music_path=music)
```

### 3. With Audio Processing

```python
from app.services.audio.mastering import get_audio_mastering
from app.services.production import get_song_mastering

# Use audio mastering directly
audio_master = get_audio_mastering()
processed = audio_master.apply_mastering_chain(audio_path=song)

# Or use song mastering wrapper
song_master = get_song_mastering()
mastered = song_master.master_song(song_path=song, genre="pop")
```

---

## Performance Optimization

### 1. Parallel Processing

Process multiple songs simultaneously:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def process_song(song_data):
    # Process in separate process
    service = get_song_assembly()
    return service.assemble_song(**song_data)

# Process multiple songs
songs_data = [...]
with ProcessPoolExecutor() as executor:
    results = await asyncio.gather(*[
        executor.submit(process_song, data)
        for data in songs_data
    ])
```

### 2. Caching

Cache generated components:

```python
# Cache vocals/music for reuse
vocals_cache = {}
music_cache = {}

def get_or_generate_vocals(lyrics, voice):
    cache_key = f"{hash(lyrics)}_{voice}"
    if cache_key not in vocals_cache:
        vocals_cache[cache_key] = generate_vocals(lyrics, voice)
    return vocals_cache[cache_key]
```

### 3. Streaming Export

Export large files in chunks:

```python
# For very long songs (>10 minutes)
from pydub import AudioSegment

# Process in chunks
chunk_size = 60000  # 60 seconds
for i in range(0, len(song), chunk_size):
    chunk = song[i:i+chunk_size]
    process_chunk(chunk)
```

---

## Summary

The Song Production system provides a complete pipeline for creating professionally produced songs:

1. **Mix** vocals with instrumental music
2. **Create** multi-section songs with proper structure
3. **Synchronize** lyrics with music timing
4. **Master** for streaming platform readiness
5. **Generate** previews and radio edits
6. **Export** in multiple formats

Ready to use via Python API or HTTP endpoints!

**Key Endpoints:**

- `POST /api/v1/production/assemble` - Mix vocals + music
- `POST /api/v1/production/structured` - Multi-section songs
- `POST /api/v1/production/master` - Final mastering
- `POST /api/v1/production/generate-complete` - End-to-end generation

**Next Steps:**

- See [Voice Synthesis Guide](VOICE_SYNTHESIS_GUIDE.md) for vocal generation
- See [Music Generation Guide](MUSIC_GENERATION_GUIDE.md) for instrumental creation
- See [Audio Processing Guide](AUDIO_PROCESSING_GUIDE.md) for audio manipulation
- See [API Reference](API_REFERENCE.md) for complete endpoint documentation
