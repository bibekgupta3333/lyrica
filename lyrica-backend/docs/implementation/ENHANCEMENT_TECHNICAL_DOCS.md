# AI Music & Voice Enhancement - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Service Architecture](#service-architecture)
5. [Configuration](#configuration)
6. [Integration Guide](#integration-guide)
7. [Database Schema](#database-schema)
8. [Memory System](#memory-system)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Music & Voice Enhancement system transforms basic TTS output into professional-quality vocals and implements intelligent, AI-driven music mixing. The system learns from user feedback and continuously improves through a memory-based learning mechanism.

### Key Features

- **Voice Enhancement**: Neural vocoders, prosody enhancement, auto-tune
- **Intelligent Mixing**: Dynamic EQ, sidechain compression, stereo imaging, genre-specific presets
- **Memory System**: Learning from feedback, configuration optimization, quality tracking
- **Quality Metrics**: PESQ, STOI, MOS scoring for objective quality assessment

### Technology Stack

- **Voice Enhancement**: Vocos (neural vocoder), CREPE (pitch tracking), librosa (audio processing)
- **Mixing**: librosa, scipy, pydub (audio processing and effects)
- **Memory**: PostgreSQL (persistent storage), Redis (caching), ChromaDB (vector storage)
- **Agents**: LangGraph (orchestration), MemoryAgent (learning)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  /enhancement/voice, /enhancement/mixing, /enhancement/complete │
└──────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Unified Pipeline Service                       │
│  - Voice Enhancement Service                                │
│  - Music Generation Service                                 │
│  - Song Assembly Service                                    │
│  - Song Mastering Service                                   │
└──────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Enhancement Services                           │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Voice Enhancement│  │ Mixing Enhancement│               │
│  │ - Vocos Vocoder  │  │ - Dynamic EQ      │               │
│  │ - Prosody        │  │ - Sidechain       │               │
│  │ - Auto-tune      │  │ - Stereo Imaging │               │
│  └──────────────────┘  └──────────────────┘               │
└──────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory System                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ PostgreSQL   │  │ Redis Cache  │  │ ChromaDB     │    │
│  │ - Configs    │  │ - Fast Lookup│  │ - Vectors    │    │
│  │ - Feedback   │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Request Received**: API endpoint receives enhancement request
2. **Configuration Load**: Load enhancement config (defaults + overrides)
3. **Voice Enhancement** (if enabled):
   - Apply neural vocoder (Vocos)
   - Apply prosody enhancement
   - Apply auto-tune (if enabled)
4. **Music Generation** (if needed):
   - Generate instrumental music
5. **Intelligent Mixing** (if enabled):
   - Get mixing recommendations from memory
   - Apply dynamic EQ
   - Apply sidechain compression
   - Apply stereo imaging
   - Apply genre-specific presets
6. **Mastering**: Final mastering (LUFS normalization, compression)
7. **Quality Tracking**: Calculate quality metrics (PESQ, STOI, MOS)
8. **Memory Learning**: Store feedback and optimize configurations

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1/enhancement
```

### Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### 1. Voice Enhancement

**POST** `/enhancement/voice`

Enhance voice audio quality using neural vocoder, prosody enhancement, and auto-tune.

**Request Body**:

```json
{
  "audio_path": "audio_files/songs/song_123/vocals.wav",
  "enable_neural_vocoder": true,
  "enable_prosody": true,
  "enable_auto_tune": false,
  "target_key": "C major"
}
```

**Response**:

```json
{
  "success": true,
  "enhanced_audio_path": "audio_files/songs/song_123/vocals_enhanced.wav",
  "quality_metrics": {
    "pesq": 3.2,
    "stoi": 0.85,
    "mos": 4.1,
    "overall": 4.0
  },
  "enhancement_applied": ["voice_enhancement"],
  "warnings": []
}
```

**Status Codes**:

- `200 OK`: Enhancement successful
- `404 NOT FOUND`: Audio file not found
- `500 INTERNAL SERVER ERROR`: Enhancement failed

---

#### 2. Mixing Enhancement

**POST** `/enhancement/mixing`

Apply intelligent mixing to vocals and music tracks.

**Request Body**:

```json
{
  "vocals_path": "audio_files/songs/song_123/vocals.wav",
  "music_path": "audio_files/songs/song_123/music.wav",
  "genre": "pop",
  "enable_frequency_balancing": true,
  "enable_sidechain": true,
  "enable_stereo_imaging": true,
  "mixing_config_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:

```json
{
  "success": true,
  "enhanced_audio_path": "audio_files/songs/song_123/mixed_enhanced.wav",
  "quality_metrics": {
    "pesq": 3.5,
    "stoi": 0.88,
    "mos": 4.3,
    "overall": 4.2
  },
  "enhancement_applied": ["mixing", "frequency_balancing", "sidechain_compression", "stereo_imaging"],
  "warnings": []
}
```

**Status Codes**:

- `200 OK`: Mixing successful
- `404 NOT FOUND`: Audio files not found
- `500 INTERNAL SERVER ERROR`: Mixing failed

---

#### 3. Complete Song Enhancement

**POST** `/enhancement/complete`

Apply complete enhancement pipeline to an existing song.

**Request Body**:

```json
{
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhancement_config": {
    "enable_voice_enhancement": true,
    "enable_prosody_enhancement": true,
    "enable_auto_tune": false,
    "enable_intelligent_mixing": true,
    "enable_stereo_imaging": true,
    "enable_genre_specific_mixing": true,
    "enable_memory_learning": true,
    "track_quality_metrics": true
  }
}
```

**Response**:

```json
{
  "success": true,
  "enhanced_audio_path": "audio_files/songs/song_123/song_enhanced.wav",
  "quality_metrics": {
    "pesq": 3.6,
    "stoi": 0.90,
    "mos": 4.4,
    "overall": 4.3
  },
  "enhancement_applied": ["voice_enhancement", "intelligent_mixing"],
  "warnings": []
}
```

**Status Codes**:

- `200 OK`: Enhancement successful
- `404 NOT FOUND`: Song not found
- `403 FORBIDDEN`: User doesn't have permission
- `500 INTERNAL SERVER ERROR`: Enhancement failed

---

## Service Architecture

### Voice Enhancement Service

**Location**: `app/services/voice/enhancement.py`

**Key Methods**:

- `enhance_tts_output(tts_audio_path, output_path, enable_enhancement=True)`: Apply neural vocoder enhancement
- `enhance_audio(audio_path, output_path, method="auto")`: General audio enhancement

**Dependencies**:

- Vocos (neural vocoder)
- librosa (audio processing)
- numpy, scipy (signal processing)

**Fallback Chain**:

1. Try Vocos neural vocoder
2. Fallback to HiFi-GAN (if available)
3. Fallback to audio processing (EQ, compression, denoising)

---

### Prosody & Pitch Service

**Location**: `app/services/voice/prosody_pitch.py`

**Key Methods**:

- `track_pitch(audio_path, method="crepe")`: Track pitch using CREPE or librosa
- `predict_prosody(lyrics, use_llm=True)`: Predict prosody from lyrics
- `auto_tune_with_scale(audio_path, target_key, output_path)`: Apply auto-tune

**Dependencies**:

- CREPE (pitch tracking)
- librosa (fallback pitch tracking)
- LLM (for prosody prediction)

---

### Quality Metrics Service

**Location**: `app/services/voice/quality_metrics.py`

**Key Methods**:

- `calculate_pesq(reference_path, degraded_path)`: Calculate PESQ score
- `calculate_stoi(reference_path, degraded_path)`: Calculate STOI score
- `estimate_mos(audio_path)`: Estimate MOS score
- `calculate_all_metrics(audio_path, reference_path=None)`: Calculate all metrics

**Dependencies**:

- pesq (PESQ calculation)
- pystoi (STOI calculation)
- librosa (audio analysis)

---

### Frequency Balancing Service

**Location**: `app/services/production/frequency_balancing.py`

**Key Services**:

- `FrequencyAnalysisService`: Analyze frequency content
- `DynamicEQService`: Apply dynamic EQ based on frequency analysis
- `SidechainCompressionService`: Apply sidechain compression

**Key Methods**:

- `analyze_frequency_content(audio_path)`: Analyze spectral features
- `apply_dynamic_eq(audio_path, output_path, genre=None)`: Apply dynamic EQ
- `apply_sidechain_compression(music_path, vocals_path, output_path)`: Apply sidechain

---

### Stereo Imaging Service

**Location**: `app/services/production/stereo_imaging.py`

**Key Methods**:

- `measure_stereo_width(audio_path)`: Measure stereo width
- `enhance_stereo_width(audio_path, output_path, width_factor=1.2)`: Enhance stereo width
- `add_spatial_reverb(audio_path, output_path, room_size=0.5)`: Add spatial reverb
- `add_spatial_delay(audio_path, output_path, delay_ms=200)`: Add spatial delay

---

### Genre Mixing Service

**Location**: `app/services/production/genre_mixing.py`

**Key Services**:

- `GenreClassificationService`: Classify music genre from audio
- `GenreMixingPresetsService`: Get genre-specific mixing presets
- `ReferenceTrackAnalysisService`: Analyze reference tracks

---

### Unified Pipeline Service

**Location**: `app/services/production/unified_pipeline.py`

**Key Method**:

- `generate_complete_song_with_enhancement(...)`: End-to-end song generation with enhancement

**Pipeline Steps**:

1. Generate vocals
2. Enhance vocals (if enabled)
3. Generate music
4. Get mixing recommendations from memory
5. Mix vocals and music
6. Master song
7. Create preview
8. Track quality metrics

---

## Configuration

### Enhancement Configuration

**Location**: `app/core/enhancement_config.py`

**Default Settings**:

```python
class EnhancementSettings(BaseModel):
    # Voice Enhancement
    voice_enhancement_enabled: bool = True
    neural_vocoder_enabled: bool = True
    prosody_enhancement_enabled: bool = True
    auto_tune_enabled: bool = False
    
    # Mixing Enhancement
    intelligent_mixing_enabled: bool = True
    frequency_balancing_enabled: bool = True
    sidechain_compression_enabled: bool = True
    stereo_imaging_enabled: bool = True
    genre_specific_mixing_enabled: bool = True
    
    # Memory & Learning
    memory_learning_enabled: bool = True
    quality_tracking_enabled: bool = True
    
    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    parallel_processing: bool = False
    fallback_on_error: bool = True
```

### Environment Variables

```bash
# Voice Enhancement
ENABLE_VOICE_ENHANCEMENT=true
ENABLE_NEURAL_VOCODER=true
ENABLE_PROSODY_ENHANCEMENT=true

# Mixing Enhancement
ENABLE_INTELLIGENT_MIXING=true
ENABLE_FREQUENCY_BALANCING=true
ENABLE_SIDECHAIN_COMPRESSION=true
ENABLE_STEREO_IMAGING=true

# Memory System
ENABLE_MEMORY_LEARNING=true
ENABLE_QUALITY_TRACKING=true

# Performance
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
PARALLEL_PROCESSING=false
FALLBACK_ON_ERROR=true
```

---

## Integration Guide

### Integrating with Existing Song Generation

The enhancement system integrates seamlessly with the existing song generation pipeline:

```python
from app.services.production.unified_pipeline import get_unified_pipeline

pipeline = get_unified_pipeline()

result = await pipeline.generate_complete_song_with_enhancement(
    lyrics_text="Your lyrics here",
    voice_profile_id="female_singer_1",
    genre="pop",
    bpm=120,
    key="C major",
    duration=180,
    output_dir=Path("output"),
    db=db_session,
    user_id=user_id,
    enable_voice_enhancement=True,
    enable_intelligent_mixing=True,
    enable_memory_learning=True
)
```

### Using Individual Services

#### Voice Enhancement Only

```python
from app.services.voice import get_voice_enhancement

service = get_voice_enhancement()
enhanced_path = service.enhance_tts_output(
    tts_audio_path=Path("vocals.wav"),
    output_path=Path("vocals_enhanced.wav"),
    enable_enhancement=True
)
```

#### Mixing Enhancement Only

```python
from app.services.production import get_song_assembly
from app.core.music_config import MusicGenre

assembly = get_song_assembly()
mixed_path = assembly.assemble_song(
    vocals_path=Path("vocals.wav"),
    music_path=Path("music.wav"),
    output_path=Path("mixed.wav"),
    use_intelligent_mixing=True,
    genre=MusicGenre.POP
)
```

---

## Database Schema

### Mixing Configuration Table

```sql
CREATE TABLE mixing_configurations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    song_id UUID REFERENCES songs(id),
    config_type VARCHAR(50) NOT NULL,  -- 'manual', 'genre_preset', 'reference_match'
    genre VARCHAR(50),
    eq_settings JSON,
    compression_settings JSON,
    stereo_width_settings JSON,
    reverb_settings JSON,
    delay_settings JSON,
    sidechain_settings JSON,
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Reference Track Table

```sql
CREATE TABLE reference_tracks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    genre VARCHAR(50),
    audio_file_path VARCHAR(500) NOT NULL,
    frequency_analysis JSON,
    stereo_width_analysis JSON,
    eq_profile JSON,
    recommendations JSON[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Audio Feature Vector Table

```sql
CREATE TABLE audio_feature_vectors (
    id UUID PRIMARY KEY,
    audio_file_id UUID REFERENCES audio_files(id),
    reference_track_id UUID REFERENCES reference_tracks(id),
    chromadb_id VARCHAR(255) UNIQUE,
    vector_dimension INTEGER NOT NULL,
    feature_type VARCHAR(50) NOT NULL,  -- 'frequency', 'spectral', 'rhythm', 'full'
    tempo FLOAT,
    spectral_centroid FLOAT,
    mfcc_features FLOAT[],
    frequency_bands JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Mixing Feedback Table

```sql
CREATE TABLE mixing_feedback (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    song_id UUID REFERENCES songs(id),
    mixing_config_id UUID REFERENCES mixing_configurations(id),
    overall_mixing_rating INTEGER,  -- 1-5
    vocals_clarity_rating INTEGER,
    music_balance_rating INTEGER,
    stereo_width_rating INTEGER,
    eq_quality_rating INTEGER,
    reverb_quality_rating INTEGER,
    pesq_score FLOAT,
    stoi_score FLOAT,
    mos_score FLOAT,
    comment TEXT,
    is_liked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Memory System

### Configuration Storage

**Location**: `app/services/memory/config_storage.py`

Stores and retrieves mixing configurations with Redis caching:

```python
from app.services.memory import get_config_storage

storage = get_config_storage()

# Store configuration
config = await storage.create_configuration(db, config_data)

# Retrieve configuration
config = await storage.get_configuration(db, config_id)

# Get configurations by genre
configs = await storage.get_configurations_by_genre(db, "pop")
```

### Audio Feature Vectors

**Location**: `app/services/memory/audio_features.py`

Stores audio feature vectors in ChromaDB for similarity search:

```python
from app.services.memory import get_audio_feature_service

service = get_audio_feature_service()

# Extract and store features
feature_vector = await service.extract_and_store_features(
    db=db,
    audio_file_id=audio_id,
    audio_path=Path("audio.wav"),
    feature_type="full"
)

# Search similar audio
similar = await service.search_similar_audio(
    db=db,
    audio_path=Path("query.wav"),
    top_k=5
)
```

### Learning Mechanisms

**Location**: `app/services/memory/learning.py`

Services for feedback collection, quality tracking, and parameter optimization:

```python
from app.services.memory import get_feedback_collection, get_quality_tracking, get_feedback_loop

# Collect feedback
feedback_service = get_feedback_collection()
feedback = await feedback_service.collect_feedback(db, feedback_data)

# Track quality metrics
quality_service = get_quality_tracking()
history = await quality_service.track_quality_metrics(
    db=db,
    mixing_config_id=config_id,
    audio_path=Path("audio.wav")
)

# Process feedback and optimize
loop_service = get_feedback_loop()
result = await loop_service.process_feedback_and_optimize(
    db=db,
    feedback_obj_in=feedback_data,
    audio_path=Path("audio.wav")
)
```

---

## Performance Considerations

### Caching Strategy

- **Redis Cache**: Mixing configurations cached for 1 hour (configurable)
- **File Cache**: Enhanced audio files cached based on input hash
- **Vector Cache**: Audio feature vectors cached in ChromaDB

### Processing Time Estimates

- **Voice Enhancement**: ~30 seconds per minute of audio
- **Mixing Enhancement**: ~10 seconds per minute of audio
- **Complete Pipeline**: ~3 minutes for a 3-minute song

### Memory Usage

- **Voice Enhancement**: ~500MB peak memory increase
- **Mixing Enhancement**: ~200MB peak memory increase
- **Complete Pipeline**: ~2GB peak memory increase

### Optimization Tips

1. **Enable Caching**: Reduces processing time for repeated requests
2. **Parallel Processing**: Enable for batch operations (experimental)
3. **Selective Enhancement**: Only enable needed features
4. **Quality vs Speed**: Lower quality settings reduce processing time

---

## Troubleshooting

### Common Issues

#### 1. Neural Vocoder Not Available

**Error**: `Vocos neural vocoder not available`

**Solution**:

- Install Vocos: `pip install vocos`
- Check if model files are downloaded
- Fallback to audio processing will be used automatically

#### 2. CREPE Pitch Tracking Fails

**Error**: `CREPE pitch tracking failed`

**Solution**:

- Install CREPE: `pip install crepe`
- System will automatically fallback to librosa pitch tracking

#### 3. Circular Import Error

**Error**: `ImportError: cannot import name 'X' from partially initialized module`

**Solution**:

- Check for circular imports in service files
- Move imports inside functions where possible
- Use lazy imports for optional dependencies

#### 4. Memory System Not Learning

**Issue**: Configurations not being optimized

**Solution**:

- Ensure `enable_memory_learning=True` in config
- Check that feedback is being collected (minimum 3 feedback entries)
- Verify database connections (PostgreSQL, Redis, ChromaDB)

#### 5. Quality Metrics Calculation Fails

**Error**: `Quality metrics calculation failed`

**Solution**:

- Install required packages: `pip install pesq pystoi`
- Ensure audio files are valid WAV format
- Check sample rate compatibility (16kHz for PESQ/STOI)

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:

```bash
LOG_LEVEL=DEBUG
```

### Performance Debugging

Use the benchmark script:

```bash
python scripts/benchmark_performance.py voice audio.wav --iterations 5
python scripts/benchmark_performance.py mixing vocals.wav music.wav --iterations 5
```

### Quality Validation

Use the validation script:

```bash
python scripts/validate_quality_improvements.py voice original.wav enhanced.wav
python scripts/validate_quality_improvements.py mixing basic_mix.wav enhanced_mix.wav
```

---

## Additional Resources

- [Phase 1 Voice Enhancement](./PHASE1_VOICE_ENHANCEMENT.md)
- [Vocos Integration](./VOCOS_INTEGRATION.md)
- [Research Documentation](../research/AI_MUSIC_VOICE_ENHANCEMENT.md)
- [Testing Guide](../testing/UAT_GUIDE.md)
- [API Documentation](http://localhost:8000/docs)

---

**Last Updated**: 2025-12-05  
**Version**: 1.0.0
