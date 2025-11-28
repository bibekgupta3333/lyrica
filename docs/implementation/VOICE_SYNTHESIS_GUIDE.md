# Voice Synthesis System Guide

## Overview

The Lyrica Voice Synthesis System provides professional text-to-speech (TTS) capabilities with advanced pitch control, tempo adjustment, and vocal effects. This guide covers the complete voice synthesis pipeline.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Voice Synthesis System                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐     ┌─────────────────────┐          │
│  │  TTS Engines     │     │  Voice Profiles     │          │
│  │  - Bark          │────▶│  - Male Narrator   │          │
│  │  - Coqui TTS     │     │  - Female Singer   │          │
│  │  - Tortoise TTS  │     │  - Male Singer     │          │
│  └──────────────────┘     │  - Neutral Soft    │          │
│                           └─────────────────────┘          │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Voice Synthesis Service                     │    │
│  │  - Text-to-speech                                   │    │
│  │  - Lyrics synthesis                                 │    │
│  │  - Duration estimation                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Pitch Control Service                       │    │
│  │  - Pitch shifting (±12 semitones)                   │    │
│  │  - Tempo control (0.5x - 2.0x)                      │    │
│  │  - Auto-tune                                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Vocal Effects Service                       │    │
│  │  - Reverb                                           │    │
│  │  - Echo                                             │    │
│  │  - Compression                                      │    │
│  │  - EQ                                               │    │
│  │  - Noise reduction                                  │    │
│  │  - Harmony generation                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## TTS Engines

### 1. Bark (Suno AI)

**Best for:** Final production vocals

**Features:**
- Natural prosody and intonation
- Built-in emotion control
- High-quality audio output
- Multiple languages

**Configuration:**
```python
from app.services.voice import get_voice_synthesis
from app.core.voice_config import get_voice_profile

# Get service
synthesis = get_voice_synthesis()

# Get voice profile
profile = get_voice_profile("male_narrator_1")

# Synthesize
audio_path = synthesis.synthesize_text(
    text="Hello, world!",
    voice_profile=profile,
    output_path=Path("output.wav"),
    temperature=0.7  # Creativity (0.0-1.0)
)
```

### 2. Coqui TTS

**Best for:** Rapid prototyping

**Features:**
- Fast generation
- Good quality
- Multi-language support
- Voice cloning capability

**Configuration:**
```python
profile = get_voice_profile("female_singer_1")

audio_path = synthesis.synthesize_text(
    text="This is a test",
    voice_profile=profile,
    output_path=Path("output.wav"),
    speed=1.2  # Speed multiplier
)
```

## Voice Profiles

### Available Profiles

| Profile ID | Gender | Age | Accent | Best For |
|------------|--------|-----|--------|----------|
| `male_narrator_1` | Male | Adult | American | Narration, storytelling |
| `female_singer_1` | Female | Young | American | Singing, melodic content |
| `male_singer_1` | Male | Adult | American | Singing, vocals |
| `neutral_soft` | Neutral | Adult | Neutral | Gentle narration |

### Creating Custom Profiles

```python
from app.core.voice_config import VoiceProfile, TTSEngine, VoiceGender

custom_profile = VoiceProfile(
    id="custom_voice_1",
    name="Custom Voice",
    gender=VoiceGender.FEMALE,
    language="en",
    accent="british",
    age_range="young",
    description="Custom British female voice",
    engine=TTSEngine.BARK,
    engine_voice_id="v2/en_speaker_5"
)
```

## Pitch Control

### Pitch Shifting

Shift pitch up or down without changing tempo:

```python
from app.services.voice import get_pitch_control
from pathlib import Path

pitch_service = get_pitch_control()

# Shift up one octave (+12 semitones)
shifted_path = pitch_service.shift_pitch(
    audio_path=Path("vocals.wav"),
    semitones=12.0,
    output_path=Path("vocals_higher.wav")
)

# Shift down a perfect fifth (-7 semitones)
shifted_path = pitch_service.shift_pitch(
    audio_path=Path("vocals.wav"),
    semitones=-7.0
)
```

### Tempo Control

Change playback speed without affecting pitch:

```python
# Slow down to 75% speed
slower_path = pitch_service.change_tempo(
    audio_path=Path("vocals.wav"),
    tempo_factor=0.75,
    output_path=Path("vocals_slower.wav")
)

# Speed up to 150%
faster_path = pitch_service.change_tempo(
    audio_path=Path("vocals.wav"),
    tempo_factor=1.5
)
```

### Combined Pitch & Tempo

```python
# Shift pitch up AND speed up
adjusted_path = pitch_service.pitch_and_tempo(
    audio_path=Path("vocals.wav"),
    semitones=3.0,      # Raise pitch
    tempo_factor=1.2,   # Speed up
    output_path=Path("vocals_adjusted.wav")
)
```

## Vocal Effects

### Reverb

Add spatial depth to vocals:

```python
from app.services.voice import get_vocal_effects

effects = get_vocal_effects()

reverb_path = effects.add_reverb(
    audio_path=Path("vocals.wav"),
    room_size=0.7,      # 0.0-1.0 (larger = longer reverb)
    damping=0.5,        # 0.0-1.0 (higher = less high freq)
    wet_level=0.4,      # 0.0-1.0 (mix level)
    output_path=Path("vocals_reverb.wav")
)
```

### Echo

Add echo/delay effect:

```python
echo_path = effects.add_echo(
    audio_path=Path("vocals.wav"),
    delay_ms=500,       # Delay in milliseconds
    decay=0.3,          # 0.0-1.0 (echo strength)
    output_path=Path("vocals_echo.wav")
)
```

### Compression

Apply dynamic range compression:

```python
compressed_path = effects.apply_compression(
    audio_path=Path("vocals.wav"),
    threshold=-20.0,    # dB threshold
    ratio=4.0,          # Compression ratio (4:1)
    attack_ms=5.0,      # Attack time
    release_ms=50.0,    # Release time
    output_path=Path("vocals_compressed.wav")
)
```

### EQ (Equalization)

Adjust frequency bands:

```python
eq_path = effects.apply_eq(
    audio_path=Path("vocals.wav"),
    low_shelf_db=2.0,   # Boost/cut low frequencies
    mid_db=0.0,         # Boost/cut mid frequencies
    high_shelf_db=-2.0, # Boost/cut high frequencies
    output_path=Path("vocals_eq.wav")
)
```

### Noise Reduction

Remove background noise:

```python
denoised_path = effects.denoise(
    audio_path=Path("vocals.wav"),
    noise_reduction_strength=0.5,  # 0.0-1.0
    output_path=Path("vocals_clean.wav")
)
```

### Harmony Generation

Add harmonic layers:

```python
harmony_path = effects.add_harmony(
    audio_path=Path("vocals.wav"),
    harmony_intervals=[4, 7],  # Major third and perfect fifth
    output_path=Path("vocals_harmony.wav")
)
```

## Lyrics Synthesis

### Basic Lyrics

```python
synthesis = get_voice_synthesis()
profile = get_voice_profile("female_singer_1")

lyrics = """
[Verse 1]
In the morning light
I see your face so bright

[Chorus]
Oh yeah, we're flying high
Reaching for the sky
"""

audio_path = synthesis.synthesize_lyrics(
    lyrics=lyrics,
    voice_profile=profile,
    output_path=Path("song_vocals.wav"),
    chunk_sentences=True  # Chunk by line breaks
)
```

### Advanced Chunking

```python
# Custom chunking for long lyrics
def custom_chunk_lyrics(lyrics: str) -> list[str]:
    """Chunk lyrics by verses."""
    sections = lyrics.split('\n\n')
    return [s.strip() for s in sections if s.strip()]

chunks = custom_chunk_lyrics(lyrics)

# Synthesize each chunk separately
for i, chunk in enumerate(chunks):
    chunk_path = Path(f"verse_{i}.wav")
    synthesis.synthesize_text(
        text=chunk,
        voice_profile=profile,
        output_path=chunk_path
    )
```

## API Usage

### REST API Endpoints

#### List Voice Profiles

```bash
curl http://localhost:8000/api/v1/voice/profiles
```

Response:
```json
[
  {
    "id": "male_narrator_1",
    "name": "Male Narrator",
    "gender": "male",
    "language": "en",
    "accent": "american",
    "age_range": "adult",
    "description": "Deep, clear male voice...",
    "engine": "bark"
  }
]
```

#### Synthesize Text

```bash
curl -X POST http://localhost:8000/api/v1/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "voice_profile_id": "male_narrator_1",
    "temperature": 0.7,
    "speed": 1.0
  }'
```

#### Adjust Pitch

```bash
curl -X POST http://localhost:8000/api/v1/voice/adjust/pitch \
  -F "file=@vocals.wav" \
  -F "semitones=3" \
  -o vocals_shifted.wav
```

#### Apply Effects

```bash
curl -X POST http://localhost:8000/api/v1/voice/effects \
  -F "file=@vocals.wav" \
  -F 'effects={"reverb":{"room_size":0.7,"wet_level":0.4},"compression":{"threshold":-20,"ratio":4}}' \
  -o vocals_processed.wav
```

## Best Practices

### 1. Voice Selection

- **Narration**: Use `male_narrator_1` or `neutral_soft`
- **Singing**: Use `female_singer_1` or `male_singer_1`
- **Character voices**: Use Bark with different temperature settings

### 2. Pitch Adjustment

- **Natural range**: ±3 semitones
- **Character effect**: ±5-7 semitones
- **Extreme effect**: ±12 semitones

### 3. Tempo Control

- **Natural variation**: 0.9x - 1.1x
- **Noticeable change**: 0.75x - 1.25x
- **Extreme effect**: 0.5x - 2.0x

### 4. Effects Chain

Recommended order:
1. Noise reduction (if needed)
2. EQ
3. Compression
4. Reverb
5. Echo

### 5. Performance

- **Fast generation**: Use Coqui TTS
- **Best quality**: Use Bark
- **Batch processing**: Process multiple chunks in parallel

## Troubleshooting

### Common Issues

#### 1. Slow Generation

**Problem**: TTS generation takes too long

**Solutions**:
- Switch to Coqui TTS for faster generation
- Use shorter text chunks
- Enable GPU acceleration (if available)

#### 2. Poor Quality

**Problem**: Generated audio sounds robotic

**Solutions**:
- Use Bark engine for natural prosody
- Adjust temperature (try 0.6-0.8)
- Add slight reverb to smooth output

#### 3. Pitch Artifacts

**Problem**: Pitch shifting sounds unnatural

**Solutions**:
- Install `pyrubberband` for better quality
- Keep pitch shifts within ±7 semitones
- Apply compression after pitch shifting

#### 4. Memory Issues

**Problem**: Out of memory errors

**Solutions**:
- Process audio in smaller chunks
- Reduce batch size
- Close unused TTS models

## Performance Optimization

### Caching

```python
from app.services.cache import get_cache_service

cache = get_cache_service()

# Cache synthesized audio
cache_key = f"voice:{voice_id}:{text_hash}"
cached_audio = cache.get(cache_key)

if not cached_audio:
    audio_path = synthesis.synthesize_text(...)
    cache.set(cache_key, str(audio_path), expire=3600)
```

### Parallel Processing

```python
import asyncio

async def process_lyrics_parallel(lyrics_chunks: list[str]):
    tasks = [
        synthesize_chunk(chunk, i)
        for i, chunk in enumerate(lyrics_chunks)
    ]
    return await asyncio.gather(*tasks)
```

## Future Enhancements

- [ ] Voice cloning from samples
- [ ] Real-time pitch correction
- [ ] Advanced auto-tune with scale detection
- [ ] More TTS engines (Azure, Google)
- [ ] Voice style transfer
- [ ] Emotion control API
- [ ] Prosody editing UI

## References

- [Bark Documentation](https://github.com/suno-ai/bark)
- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [pyrubberband Documentation](https://github.com/bmcfee/pyrubberband)
- [librosa Documentation](https://librosa.org/doc/latest/)

## Support

For issues or questions:
- Check the [API Reference](./API_REFERENCE.md)
- Review [examples](../examples/voice_synthesis/)
- Open an issue on GitHub
