# YuE Installation Guide

## Overview

YuE is an open-source full-song generation model that generates complete songs with vocals and music together, similar to commercial services like Suno.ai.

**Repository**: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation

**Key Features**:
- Full-song generation (vocals + music)
- Professional quality output
- Style transfer
- Voice cloning
- Lyric alignment
- Dual-track in-context learning

## Installation Steps

### Step 1: Clone YuE Repository

```bash
# Clone the repository
git clone https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation.git
cd YuE-Open-Full-song-Music-Generation
```

### Step 2: Check Requirements

```bash
# Check Python version (should work with Python 3.12)
python --version

# Check requirements.txt
cat requirements.txt
```

### Step 3: Install Dependencies

```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Or install in your virtual environment
source venv/bin/activate  # If using virtual environment
pip install -r requirements.txt
```

### Step 4: Download Model Weights

Follow the instructions in the YuE repository README to download model weights. This typically involves:

1. Downloading pre-trained model checkpoints
2. Placing them in the appropriate directory
3. Configuring model paths

### Step 5: Verify Installation

```bash
# Try importing YuE
python -c "from yue import YueModel; print('YuE installed successfully')"

# Or check if the module exists
python -c "import yue; print('YuE module found')"
```

## Integration with Lyrica

Once YuE is installed, the `YueGenerationService` will automatically detect it and use it for music generation.

### Check YuE Availability

```python
from app.services.music import get_yue_generation

yue_service = get_yue_generation()
if yue_service.is_available():
    print("YuE is available and ready to use")
else:
    print("YuE is not installed. See installation guide.")
```

### Using YuE for Full-Song Generation

```python
from app.services.music import get_yue_generation
from app.core.music_config import MusicGenre

yue_service = get_yue_generation()
if yue_service.is_available():
    song_path = yue_service.generate_full_song(
        lyrics="Verse 1...\nChorus...\nVerse 2...",
        genre=MusicGenre.POP,
        duration=180,  # 3 minutes
        style="professional"
    )
    print(f"Full song generated: {song_path}")
```

### Using YuE for Instrumental Music

```python
from app.services.music import get_yue_generation
from app.core.music_config import MusicGenre

yue_service = get_yue_generation()
if yue_service.is_available():
    music_path = yue_service.generate_music_only(
        prompt="upbeat pop music with piano and drums",
        genre=MusicGenre.POP,
        duration=180
    )
    print(f"Instrumental music generated: {music_path}")
```

## Automatic Integration

The `MusicGenerationService` automatically tries YuE first when generating music:

1. **Priority 1**: YuE (if available)
2. **Priority 2**: AudioCraft/MusicGen (if available)
3. **Fallback**: MIDI-based generation

This ensures the best possible quality while maintaining backward compatibility.

## Troubleshooting

### YuE Not Detected

If YuE is installed but not detected:

1. **Check Python Path**: Ensure YuE is installed in the same Python environment as Lyrica
2. **Check Import Path**: The import path may vary. Update `_check_yue_availability()` in `yue_generation.py` with the correct import path
3. **Check Model Weights**: Ensure model weights are downloaded and accessible

### Import Errors

If you get import errors:

```python
# Try different import paths
from yue import YueModel
# Or
from yue_model import YueModel
# Or
import yue
```

Update the import in `yue_generation.py` based on what works.

### Model Loading Errors

If model loading fails:

1. Check that model weights are in the correct location
2. Verify file permissions
3. Check available disk space
4. Review YuE repository documentation for model loading requirements

## Updating YuE Integration

Once YuE is installed and working, update the `YueGenerationService` methods:

1. **Update `_check_yue_availability()`**: Use the correct import path
2. **Update `_load_yue_model()`**: Use the actual YuE API for model loading
3. **Update `generate_full_song()`**: Use the actual YuE API for generation
4. **Update `generate_music_only()`**: Use the actual YuE API for instrumental generation

## Python 3.12 Compatibility

YuE should work with Python 3.12, but if you encounter compatibility issues:

1. Check the YuE repository for Python 3.12 compatibility notes
2. Consider using a Python 3.11 environment for YuE if needed
3. Use Docker with Python 3.11 if necessary

## Next Steps

After installing YuE:

1. Test generation quality locally
2. Compare YuE output with MIDI fallback
3. Validate full-song generation (vocals + music)
4. Test error handling and fallbacks
5. Benchmark generation time and resource usage

## References

- **YuE Repository**: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation
- **Lyrica YuE Service**: `app/services/music/yue_generation.py`
- **Music Generation Integration**: `app/services/music/generation.py`
