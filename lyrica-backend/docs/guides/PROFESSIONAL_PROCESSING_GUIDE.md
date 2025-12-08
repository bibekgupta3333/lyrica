# Professional Processing Guide

## Overview

This guide explains the professional processing features implemented in Phase 3 of the Lyrica project, which bring song quality from 60% to 90% professional level.

## Table of Contents

1. [Professional Vocal Processing](#professional-vocal-processing)
2. [Professional Mixing](#professional-mixing)
3. [Professional Mastering](#professional-mastering)
4. [Music Structure](#music-structure)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)

---

## Professional Vocal Processing

### Features

#### 1. Pitch Correction (Auto-Tune)

**Service**: `ProsodyPitchService`

Auto-tune corrects pitch to a target musical key and scale.

```python
from app.services.voice import get_prosody_pitch

prosody_service = get_prosody_pitch()
tuned_audio = prosody_service.auto_tune_with_scale(
    audio_path=Path("vocals.wav"),
    target_key="C",
    scale_type="major",
    strength=0.8
)
```

**Parameters**:
- `target_key`: Musical key (C, D, E, F, G, A, B)
- `scale_type`: Scale type ("major", "minor", "pentatonic")
- `strength`: Correction strength (0.0-1.0)

#### 2. Timing Correction (Quantization)

**Service**: `VocalEffectsService`

Quantizes vocal timing to a beat grid for tighter rhythm.

```python
from app.services.voice import get_vocal_effects

effects_service = get_vocal_effects()
quantized = effects_service.quantize_timing(
    audio_path=Path("vocals.wav"),
    bpm=120.0,
    strength=0.8
)
```

**Parameters**:
- `bpm`: Beats per minute (tempo)
- `strength`: Quantization strength (0.0-1.0)

#### 3. Vocal Doubling

**Service**: `VocalEffectsService`

Adds a slightly delayed and detuned copy for a thicker, more professional sound.

```python
doubled = effects_service.add_vocal_doubling(
    audio_path=Path("vocals.wav"),
    delay_ms=20,
    detune_cents=5.0,
    volume_db=-8.0
)
```

**Parameters**:
- `delay_ms`: Delay in milliseconds (typically 10-30ms)
- `detune_cents`: Detune amount in cents (typically 3-10 cents)
- `volume_db`: Volume of doubled track (typically -6 to -12dB)

#### 4. Harmony Layers

**Service**: `VocalEffectsService`

Adds harmony vocals at specified intervals.

```python
harmonized = effects_service.add_harmony(
    audio_path=Path("vocals.wav"),
    harmony_intervals=[4, 7]  # Major third and perfect fifth
)
```

#### 5. Ad-Libs and Vocal Fills

**Service**: `VocalEffectsService`

Adds background vocal ad-libs at specified positions.

```python
with_adlibs = effects_service.add_ad_libs(
    audio_path=Path("vocals.wav"),
    ad_lib_text="yeah",
    positions=[10.0, 30.0, 50.0],
    volume_db=-6.0
)
```

#### 6. Complete Professional Vocal Chain

**Service**: `VocalEffectsService`

Applies all professional vocal processing in the correct order.

```python
processed = effects_service.apply_professional_vocal_chain(
    audio_path=Path("vocals.wav"),
    enable_auto_tune=True,
    enable_timing=True,
    enable_doubling=True,
    enable_harmony=False,
    enable_ad_libs=False,
    target_key="C",
    scale_type="major",
    bpm=120.0
)
```

---

## Professional Mixing

### Features

#### 1. Multi-Band Compression

**Service**: `MultiBandCompressionService`

Applies compression to different frequency bands independently.

```python
from app.services.production.frequency_balancing import get_multiband_compression

multiband = get_multiband_compression()
compressed = multiband.apply_multiband_compression(
    audio_path=Path("vocals.wav"),
    bands=[
        {"low_freq": 0, "high_freq": 250, "threshold": -18, "ratio": 3.0},
        {"low_freq": 250, "high_freq": 2000, "threshold": -20, "ratio": 4.0},
        {"low_freq": 2000, "high_freq": 20000, "threshold": -22, "ratio": 2.0},
    ]
)
```

#### 2. Dynamic EQ

**Service**: `DynamicEQService`

Applies adaptive EQ based on frequency analysis.

```python
from app.services.production.frequency_balancing import get_dynamic_eq

dynamic_eq = get_dynamic_eq()
eq_audio = dynamic_eq.apply_dynamic_eq(
    audio_path=Path("vocals.wav"),
    genre=MusicGenre.POP
)
```

#### 3. Sidechain Compression

**Service**: `SidechainCompressionService`

Ducks music volume when vocals are present.

```python
from app.services.production.frequency_balancing import get_sidechain_compression

sidechain = get_sidechain_compression()
compressed_music = sidechain.apply_sidechain_compression(
    vocals_path=Path("vocals.wav"),
    music_path=Path("music.wav"),
    threshold_db=-20.0,
    ratio=4.0
)
```

---

## Professional Mastering

### Features

#### 1. Harmonic Enhancement

**Service**: `AudioMasteringService`

Adds subtle harmonic content for richer, warmer sound.

```python
from app.services.audio.mastering import AudioMasteringService

mastering = AudioMasteringService()
enhanced = mastering.apply_harmonic_enhancement(
    audio_path=Path("song.wav"),
    enhancement_strength=0.3
)
```

#### 2. Stereo Enhancement

**Service**: `AudioMasteringService`

Widens the stereo field for a more immersive sound.

```python
widened = mastering.enhance_stereo_width(
    audio_path=Path("song.wav"),
    width_factor=1.1
)
```

#### 3. Complete Mastering Chain

**Service**: `SongMasteringService`

Applies complete mastering chain with all enhancements.

```python
from app.services.production import get_song_mastering

mastering_service = get_song_mastering()
mastered = mastering_service.master_song(
    song_path=Path("mixed.wav"),
    target_loudness=-14.0,
    genre="pop"
)
```

---

## Music Structure

### Features

#### 1. Structure Analysis

**Service**: `MusicStructureService`

Analyzes song structure from audio.

```python
from app.services.music.structure import get_music_structure

structure_service = get_music_structure()
structure = structure_service.analyze_structure(
    audio_path=Path("song.wav"),
    bpm=120.0
)
```

#### 2. Structure Template Generation

**Service**: `MusicStructureService`

Generates genre-specific structure templates.

```python
template = structure_service.generate_structure_template(
    genre=MusicGenre.POP,
    duration=180
)
```

#### 3. Dynamic Changes

**Service**: `MusicStructureService`

Adds dynamic changes (build-ups, drops, transitions) based on structure.

```python
dynamic = structure_service.add_dynamic_changes(
    audio_path=Path("song.wav"),
    structure=template
)
```

---

## Usage Examples

### Complete Professional Song Generation

```python
from pathlib import Path
from app.core.music_config import MusicGenre
from app.services.voice import get_voice_synthesis, get_vocal_effects
from app.services.music import get_music_generation
from app.services.production import get_song_assembly, get_song_mastering

# 1. Generate vocals
voice_service = get_voice_synthesis()
vocals_path = voice_service.synthesize_lyrics(
    lyrics="Verse 1...\nChorus...",
    voice_profile=get_voice_profile("female_singer_1"),
    output_path=Path("vocals_raw.wav")
)

# 2. Apply professional vocal processing
effects_service = get_vocal_effects()
vocals_processed = effects_service.apply_professional_vocal_chain(
    audio_path=vocals_path,
    enable_auto_tune=True,
    enable_timing=True,
    enable_doubling=True,
    target_key="C",
    scale_type="major",
    bpm=120.0,
    output_path=Path("vocals_professional.wav")
)

# 3. Generate music
music_service = get_music_generation()
music_path = music_service.generate_by_genre(
    genre=MusicGenre.POP,
    duration=180,
    output_path=Path("music.wav")
)

# 4. Mix with professional processing
assembly_service = get_song_assembly()
mixed_path = assembly_service.assemble_song(
    vocals_path=vocals_processed,
    music_path=music_path,
    output_path=Path("mixed.wav"),
    use_intelligent_mixing=True,
    genre=MusicGenre.POP
)

# 5. Master with enhancements
mastering_service = get_song_mastering()
final_path = mastering_service.master_song(
    song_path=mixed_path,
    target_loudness=-14.0,
    genre="pop",
    output_path=Path("final_mastered.wav")
)
```

---

## Best Practices

### Vocal Processing

1. **Order Matters**: Always apply processing in this order:
   - Timing correction (quantization)
   - Pitch correction (auto-tune)
   - Vocal doubling
   - Harmony layers
   - Ad-libs
   - Effects chain (compression, EQ, reverb, delay)

2. **Moderation**: Don't over-process vocals. Use subtle settings:
   - Auto-tune strength: 0.6-0.8
   - Doubling delay: 15-25ms
   - Doubling detune: 3-7 cents

3. **Genre-Specific**: Adjust settings based on genre:
   - Pop: More auto-tune, more doubling
   - Rock: Less auto-tune, more natural
   - Hip-Hop: Strong auto-tune, minimal doubling

### Mixing

1. **Frequency Balance**: Use multi-band compression to balance frequencies
2. **Sidechain**: Always use sidechain compression for vocals + music
3. **Stereo Width**: Keep vocals centered, widen music

### Mastering

1. **Loudness Standards**:
   - Streaming (Spotify, YouTube): -14 LUFS
   - Apple Music: -16 LUFS
   - Broadcast: -23 LUFS

2. **Harmonic Enhancement**: Use subtle enhancement (0.2-0.3 strength)
3. **Stereo Width**: Moderate widening (1.1-1.2 factor)

### Structure

1. **Genre Templates**: Use genre-specific structure templates
2. **Dynamic Changes**: Add build-ups and drops for interest
3. **Transitions**: Smooth transitions between sections

---

## Troubleshooting

### Common Issues

1. **Over-processed Vocals**
   - Reduce auto-tune strength
   - Reduce doubling amount
   - Use less aggressive effects

2. **Muddy Mix**
   - Check frequency balance
   - Reduce low-frequency content
   - Use multi-band compression

3. **Clipping**
   - Reduce input levels
   - Use proper headroom
   - Check mastering chain

---

## References

- [Voice Enhancement Documentation](../implementation/PHASE1_VOICE_ENHANCEMENT.md)
- [Mixing Documentation](../implementation/ENHANCEMENT_TECHNICAL_DOCS.md)
- [API Documentation](../../app/api/v1/endpoints/enhancement.py)
