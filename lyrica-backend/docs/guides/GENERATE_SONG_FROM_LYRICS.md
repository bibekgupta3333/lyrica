# Generate Song from Lyrics - Quick Guide

This guide shows you how to generate a complete song from lyrics using Lyrica, similar to YuEGP.

## Overview

Lyrica can generate complete songs (vocals + music) directly from lyrics text. The system:

1. Synthesizes vocals from lyrics using TTS
2. Generates instrumental music matching the genre and tempo
3. Mixes vocals and music with intelligent frequency balancing
4. Applies final mastering
5. Creates a preview version

## API Endpoint

**POST** `/api/v1/production/generate-complete`

## Request Format

```json
{
  "lyrics_text": "Your lyrics here...",
  "genre": "pop",
  "bpm": 120,
  "key": "C major",
  "voice_profile": "female_singer_1",
  "duration": 180
}
```

### Required Fields

- **lyrics_text** (string, min 50 chars): Your song lyrics
  - Can include section markers: `[Verse 1]`, `[Chorus]`, `[Bridge]`, etc.
  - Use line breaks (`\n`) to separate lines
  - Example:

    ```
    [Verse 1]
    Walking down the street
    Feeling the beat
    
    [Chorus]
    Dancing in the moonlight
    Everything feels right
    ```

- **genre** (string): Music genre
  - Supported: `pop`, `rock`, `jazz`, `hip-hop`, `electronic`, `ballad`, `country`, `blues`, `classical`, `folk`, `reggae`, `metal`, `punk`, `r&b`, `soul`, `funk`, `disco`, `latin`, `world`

- **bpm** (integer, 40-200): Tempo in beats per minute
  - Pop: 100-130
  - Rock: 120-140
  - Ballad: 60-90
  - Hip-hop: 80-100

- **key** (string): Musical key
  - Examples: `C major`, `A minor`, `G major`, `D minor`, `E major`, `F major`
  - Format: `[Note] [major|minor]`

- **voice_profile** (string): Voice to use for vocals
  - Available: `female_singer_1`, `male_singer_1`, `female_singer_2`, `male_singer_2`
  - Default: `female_singer_1`

- **duration** (integer, 30-600): Target song duration in seconds
  - Default: 180 (3 minutes)

## Response Format

```json
{
  "success": true,
  "message": "Complete song generated successfully",
  "song_id": "song_abc12345",
  "song_path": "audio_files/songs/song_abc12345/song_abc12345.wav",
  "vocals_path": "audio_files/songs/song_abc12345/vocals.wav",
  "music_path": "audio_files/songs/song_abc12345/music.wav",
  "preview_path": "audio_files/songs/song_abc12345/song_abc12345_preview.wav",
  "duration": 185.3,
  "file_size": 32400000,
  "generation_time": 45.2
}
```

## Examples

### Example 1: Pop Song

```bash
curl -X POST "http://localhost:8000/api/v1/production/generate-complete" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics_text": "[Verse 1]\nWalking down the street\nFeeling the beat\n\n[Chorus]\nDancing in the moonlight\nEverything feels right\n\n[Verse 2]\nMusic fills the air\nNo time for a care\n\n[Chorus]\nDancing in the moonlight\nEverything feels right",
    "genre": "pop",
    "bpm": 120,
    "key": "C major",
    "voice_profile": "female_singer_1",
    "duration": 180
  }'
```

### Example 2: Rock Song

```bash
curl -X POST "http://localhost:8000/api/v1/production/generate-complete" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics_text": "[Verse 1]\nTurn up the volume\nFeel the power\n\n[Chorus]\nRock and roll forever\nWe'\''ll never surrender\n\n[Verse 2]\nGuitars are screaming\nDrums are beating\n\n[Chorus]\nRock and roll forever\nWe'\''ll never surrender",
    "genre": "rock",
    "bpm": 140,
    "key": "E major",
    "voice_profile": "male_singer_1",
    "duration": 200
  }'
```

### Example 3: Ballad

```bash
curl -X POST "http://localhost:8000/api/v1/production/generate-complete" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics_text": "[Verse]\nIn the quiet of the night\nI think of you\nAll the moments we shared\nSo few, so true\n\n[Bridge]\nTime moves on\nBut memories stay\nIn my heart forever\nThey'\''ll never fade away",
    "genre": "pop",
    "bpm": 80,
    "key": "A minor",
    "voice_profile": "female_singer_1",
    "duration": 150
  }'
```

### Example 4: Python Script

```python
import requests
import json

url = "http://localhost:8000/api/v1/production/generate-complete"

lyrics = """[Verse 1]
Walking down the street
Feeling the beat

[Chorus]
Dancing in the moonlight
Everything feels right

[Verse 2]
Music fills the air
No time for a care

[Chorus]
Dancing in the moonlight
Everything feels right"""

payload = {
    "lyrics_text": lyrics,
    "genre": "pop",
    "bpm": 120,
    "key": "C major",
    "voice_profile": "female_singer_1",
    "duration": 180
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    print(f"✅ Song generated: {result['song_id']}")
    print(f"📁 Path: {result['song_path']}")
    print(f"⏱️  Duration: {result['duration']:.1f}s")
    print(f"⏱️  Generation time: {result['generation_time']:.1f}s")
else:
    print(f"❌ Error: {result['message']}")
```

## Features

### Intelligent Mixing

The endpoint uses intelligent frequency balancing:

- **Dynamic EQ**: Adjusts frequencies to prevent conflicts between vocals and music
- **Sidechain Compression**: Music volume ducks when vocals are present
- **Stereo Imaging**: Creates spatial depth with reverb and delay
- **Genre-Specific Presets**: Optimized mixing settings for each genre

### Quality Improvements

All recent fixes are applied:

- ✅ Sample rate normalization (prevents corruption)
- ✅ Channel normalization (proper stereo mixing)
- ✅ Volume headroom (prevents clipping)
- ✅ Final normalization (optimal levels)
- ✅ Vocals synthesis normalization (prevents signal loss)

## Tips for Best Results

1. **Lyrics Format**:
   - Use section markers: `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro]`
   - Keep lines concise (4-8 words per line)
   - Use line breaks (`\n`) between lines

2. **Genre Selection**:
   - Match genre to lyrics mood
   - Pop: Upbeat, catchy
   - Rock: Powerful, energetic
   - Ballad: Slow, emotional
   - Hip-hop: Rhythmic, urban

3. **BPM Selection**:
   - Match BPM to genre and mood
   - Faster BPM = more energetic
   - Slower BPM = more emotional/introspective

4. **Key Selection**:
   - Major keys: Happy, uplifting
   - Minor keys: Sad, melancholic
   - Match key to lyrics mood

5. **Duration**:
   - Typical pop song: 180-240 seconds (3-4 minutes)
   - Ballad: 150-200 seconds
   - Rock: 200-300 seconds

## Troubleshooting

### "Signal loss" or corrupted audio

- ✅ **Fixed**: All normalization issues have been resolved
- If you still experience issues, generate a new song

### Vocals too quiet or too loud

- The system uses intelligent mixing with automatic volume balancing
- Vocals are normalized to optimal levels

### Music doesn't match genre

- Ensure genre string matches supported genres exactly (lowercase)
- Check that BPM is appropriate for the genre

### Generation takes too long

- Normal generation time: 30-60 seconds
- First generation may take longer (model loading)
- Complex songs may take up to 2 minutes

## Comparison with YuEGP

| Feature | YuEGP | Lyrica |
|---------|-------|--------|
| Input | Lyrics text | Lyrics text ✅ |
| Output | Complete song | Complete song ✅ |
| Vocals | TTS synthesis | TTS synthesis ✅ |
| Music | AI generation | AI generation ✅ |
| Mixing | Basic | Intelligent mixing ✅ |
| Mastering | Basic | Professional mastering ✅ |
| Genre Support | Limited | 20+ genres ✅ |
| API | CLI only | REST API ✅ |
| Authentication | None | JWT auth ✅ |

## Next Steps

1. **Generate your first song**: Use the examples above
2. **Experiment with genres**: Try different genres and BPMs
3. **Customize voice**: Try different voice profiles
4. **Enhance songs**: Use `/api/v1/enhancement/complete` for post-processing

## Related Endpoints

- **Generate lyrics first**: `/api/v1/songs/generate-complete` (generates lyrics + song)
- **Enhance existing song**: `/api/v1/enhancement/complete`
- **Regenerate music**: `/api/v1/songs/{id}/regenerate-music`
- **Regenerate vocals**: `/api/v1/songs/{id}/regenerate-vocals`

---

**Last Updated**: 2025-12-05  
**Status**: ✅ Production Ready
