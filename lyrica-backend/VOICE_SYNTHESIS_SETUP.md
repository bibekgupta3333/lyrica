# Voice Synthesis Setup Guide

## Overview

Updated voice synthesis packages to latest versions with improved features and
performance.

## Updated Packages

### Requirements (requirements.txt)

```
# Voice Synthesis & TTS
TTS>=0.22.0                  # Coqui TTS with XTTS v2
bark>=0.1.5                  # Suno AI's Bark (latest)
phonemizer>=3.3.0            # Text-to-phoneme conversion
tortoise-tts>=3.0.0          # High-quality TTS
silero-vad>=5.1.0            # Voice Activity Detection
```

## Installation

### 1. System Dependencies (macOS)

```bash
# Install ffmpeg (required for audio processing)
brew install ffmpeg

# Install espeak-ng (required for phonemizer)
brew install espeak-ng
```

### 2. Python Packages

```bash
cd lyrica-backend

# Install updated requirements
pip install -r requirements.txt

# Or install voice synthesis packages individually:
pip install TTS>=0.22.0
pip install bark>=0.1.5
pip install phonemizer>=3.3.0
pip install tortoise-tts>=3.0.0
pip install silero-vad>=5.1.0
```

## New Features

### 1. **Bark TTS v0.1.5+**

- GPU acceleration support
- Improved voice quality
- Better prompt handling
- Audio normalization to prevent clipping

### 2. **Coqui TTS v0.22.0+ (XTTS v2)**

- Latest multilingual model
- Better sentence splitting for long text
- Improved voice cloning
- GPU support

### 3. **Tortoise TTS v3.0.0+**

- High-quality speech synthesis
- Voice cloning capabilities
- Multiple quality presets (ultra_fast, fast, standard, high_quality)
- FP16 optimization for GPU

### 4. **Silero VAD v5.1.0+**

- Voice Activity Detection
- Real-time speech detection
- Configurable thresholds
- Segment extraction

## Updated Code

### Service Layer (`app/services/voice/synthesis.py`)

- ✅ Added Tortoise TTS support
- ✅ Added Silero VAD integration
- ✅ GPU optimization for all models
- ✅ Improved error handling
- ✅ Audio normalization
- ✅ Better model loading with progress tracking

### API Layer (`app/api/v1/endpoints/voice.py`)

- ✅ New endpoint: `/voice/voice-activity-detection` - Detect speech segments
- ✅ Updated health endpoint with supported engines
- ✅ Enhanced error messages

### Configuration (`app/core/voice_config.py`)

- ✅ Tortoise TTS engine option
- ✅ GPU configuration
- ✅ VAD threshold settings

## API Endpoints

### Voice Activity Detection (NEW)

```bash
POST /api/v1/voice/voice-activity-detection
Content-Type: multipart/form-data

file: audio.wav
threshold: 0.5

Response:
{
  "segments": [
    {"start": 0.5, "end": 2.3},
    {"start": 3.1, "end": 5.7}
  ],
  "total_speech_duration": 4.4,
  "total_segments": 2
}
```

### Synthesize Speech

```bash
POST /api/v1/voice/synthesize
Content-Type: application/json

{
  "text": "Hello, world!",
  "voice_profile_id": "male_narrator_1",
  "temperature": 0.7,
  "speed": 1.0
}
```

### Get Voice Profiles

```bash
GET /api/v1/voice/profiles?engine=bark
```

## Testing

### 1. Test Package Installation

```bash
python -c "
from TTS.api import TTS
print('✓ Coqui TTS installed')

from bark import generate_audio
print('✓ Bark installed')

from phonemizer import phonemize
print('✓ Phonemizer installed')

from tortoise.api import TextToSpeech
print('✓ Tortoise TTS installed')

from silero_vad import load_silero_vad
print('✓ Silero VAD installed')
"
```

### 2. Test Voice Synthesis Service

```bash
python -c "
from app.services.voice import get_voice_synthesis
from app.core.voice_config import get_voice_profile
from pathlib import Path

service = get_voice_synthesis()
profile = get_voice_profile('male_narrator_1')
output = Path('test_voice.wav')

service.synthesize_text('Hello, this is a test!', profile, output)
print(f'✓ Generated: {output}')
"
```

### 3. Test API Endpoint

```bash
# Start server
uvicorn app.main:app --reload

# Test synthesis endpoint
curl -X POST "http://localhost:8000/api/v1/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Testing voice synthesis",
    "voice_profile_id": "male_narrator_1",
    "temperature": 0.7,
    "speed": 1.0
  }'
```

## GPU Configuration

Enable GPU acceleration in `.env`:

```bash
# Voice synthesis GPU settings
USE_GPU=true  # Enable GPU for TTS models
```

Or in code:

```python
# app/core/voice_config.py
voice_config = VoiceConfig(use_gpu=True)
```

## Voice Engines Comparison

| Engine              | Quality   | Speed     | GPU Support | Best For                    |
| ------------------- | --------- | --------- | ----------- | --------------------------- |
| **Bark**            | High      | Medium    | ✅          | Natural speech, emotions    |
| **Coqui (XTTS v2)** | High      | Fast      | ✅          | Multilingual, voice cloning |
| **Tortoise**        | Very High | Slow      | ✅          | High-quality narration      |
| **Edge TTS**        | Medium    | Very Fast | ❌          | Quick prototyping           |

## Troubleshooting

### Issue: FFmpeg not found

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

### Issue: espeak-ng not found

```bash
# macOS
brew install espeak-ng

# Linux
sudo apt-get install espeak-ng

# Windows
# Download from: https://github.com/espeak-ng/espeak-ng/releases
```

### Issue: CUDA out of memory

```bash
# Disable GPU or use smaller batch sizes
export USE_GPU=false
```

### Issue: Model download fails

```bash
# Models are downloaded automatically on first use
# Ensure stable internet connection
# Models are cached in ~/.cache/torch/
```

## Performance Tips

1. **Use GPU for faster synthesis**
   - Bark: 2-5x faster
   - Coqui: 3-10x faster
   - Tortoise: 5-20x faster

2. **Cache models**
   - Models are loaded once and reused
   - First synthesis will be slower

3. **Chunk long text**
   - Use `synthesize_lyrics()` for long text
   - Automatic sentence splitting

4. **Choose right engine**
   - Fast: Coqui or Edge TTS
   - Quality: Tortoise
   - Balanced: Bark

## Migration from Old Version

If you had old versions commented out:

```diff
- # TTS>=0.22.0
- # bark>=0.1.5
+ TTS>=0.22.0
+ bark>=0.1.5
```

No code changes needed - the service automatically detects and uses the latest
APIs!

## Next Steps

1. Install system dependencies (ffmpeg, espeak-ng)
2. Install Python packages: `pip install -r requirements.txt`
3. Test installation with the test commands above
4. Configure GPU if available
5. Start using the updated voice synthesis service!

## Resources

- [Bark Documentation](https://github.com/suno-ai/bark)
- [Coqui TTS Documentation](https://docs.coqui.ai/)
- [Tortoise TTS Documentation](https://github.com/neonbjb/tortoise-tts)
- [Silero VAD Documentation](https://github.com/snakers4/silero-vad)
