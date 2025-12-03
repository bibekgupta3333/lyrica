# Voice Synthesis for Python 3.12

## Important: Python Version Compatibility

**The original TTS packages (Coqui TTS, Bark, Tortoise) only support Python
<=3.11.**

For Python 3.12, we've updated to use compatible alternatives.

## Python 3.12 Compatible Packages

### Installed in requirements.txt:

```
# Voice Synthesis & TTS (Python 3.12 compatible)
edge-tts>=6.1.0          # Microsoft Edge TTS (cloud-based)
pyttsx3>=2.90            # Offline TTS engine wrapper
gTTS>=2.5.0              # Google Text-to-Speech
torch>=2.2.0             # For VAD
torchaudio>=2.2.0        # For VAD
```

## Installation

### 1. Install System Dependencies (macOS)

```bash
# Install ffmpeg (required for audio processing)
brew install ffmpeg

# Optional: Install espeak-ng (for phonemizer, if needed later)
brew install espeak-ng
```

### 2. Install Python Packages

```bash
cd lyrica-backend

# Install requirements
pip install -r requirements.txt

# Install Silero VAD separately (after torch)
pip install git+https://github.com/snakers4/silero-vad.git
```

## Available TTS Engines (Python 3.12)

### 1. **Edge TTS** (Recommended - Default)

- ✅ Python 3.12 compatible
- ✅ Cloud-based (Microsoft)
- ✅ High quality neural voices
- ✅ Multiple languages
- ✅ Fast generation
- ❌ Requires internet connection

**Voice IDs:**

- `en-US-GuyNeural` - Male narrator
- `en-US-JennyNeural` - Female singer
- `en-US-ChristopherNeural` - Male singer
- `en-US-AriaNeural` - Soft narrator

### 2. **Google TTS (gTTS)**

- ✅ Python 3.12 compatible
- ✅ Cloud-based (Google)
- ✅ Simple and reliable
- ✅ Multiple languages
- ✅ Free
- ❌ Requires internet connection
- ❌ Lower quality than Edge TTS

### 3. **pyttsx3** (Offline)

- ✅ Python 3.12 compatible
- ✅ Works offline
- ✅ Uses system voices
- ✅ Fast
- ❌ Lower quality
- ❌ Limited voice options

### 4. **Silero VAD** (Voice Activity Detection)

- ✅ Python 3.12 compatible
- ✅ Real-time speech detection
- ✅ High accuracy
- ✅ GPU support

## Updated Voice Profiles

Default voice profiles now use Edge TTS:

```python
VOICE_PROFILES = [
    VoiceProfile(
        id="male_narrator_1",
        name="Male Narrator",
        engine=TTSEngine.EDGE,
        engine_voice_id="en-US-GuyNeural",
    ),
    VoiceProfile(
        id="female_singer_1",
        name="Female Singer",
        engine=TTSEngine.EDGE,
        engine_voice_id="en-US-JennyNeural",
    ),
    # ... more profiles
]
```

## API Usage Examples

### Synthesize Speech

```bash
curl -X POST "http://localhost:8000/api/v1/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Edge TTS!",
    "voice_profile_id": "male_narrator_1",
    "temperature": 0.7,
    "speed": 1.0
  }'
```

### Voice Activity Detection

```bash
curl -X POST "http://localhost:8000/api/v1/voice/voice-activity-detection" \
  -F "file=@audio.wav" \
  -F "threshold=0.5"
```

### List Available Voices

```bash
curl "http://localhost:8000/api/v1/voice/profiles?engine=edge"
```

## Code Examples

### Using Edge TTS

```python
from app.services.voice import get_voice_synthesis
from app.core.voice_config import get_voice_profile
from pathlib import Path

service = get_voice_synthesis()
profile = get_voice_profile('male_narrator_1')  # Uses Edge TTS
output = Path('output.wav')

service.synthesize_text(
    "Hello, world!",
    profile,
    output,
    speed=1.0
)
```

### Voice Activity Detection

```python
audio_path = Path("speech.wav")
segments = service.detect_voice_activity(audio_path, threshold=0.5)

for start, end in segments:
    print(f"Speech: {start:.2f}s - {end:.2f}s")
```

## Migration from Bark/Coqui TTS

### Option 1: Use Python 3.11 Environment (Recommended for Best Quality)

If you need Bark/Coqui TTS quality:

```bash
# Create Python 3.11 environment
pyenv install 3.11.9
pyenv local 3.11.9

# Or use conda
conda create -n lyrica-py311 python=3.11
conda activate lyrica-py311

# Install original TTS packages
pip install TTS>=0.22.0 bark>=0.1.5 tortoise-tts>=3.0.0
```

### Option 2: Use Docker with Python 3.11

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-py311.txt .
RUN pip install -r requirements-py311.txt

# Your app code
COPY . .
```

### Option 3: Use External TTS APIs

For production, consider:

- **ElevenLabs** - Best quality, paid
- **Azure Cognitive Services** - Enterprise-grade
- **AWS Polly** - Scalable, paid
- **OpenAI TTS** - GPT-quality voices

## Comparison: Python 3.11 vs 3.12 TTS

| Feature          | Python 3.11 (Bark/Coqui) | Python 3.12 (Edge TTS) |
| ---------------- | ------------------------ | ---------------------- |
| Quality          | ⭐⭐⭐⭐⭐               | ⭐⭐⭐⭐               |
| Speed            | ⭐⭐⭐                   | ⭐⭐⭐⭐⭐             |
| Offline          | ✅                       | ❌                     |
| GPU Support      | ✅                       | N/A (Cloud)            |
| Voice Cloning    | ✅                       | ❌                     |
| Setup Complexity | High                     | Low                    |
| Dependencies     | Heavy                    | Light                  |
| Cost             | Free (self-hosted)       | Free (limited)         |

## Troubleshooting

### Edge TTS Connection Issues

```bash
# Test Edge TTS directly
edge-tts --text "Hello" --voice en-US-GuyNeural --write-media test.mp3

# Check connectivity
curl -I https://speech.platform.bing.com
```

### pyttsx3 Not Working

```bash
# macOS - Install system TTS
# Already included in macOS

# Linux - Install espeak
sudo apt-get install espeak

# Windows - Install SAPI5 voices
# Built into Windows
```

### gTTS Rate Limiting

```bash
# gTTS may be rate-limited by Google
# Add delays between requests or switch to Edge TTS
```

### Silero VAD Installation

```bash
# If git install fails, try:
pip install silero-vad --no-build-isolation

# Or install torch first:
pip install torch torchaudio
pip install git+https://github.com/snakers4/silero-vad.git
```

## Performance Optimization

### Edge TTS

- ✅ Already optimized (cloud-based)
- ✅ No local GPU needed
- ✅ Scales automatically

### Local TTS (pyttsx3)

- Fast but lower quality
- Good for development/testing
- No internet required

### Voice Activity Detection

- Enable GPU for faster processing:
  ```python
  # In .env
  USE_GPU=true
  ```

## Testing

### Test Installation

```bash
python -c "
import edge_tts
print('✓ Edge TTS installed')

from gtts import gTTS
print('✓ Google TTS installed')

import pyttsx3
print('✓ pyttsx3 installed')

import torch
import torchaudio
print('✓ torch/torchaudio installed')
"
```

### Test Voice Synthesis

```bash
# Start server
uvicorn app.main:app --reload

# Test synthesis
curl -X POST http://localhost:8000/api/v1/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "voice_profile_id": "male_narrator_1"}'
```

## Next Steps

1. ✅ Install system dependencies (ffmpeg)
2. ✅ Install Python packages: `pip install -r requirements.txt`
3. ✅ Test Edge TTS: `edge-tts --list-voices | grep en-US`
4. ✅ Start using the updated voice synthesis service!

## Recommendations

### For Development (Python 3.12)

- Use **Edge TTS** - Best balance of quality and ease
- Use **pyttsx3** for offline testing
- Use **Silero VAD** for speech detection

### For Production

- Option 1: **Python 3.11 + Bark/Coqui** in Docker (best quality)
- Option 2: **Python 3.12 + Edge TTS** (easier deployment)
- Option 3: **External API** (ElevenLabs, Azure, AWS)

### For Best Quality

- Use Python 3.11 environment with Bark/Coqui TTS
- Or integrate with commercial TTS APIs

## Resources

- [Edge TTS Documentation](https://github.com/rany2/edge-tts)
- [gTTS Documentation](https://gtts.readthedocs.io/)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)
