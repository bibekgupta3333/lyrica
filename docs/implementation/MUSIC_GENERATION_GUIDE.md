# Music Generation & Composition Guide

## Overview

The Lyrica Music Generation System provides AI-powered music composition capabilities using Meta's MusicGen, combined with music theory-based chord progressions and MIDI melody generation. This guide covers the complete music generation pipeline.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                 Music Generation System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐     ┌─────────────────────┐          │
│  │  MusicGen AI     │     │  Configuration      │          │
│  │  - Text-to-music │────▶│  - 15 Genres       │          │
│  │  - Genre-based   │     │  - 19 Keys         │          │
│  │  - Instrumental  │     │  - 10 Moods        │          │
│  │  - Structured    │     │  - BPM Ranges      │          │
│  └──────────────────┘     └─────────────────────┘          │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Music Generation Service                    │    │
│  │  - AI music composition                             │    │
│  │  - Genre-specific generation                        │    │
│  │  - Melody conditioning                              │    │
│  │  - Structured composition                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Chord Progression Service                   │    │
│  │  - Music theory-based generation                    │    │
│  │  - Genre-specific patterns                          │    │
│  │  - Roman numeral system                             │    │
│  │  - Transposition                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                   │                         │
│  ┌────────────────────────────────▼───────────────────┐    │
│  │         Melody Generation Service                   │    │
│  │  - MIDI melody creation                             │    │
│  │  - Scale-based composition                          │    │
│  │  - Pentatonic melodies                              │    │
│  │  - MIDI to audio conversion                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Supported Genres

Lyrica supports 15 music genres, each with specific characteristics:

| Genre | BPM Range | Typical Instruments | Common Progressions |
|-------|-----------|---------------------|---------------------|
| Pop | 100-130 | Piano, Guitar, Bass, Drums, Synth | I-V-vi-IV, vi-IV-I-V |
| Rock | 110-140 | Guitar, Bass, Drums | I-IV-V-IV, I-bVII-IV-I |
| Hip-Hop | 80-110 | Bass, Drums, Synth | Various, sample-based |
| Electronic | 120-140 | Synth, Bass, Drums | i-bVI-bVII-i |
| Jazz | 100-160 | Piano, Bass, Drums, Brass | IIm7-V7-Imaj7 |
| Classical | 60-120 | Piano, Strings | Complex, varied |
| Country | 90-120 | Guitar, Bass, Drums | I-IV-V, I-V-vi-IV |
| R&B | 70-110 | Piano, Bass, Drums, Synth | Various, smooth progressions |
| Indie | 90-130 | Guitar, Bass, Drums | Creative, varied |
| Folk | 80-120 | Guitar, Vocals | Simple progressions |
| Metal | 140-200 | Guitar, Bass, Drums | i-bVII-bVI-V |
| Blues | 80-120 | Guitar, Bass, Drums | 12-bar blues (I7-IV7-V7) |
| Reggae | 80-110 | Guitar, Bass, Drums | I-V-vi-IV offbeat |
| Latin | 100-140 | Guitar, Percussion, Bass | Various, rhythmic |
| Ambient | 60-90 | Synth, Pads | Atmospheric, minimal |

## MusicGen AI

### Overview

MusicGen is Meta's AI model that generates high-quality music from text descriptions. It understands:
- Genre and style
- Instrumentation
- Mood and energy
- Musical characteristics

### Text-to-Music Generation

```python
from app.services.music import get_music_generation

music_service = get_music_generation()

# Generate music from text prompt
audio_path = music_service.generate_music(
    prompt="upbeat pop music with piano and drums, 120 BPM",
    duration=30,  # seconds
    temperature=1.0  # creativity (0.5-2.0)
)
```

### Genre-Based Generation

```python
from app.core.music_config import MusicGenre, MusicMood, MusicKey

# Generate genre-specific music
audio_path = music_service.generate_by_genre(
    genre=MusicGenre.ROCK,
    mood=MusicMood.ENERGETIC,
    key=MusicKey.D_MAJOR,
    bpm=140,
    duration=30
)
```

### Instrumental Generation

```python
# Generate with specific instruments
audio_path = music_service.generate_instrumental(
    instruments=["piano", "violin", "cello"],
    genre=MusicGenre.CLASSICAL,
    duration=60
)
```

### Structured Composition

```python
# Generate music with song structure
sections = [
    ("intro", 8),
    ("verse", 16),
    ("chorus", 16),
    ("verse", 16),
    ("chorus", 16),
    ("bridge", 8),
    ("chorus", 16),
    ("outro", 8)
]

audio_path = music_service.generate_structure(
    sections=sections,
    genre=MusicGenre.POP
)
```

### Melody Conditioning

```python
from pathlib import Path

# Generate music based on existing melody
melody_path = Path("my_melody.wav")

audio_path = music_service.generate_with_melody(
    melody_audio_path=melody_path,
    genre=MusicGenre.POP,
    duration=30
)
```

## Chord Progressions

### Music Theory-Based Generation

```python
from app.services.music import get_chord_service
from app.core.music_config import MusicKey, MusicGenre

chord_service = get_chord_service()

# Generate chord progression
chords = chord_service.generate_progression(
    key=MusicKey.C_MAJOR,
    genre=MusicGenre.POP,
    num_chords=4
)
# Returns: ['C', 'G', 'Am', 'F']
```

### Genre-Specific Patterns

Each genre has characteristic chord progressions:

**Pop:**
- I-V-vi-IV (C-G-Am-F)
- vi-IV-I-V (Am-F-C-G)
- I-vi-IV-V (C-Am-F-G)

**Rock:**
- I-IV-V-IV (C-F-G-F)
- I-bVII-IV-I (C-Bb-F-C)
- i-bVII-bVI-V (Cm-Bb-Ab-G)

**Jazz:**
- IIm7-V7-Imaj7 (Dm7-G7-Cmaj7)
- Im7-IVm7-bVII7-IIImaj7

**Blues:**
- 12-bar blues: I7-I7-I7-I7-IV7-IV7-I7-I7-V7-IV7-I7-V7

### Random Progression Generation

```python
# Generate random but musically valid progression
chords = chord_service.generate_random_progression(
    key=MusicKey.G_MAJOR,
    num_chords=6,
    allow_complex=True  # Include 7th chords
)
```

### Progression Analysis

```python
# Analyze a chord progression
chords = ['C', 'Am', 'F', 'G', 'C']

analysis = chord_service.analyze_progression(chords)
# Returns:
# {
#     "num_chords": 5,
#     "unique_chords": 4,
#     "chord_types": {"major": 3, "minor": 1},
#     "complexity": "simple"
# }
```

### Transposition

```python
# Transpose progression up 3 semitones
original = ['C', 'Am', 'F', 'G']
transposed = chord_service.transpose_progression(original, semitones=3)
# Returns: ['D#', 'Cm', 'G#', 'A#']

# Transpose down 2 semitones
transposed = chord_service.transpose_progression(original, semitones=-2)
# Returns: ['A#', 'Gm', 'D#', 'F']
```

## Melody Generation

### MIDI Melody Creation

```python
from app.services.music import get_melody_service
from app.core.music_config import MusicKey, MusicGenre

melody_service = get_melody_service()

# Generate MIDI melody
midi_path = melody_service.generate_melody(
    key=MusicKey.C_MAJOR,
    num_notes=16,
    duration_seconds=8,
    genre=MusicGenre.POP
)
```

### Pentatonic Melodies

Pentatonic scales are simpler and more consonant, ideal for catchy melodies:

```python
# Generate pentatonic melody
midi_path = melody_service.generate_pentatonic_melody(
    key=MusicKey.A_MINOR,
    num_notes=24
)
```

### MIDI to Audio Conversion

```python
from pathlib import Path

# Convert MIDI to WAV audio
midi_path = Path("melody.mid")
audio_path = melody_service.midi_to_audio(
    midi_path=midi_path,
    output_path=Path("melody.wav")
)
```

### Scale Types

Lyrica supports multiple scale types:

**Major Scale:**
- Intervals: 0, 2, 4, 5, 7, 9, 11
- Mood: Happy, bright
- Example (C Major): C, D, E, F, G, A, B

**Minor Scale:**
- Intervals: 0, 2, 3, 5, 7, 8, 10
- Mood: Sad, dark
- Example (A Minor): A, B, C, D, E, F, G

**Pentatonic Major:**
- Intervals: 0, 2, 4, 7, 9
- Mood: Simple, consonant
- Example (C Pentatonic): C, D, E, G, A

**Pentatonic Minor:**
- Intervals: 0, 3, 5, 7, 10
- Mood: Bluesy, soulful
- Example (A Minor Pentatonic): A, C, D, E, G

## Musical Parameters

### Keys

19 available keys:

**Major Keys:**
C, C#, D, D#, E, F, F#, G, G#, A, A#, B

**Minor Keys:**
Am, Bm, Cm, Dm, Em, Fm, Gm

### BPM (Tempo)

- **Range:** 40-200 BPM
- **Slow:** 60-80 (Ballads, Ambient)
- **Moderate:** 90-110 (Pop, R&B)
- **Fast:** 120-140 (Electronic, Rock)
- **Very Fast:** 150-200 (Metal, Speed Rock)

### Duration

- **Minimum:** 5 seconds
- **Maximum:** 300 seconds (5 minutes)
- **Typical:** 30-60 seconds for samples

### Audio Quality

- **Sample Rate:** 32kHz
- **Channels:** Stereo (2)
- **Bit Depth:** 16-bit
- **Format:** WAV (uncompressed)

## API Usage

### REST API Endpoints

#### Generate from Text Prompt

```bash
curl -X POST http://localhost:8000/api/v1/music/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "upbeat electronic dance music with synth and bass",
    "duration": 30,
    "temperature": 1.0
  }'
```

Response:
```json
{
  "file_path": "audio_files/music/music_upbeat_electronic.wav",
  "duration_seconds": 30,
  "genre": null,
  "key": null,
  "bpm": null,
  "message": "Music generated successfully from prompt"
}
```

#### Generate by Genre

```bash
curl -X POST http://localhost:8000/api/v1/music/generate/genre \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "jazz",
    "mood": "calm",
    "key": "F",
    "bpm": 120,
    "duration": 45
  }'
```

#### Generate Instrumental

```bash
curl -X POST http://localhost:8000/api/v1/music/generate/instrumental \
  -H "Content-Type: application/json" \
  -d '{
    "instruments": ["piano", "violin", "cello", "flute"],
    "genre": "classical",
    "duration": 60
  }'
```

#### Generate Structured Music

```bash
curl -X POST http://localhost:8000/api/v1/music/generate/structured \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [
      ["intro", 8],
      ["verse", 16],
      ["chorus", 16],
      ["verse", 16],
      ["chorus", 16],
      ["outro", 8]
    ],
    "genre": "rock",
    "key": "E",
    "bpm": 130
  }'
```

#### Generate Chord Progression

```bash
curl -X POST http://localhost:8000/api/v1/music/chords/generate \
  -H "Content-Type: application/json" \
  -d '{
    "key": "G",
    "genre": "pop",
    "num_chords": 4
  }'
```

Response:
```json
{
  "chords": ["G", "D", "Em", "C"],
  "key": "G",
  "analysis": {
    "num_chords": 4,
    "unique_chords": 4,
    "chord_types": {
      "major": 3,
      "minor": 1
    },
    "complexity": "simple"
  }
}
```

#### Generate Melody

```bash
curl -X POST http://localhost:8000/api/v1/music/melody/generate \
  -H "Content-Type: application/json" \
  -d '{
    "key": "D",
    "num_notes": 32,
    "duration": 16,
    "genre": "indie",
    "pentatonic": false
  }' \
  -o melody.mid
```

#### List Genres

```bash
curl http://localhost:8000/api/v1/music/genres
```

Response:
```json
{
  "genres": [
    "pop", "rock", "hiphop", "electronic", "jazz",
    "classical", "country", "rnb", "indie", "folk",
    "metal", "blues", "reggae", "latin", "ambient"
  ],
  "count": 15
}
```

#### Get Genre Info

```bash
curl http://localhost:8000/api/v1/music/genres/rock/info
```

Response:
```json
{
  "genre": "rock",
  "bpm_range": {
    "min": 110,
    "max": 140,
    "typical": 125
  },
  "description": "Rock music"
}
```

## Best Practices

### 1. Prompt Engineering

**Good Prompts:**
- "upbeat pop music with piano melody and electronic drums, 120 BPM"
- "dark atmospheric ambient music with deep bass and ethereal pads"
- "energetic rock guitar riff with driving drums and bass"
- "smooth jazz piano with walking bass and brushed drums"

**Bad Prompts:**
- "music" (too vague)
- "something cool" (not descriptive)
- "loud" (needs more context)

### 2. Genre Selection

- Use genre for consistent style
- Combine genre with mood for better results
- Specify key and BPM for tighter control

### 3. Duration Management

- **Short (5-15s):** Loops, intros, transitions
- **Medium (15-45s):** Song sections, samples
- **Long (45-120s):** Full segments, instrumentals
- **Very Long (120-300s):** Complete compositions

### 4. Chord Progressions

- Start with genre-specific progressions
- Use common progressions for familiarity
- Add complex chords (7ths) for sophistication
- Keep it simple for catchy melodies

### 5. Melody Generation

- Use pentatonic for catchy, safe melodies
- Use major/minor for full range
- Match melody key to song key
- Consider note range (stay within C3-C6)

### 6. Temperature Control

- **0.5-0.7:** Conservative, predictable
- **0.8-1.0:** Balanced creativity
- **1.1-1.5:** More experimental
- **1.6-2.0:** Very creative, risky

## Workflow Examples

### Example 1: Create a Pop Song Backing Track

```python
from app.services.music import (
    get_music_generation,
    get_chord_service,
    get_melody_service
)
from app.core.music_config import MusicGenre, MusicKey, MusicMood

# Step 1: Generate chord progression
chord_service = get_chord_service()
chords = chord_service.generate_progression(
    key=MusicKey.C_MAJOR,
    genre=MusicGenre.POP,
    num_chords=4
)
print(f"Chords: {chords}")  # ['C', 'G', 'Am', 'F']

# Step 2: Generate melody
melody_service = get_melody_service()
melody_midi = melody_service.generate_pentatonic_melody(
    key=MusicKey.C_MAJOR,
    num_notes=32
)
melody_audio = melody_service.midi_to_audio(melody_midi)

# Step 3: Generate backing track
music_service = get_music_generation()
backing_track = music_service.generate_by_genre(
    genre=MusicGenre.POP,
    mood=MusicMood.HAPPY,
    key=MusicKey.C_MAJOR,
    bpm=120,
    duration=60
)

# Step 4: Mix melody with backing track (use audio mixer)
# See Audio Processing guide
```

### Example 2: Create Structured Rock Song

```python
# Define song structure
sections = [
    ("intro", 8),       # 8 seconds
    ("verse", 16),      # 16 seconds
    ("chorus", 16),     # 16 seconds
    ("verse", 16),      # 16 seconds
    ("chorus", 16),     # 16 seconds
    ("bridge", 12),     # 12 seconds
    ("chorus", 16),     # 16 seconds
    ("outro", 8)        # 8 seconds
]

# Generate complete song
music_service = get_music_generation()
song = music_service.generate_structure(
    sections=sections,
    genre=MusicGenre.ROCK
)

# Total duration: 108 seconds (~1:48)
```

### Example 3: Generate Genre-Specific Instrumentals

```python
# Classical piano piece
classical = music_service.generate_instrumental(
    instruments=["piano", "strings"],
    genre=MusicGenre.CLASSICAL,
    duration=90
)

# Jazz combo
jazz = music_service.generate_instrumental(
    instruments=["piano", "bass", "drums", "saxophone"],
    genre=MusicGenre.JAZZ,
    duration=120
)

# Electronic dance
electronic = music_service.generate_instrumental(
    instruments=["synth", "bass", "drums"],
    genre=MusicGenre.ELECTRONIC,
    duration=180
)
```

## Troubleshooting

### Common Issues

#### 1. Slow Generation

**Problem:** Music generation takes too long

**Solutions:**
- Use shorter durations (< 30 seconds)
- Enable GPU acceleration if available
- Use smaller MusicGen model
- Generate sections separately

#### 2. Poor Quality Output

**Problem:** Generated music sounds bad

**Solutions:**
- Improve text prompt (be more specific)
- Adjust temperature (try 0.8-1.0)
- Specify genre and mood explicitly
- Use melody conditioning for better results

#### 3. Out of Memory Errors

**Problem:** System runs out of memory

**Solutions:**
- Reduce duration
- Use smaller model (`musicgen-small`)
- Close other applications
- Generate in smaller chunks

#### 4. MIDI Not Converting to Audio

**Problem:** MIDI to audio conversion fails

**Solutions:**
- Install FluidSynth: `brew install fluid-synth` (macOS)
- Check MIDI file is valid
- Ensure sufficient disk space

#### 5. Inconsistent Results

**Problem:** Same prompt produces different results

**Solutions:**
- This is expected behavior (AI creativity)
- Lower temperature for consistency
- Use seed parameter if available
- Generate multiple versions and select best

## Performance Optimization

### Caching

```python
from app.services.cache import get_cache_service
import hashlib

cache = get_cache_service()

def generate_with_cache(prompt: str, duration: int):
    # Create cache key
    cache_key = f"music:{hashlib.md5(prompt.encode()).hexdigest()}:{duration}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Generate
    audio_path = music_service.generate_music(prompt, duration)
    
    # Cache result
    cache.set(cache_key, str(audio_path), expire=3600)  # 1 hour
    
    return audio_path
```

### Batch Processing

```python
import asyncio

async def generate_multiple_tracks(prompts: list[str]):
    tasks = [
        asyncio.to_thread(
            music_service.generate_music,
            prompt=prompt,
            duration=30
        )
        for prompt in prompts
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### Resource Management

```python
# Free model memory after generation
music_service._musicgen_model = None

# Use context manager for large batches
with music_service:
    for prompt in prompts:
        audio = music_service.generate_music(prompt, 30)
```

## Advanced Features

### Custom Genre Combinations

```python
# Blend multiple genres
prompt = "rock metal fusion with electronic elements and jazz harmonies"
audio = music_service.generate_music(prompt, duration=60)
```

### Dynamic BPM Changes

```python
# Generate sections with different tempos
intro = music_service.generate_by_genre(
    genre=MusicGenre.POP, bpm=90, duration=8
)

verse = music_service.generate_by_genre(
    genre=MusicGenre.POP, bpm=120, duration=16
)

# Combine using audio mixer
```

### Mood Transitions

```python
from app.core.music_config import MusicMood

# Start calm, build to energetic
sections = [
    (MusicMood.CALM, 16),
    (MusicMood.UPLIFTING, 16),
    (MusicMood.ENERGETIC, 32)
]

# Generate each section
for mood, duration in sections:
    audio = music_service.generate_by_genre(
        genre=MusicGenre.ELECTRONIC,
        mood=mood,
        duration=duration
    )
```

## Integration with Other Systems

### Combine with Voice Synthesis

```python
from app.services.voice import get_voice_synthesis
from app.core.voice_config import get_voice_profile

# 1. Generate lyrics
lyrics = "..."  # From lyrics generation

# 2. Synthesize vocals
voice_service = get_voice_synthesis()
profile = get_voice_profile("female_singer_1")
vocals = voice_service.synthesize_lyrics(lyrics, profile, ...)

# 3. Generate backing music
music = music_service.generate_by_genre(
    genre=MusicGenre.POP,
    key=MusicKey.C_MAJOR,
    bpm=120,
    duration=60
)

# 4. Mix vocals with music
# Use Audio Mixer service
```

### Use with Audio Processing

```python
from app.services.audio import (
    get_audio_mixer,
    get_audio_mastering
)

# Generate music
music = music_service.generate_music("upbeat pop", 60)

# Apply mastering
mastering = get_audio_mastering()
mastered = mastering.apply_mastering_chain(
    audio_path=music,
    target_loudness=-14.0
)
```

## Future Enhancements

- [ ] Custom model fine-tuning
- [ ] Real-time generation
- [ ] Interactive composition
- [ ] Style transfer between genres
- [ ] Longer generation (> 5 minutes)
- [ ] Multi-track generation
- [ ] Stem separation
- [ ] MIDI import/export
- [ ] Music theory constraints
- [ ] Adaptive composition

## References

- [MusicGen Paper](https://arxiv.org/abs/2306.05284)
- [AudioCraft Documentation](https://github.com/facebookresearch/audiocraft)
- [Music21 Documentation](https://web.mit.edu/music21/)
- [Pretty MIDI Documentation](https://craffel.github.io/pretty-midi/)
- [Music Theory Primer](https://www.musictheory.net/)

## Support

For issues or questions:
- Check the [API Reference](./API_REFERENCE.md)
- Review [examples](../examples/music_generation/)
- Consult [Music Theory Guide](./MUSIC_THEORY_BASICS.md)
- Open an issue on GitHub
