# AI Music & Voice Enhancement - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Voice Enhancement](#voice-enhancement)
4. [Mixing Enhancement](#mixing-enhancement)
5. [Complete Song Enhancement](#complete-song-enhancement)
6. [Best Practices](#best-practices)
7. [Examples](#examples)
8. [FAQ](#faq)

---

## Introduction

The AI Music & Voice Enhancement system transforms your songs into professional-quality productions. Whether you're working with basic TTS voices or need intelligent mixing, our AI-powered system learns from your preferences and continuously improves.

### What You Can Do

- **Transform Basic Voices**: Convert robotic TTS output into natural, professional vocals
- **Intelligent Mixing**: Automatically balance vocals and music with AI-driven mixing
- **Genre-Specific Processing**: Get mixing presets tailored to your music genre
- **Continuous Learning**: The system learns from your feedback and improves over time

### Key Features

- 🎤 **Neural Vocoder Enhancement**: High-quality voice synthesis using AI
- 🎵 **Prosody Enhancement**: Natural rhythm, stress, and intonation
- 🎹 **Auto-Tune**: Pitch correction to any musical key
- 🎚️ **Dynamic EQ**: Intelligent frequency balancing
- 🔊 **Sidechain Compression**: Music automatically ducks for vocals
- 🎧 **Stereo Imaging**: Professional stereo width and spatial effects
- 🎯 **Genre-Specific Mixing**: Presets optimized for Pop, Rock, Hip-Hop, Jazz, and more
- 🧠 **Memory Learning**: System learns from your feedback and improves

---

## Getting Started

### Prerequisites

- Valid API access token (JWT)
- Audio files in WAV format (recommended)
- Song ID (for complete enhancement)

### Authentication

All API requests require authentication. Include your JWT token in the Authorization header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### Base URL

```
http://localhost:8000/api/v1/enhancement
```

### Quick Example

Enhance voice audio:

```bash
curl -X POST "http://localhost:8000/api/v1/enhancement/voice" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_path": "audio_files/songs/song_123/vocals.wav",
    "enable_neural_vocoder": true,
    "enable_prosody": true
  }'
```

---

## Voice Enhancement

### Overview

Voice enhancement transforms basic TTS output into professional-quality vocals using neural vocoders, prosody enhancement, and auto-tune.

### Endpoint

**POST** `/enhancement/voice`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio_path` | string | Yes | - | Path to the voice audio file |
| `enable_neural_vocoder` | boolean | No | `true` | Use neural vocoder for enhancement |
| `enable_prosody` | boolean | No | `true` | Apply prosody enhancement |
| `enable_auto_tune` | boolean | No | `false` | Apply auto-tune |
| `target_key` | string | No | - | Target musical key (e.g., "C major") |

### Example Requests

#### Basic Enhancement

```json
{
  "audio_path": "audio_files/songs/song_123/vocals.wav",
  "enable_neural_vocoder": true,
  "enable_prosody": true,
  "enable_auto_tune": false
}
```

#### With Auto-Tune

```json
{
  "audio_path": "audio_files/songs/song_123/vocals.wav",
  "enable_neural_vocoder": true,
  "enable_prosody": true,
  "enable_auto_tune": true,
  "target_key": "C major"
}
```

#### Neural Vocoder Only

```json
{
  "audio_path": "audio_files/songs/song_123/vocals.wav",
  "enable_neural_vocoder": true,
  "enable_prosody": false,
  "enable_auto_tune": false
}
```

### Response

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

### Quality Metrics Explained

- **PESQ** (Perceptual Evaluation of Speech Quality): 1.0-4.5 scale, higher is better
- **STOI** (Short-Time Objective Intelligibility): 0.0-1.0 scale, higher is better
- **MOS** (Mean Opinion Score): 1.0-5.0 scale, higher is better
- **Overall**: Weighted average of all metrics

### Tips

- Use WAV format for best quality
- Enable neural vocoder for maximum quality improvement
- Use auto-tune only when pitch correction is needed
- Check quality metrics to assess improvement

---

## Mixing Enhancement

### Overview

Mixing enhancement applies intelligent frequency balancing, sidechain compression, and stereo imaging to create professional-quality mixes.

### Endpoint

**POST** `/enhancement/mixing`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `vocals_path` | string | Yes | - | Path to vocals audio file |
| `music_path` | string | Yes | - | Path to music audio file |
| `genre` | string | Yes | - | Music genre (pop, rock, hiphop, jazz, etc.) |
| `enable_frequency_balancing` | boolean | No | `true` | Apply dynamic EQ |
| `enable_sidechain` | boolean | No | `true` | Apply sidechain compression |
| `enable_stereo_imaging` | boolean | No | `true` | Apply stereo imaging |
| `mixing_config_id` | UUID | No | - | Use specific mixing configuration |

### Example Requests

#### Pop Song Mixing

```json
{
  "vocals_path": "audio_files/songs/song_123/vocals.wav",
  "music_path": "audio_files/songs/song_123/music.wav",
  "genre": "pop",
  "enable_frequency_balancing": true,
  "enable_sidechain": true,
  "enable_stereo_imaging": true
}
```

#### Rock Song Mixing

```json
{
  "vocals_path": "audio_files/songs/song_456/vocals.wav",
  "music_path": "audio_files/songs/song_456/music.wav",
  "genre": "rock",
  "enable_frequency_balancing": true,
  "enable_sidechain": true,
  "enable_stereo_imaging": true
}
```

#### Minimal Mixing

```json
{
  "vocals_path": "audio_files/songs/song_789/vocals.wav",
  "music_path": "audio_files/songs/song_789/music.wav",
  "genre": "pop",
  "enable_frequency_balancing": true,
  "enable_sidechain": false,
  "enable_stereo_imaging": false
}
```

### Response

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

### Supported Genres

- `pop` - Pop music
- `rock` - Rock music
- `hiphop` - Hip-hop
- `jazz` - Jazz
- `electronic` - Electronic music
- `country` - Country music
- `classical` - Classical music
- `rnb` - R&B

### Tips

- Specify the correct genre for best results
- Enable all features for maximum quality
- Use mixing_config_id to reuse successful configurations
- Check quality metrics to compare before/after

---

## Complete Song Enhancement

### Overview

Complete song enhancement applies the full pipeline to an existing song, including voice enhancement, mixing enhancement, and quality tracking.

### Endpoint

**POST** `/enhancement/complete`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `song_id` | UUID | Yes | - | ID of the song to enhance |
| `enhancement_config` | object | No | Defaults | Enhancement configuration |

### Enhancement Config Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_voice_enhancement` | boolean | `true` | Enable voice enhancement |
| `enable_prosody_enhancement` | boolean | `true` | Enable prosody enhancement |
| `enable_auto_tune` | boolean | `false` | Enable auto-tune |
| `target_key` | string | - | Target musical key |
| `enable_intelligent_mixing` | boolean | `true` | Enable intelligent mixing |
| `enable_stereo_imaging` | boolean | `true` | Enable stereo imaging |
| `enable_genre_specific_mixing` | boolean | `true` | Enable genre-specific mixing |
| `use_reference_track` | boolean | `false` | Use reference track matching |
| `reference_track_id` | UUID | - | Reference track ID |
| `enable_memory_learning` | boolean | `true` | Enable memory-based learning |
| `track_quality_metrics` | boolean | `true` | Track quality metrics |

### Example Requests

#### Full Enhancement

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

#### Voice Enhancement Only

```json
{
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhancement_config": {
    "enable_voice_enhancement": true,
    "enable_prosody_enhancement": true,
    "enable_auto_tune": true,
    "target_key": "C major",
    "enable_intelligent_mixing": false,
    "enable_stereo_imaging": false,
    "enable_genre_specific_mixing": false
  }
}
```

#### With Reference Track

```json
{
  "song_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhancement_config": {
    "enable_voice_enhancement": true,
    "enable_intelligent_mixing": true,
    "use_reference_track": true,
    "reference_track_id": "660e8400-e29b-41d4-a716-446655440001",
    "enable_memory_learning": true
  }
}
```

### Response

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

### Tips

- Use complete enhancement for best results
- Enable memory learning for continuous improvement
- Use reference tracks to match specific styles
- Track quality metrics to monitor improvements

---

## Best Practices

### Audio File Preparation

1. **Format**: Use WAV format (16-bit or 24-bit, 44.1kHz or 48kHz)
2. **Quality**: Start with high-quality source audio
3. **Normalization**: Ensure audio is not clipped or distorted
4. **Length**: Process songs in reasonable chunks (under 5 minutes recommended)

### Voice Enhancement

1. **Start with Neural Vocoder**: Always enable neural vocoder for best results
2. **Use Prosody Enhancement**: Improves naturalness significantly
3. **Auto-Tune Sparingly**: Only use when pitch correction is needed
4. **Check Quality Metrics**: Monitor PESQ, STOI, and MOS scores

### Mixing Enhancement

1. **Specify Genre Correctly**: Genre-specific presets improve quality
2. **Enable All Features**: For maximum quality, enable all mixing features
3. **Use Reference Tracks**: Match professional reference tracks for best results
4. **Save Successful Configs**: Reuse mixing configurations that work well

### Memory Learning

1. **Provide Feedback**: Rate your mixes to help the system learn
2. **Be Consistent**: Consistent feedback helps the system learn faster
3. **Wait for Learning**: System needs at least 3 feedback entries to optimize
4. **Check Improvements**: Monitor quality metrics over time

### Performance

1. **Enable Caching**: Reduces processing time for repeated requests
2. **Batch Processing**: Process multiple songs together when possible
3. **Selective Enhancement**: Only enable features you need
4. **Monitor Processing Time**: Check response times and optimize accordingly

---

## Examples

### Example 1: Enhance a Pop Song

```bash
curl -X POST "http://localhost:8000/api/v1/enhancement/complete" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "song_id": "550e8400-e29b-41d4-a716-446655440000",
    "enhancement_config": {
      "enable_voice_enhancement": true,
      "enable_prosody_enhancement": true,
      "enable_intelligent_mixing": true,
      "enable_genre_specific_mixing": true,
      "enable_memory_learning": true
    }
  }'
```

### Example 2: Enhance Voice Only

```bash
curl -X POST "http://localhost:8000/api/v1/enhancement/voice" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_path": "audio_files/songs/song_123/vocals.wav",
    "enable_neural_vocoder": true,
    "enable_prosody": true,
    "enable_auto_tune": true,
    "target_key": "C major"
  }'
```

### Example 3: Mix Vocals and Music

```bash
curl -X POST "http://localhost:8000/api/v1/enhancement/mixing" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vocals_path": "audio_files/songs/song_123/vocals.wav",
    "music_path": "audio_files/songs/song_123/music.wav",
    "genre": "pop",
    "enable_frequency_balancing": true,
    "enable_sidechain": true,
    "enable_stereo_imaging": true
  }'
```

### Example 4: Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/enhancement"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Enhance voice
response = requests.post(
    f"{BASE_URL}/voice",
    headers=headers,
    json={
        "audio_path": "audio_files/songs/song_123/vocals.wav",
        "enable_neural_vocoder": True,
        "enable_prosody": True
    }
)

result = response.json()
print(f"Enhanced audio: {result['enhanced_audio_path']}")
print(f"Quality score: {result['quality_metrics']['overall']}")
```

---

## FAQ

### General Questions

**Q: What audio formats are supported?**  
A: WAV format is recommended for best quality. MP3 and other formats may work but quality may be reduced.

**Q: How long does enhancement take?**  
A: Voice enhancement takes ~30 seconds per minute of audio. Mixing takes ~10 seconds per minute. Complete enhancement takes ~3 minutes for a 3-minute song.

**Q: Can I enhance multiple songs at once?**  
A: Currently, each request processes one song. You can make multiple requests in parallel.

**Q: What happens if enhancement fails?**  
A: The system will attempt fallback methods. If all fail, an error will be returned with details.

### Voice Enhancement

**Q: What is a neural vocoder?**  
A: A neural vocoder is an AI model that converts voice features into high-quality audio waveforms, making voices sound more natural.

**Q: Should I always enable neural vocoder?**  
A: Yes, for best quality. The system will automatically fallback if the vocoder is unavailable.

**Q: What is prosody enhancement?**  
A: Prosody enhancement improves rhythm, stress, and intonation to make speech sound more natural.

**Q: When should I use auto-tune?**  
A: Use auto-tune when you need to correct pitch to a specific musical key. It's not needed for all songs.

### Mixing Enhancement

**Q: What is dynamic EQ?**  
A: Dynamic EQ automatically adjusts frequency balance based on the audio content, preventing frequency conflicts between vocals and music.

**Q: What is sidechain compression?**  
A: Sidechain compression makes the music volume automatically decrease when vocals are present, ensuring vocals remain clear.

**Q: What is stereo imaging?**  
A: Stereo imaging enhances the stereo width and adds spatial effects (reverb, delay) to create a more immersive sound.

**Q: How do genre-specific presets work?**  
A: The system uses pre-configured mixing settings optimized for each genre, ensuring professional-quality mixes.

### Memory Learning

**Q: How does the memory system learn?**  
A: The system collects feedback on mixing quality and optimizes configurations based on successful patterns.

**Q: How much feedback is needed?**  
A: At least 3 feedback entries are needed before the system starts optimizing configurations.

**Q: Can I disable memory learning?**  
A: Yes, set `enable_memory_learning: false` in your enhancement config.

**Q: How do I provide feedback?**  
A: Feedback is collected automatically through quality metrics. You can also provide explicit ratings through the feedback API.

### Quality Metrics

**Q: What do the quality metrics mean?**  
A: PESQ measures speech quality, STOI measures intelligibility, MOS estimates overall quality. Higher scores are better.

**Q: What is a good quality score?**  
A: PESQ > 3.0, STOI > 0.8, MOS > 4.0 are considered good quality.

**Q: How can I improve quality scores?**  
A: Enable all enhancement features, use high-quality source audio, and specify the correct genre.

### Troubleshooting

**Q: Enhancement is taking too long**  
A: Check your audio file size and length. Very long files take more time. Consider processing in chunks.

**Q: Quality metrics are low**  
A: Ensure you're using high-quality source audio and enabling all relevant enhancement features.

**Q: I'm getting errors**  
A: Check that your audio files exist and are valid. Ensure you have proper authentication. Check the error message for details.

**Q: Enhancement doesn't sound better**  
A: Try enabling different features. Check quality metrics to see if there's improvement. Some audio may already be high quality.

---

## Support

For technical support or questions:

- Check the [Technical Documentation](../implementation/ENHANCEMENT_TECHNICAL_DOCS.md)
- Review the [API Documentation](http://localhost:8000/docs)
- Check logs for detailed error messages
- Contact support with your request ID and error details

---

**Last Updated**: 2025-12-05  
**Version**: 1.0.0
