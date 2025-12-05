# Vocos Neural Vocoder Integration

## Overview

Vocos is a modern, Python 3.12-compatible neural vocoder that has been integrated as an alternative to `parallel-wavegan` (HiFi-GAN), which has Python 3.12 compatibility issues.

## Status

✅ **Fully Integrated and Working**

- Vocos v0.1.0 installed and functional
- Python 3.12 compatible
- Integrated into voice enhancement pipeline
- Automatic fallback to audio processing if Vocos unavailable

## Installation

Vocos is included in `requirements.txt`:

```bash
pip install vocos>=0.1.0
```

Or install manually:

```bash
pip install vocos
```

## Features

### Neural Vocoder Support

- **Vocos** (Primary, Python 3.12 compatible)
  - High-quality neural vocoder
  - Uses pretrained models from Hugging Face
  - Converts mel-spectrograms to high-quality audio
  - Supports 24kHz output sample rate

- **parallel-wavegan** (Legacy, fallback)
  - HiFi-GAN implementation
  - May have Python 3.12 compatibility issues
  - Used if Vocos is not available

- **Audio Processing** (Always available)
  - Noise reduction
  - EQ enhancement
  - Compression
  - Normalization

## Usage

The enhancement service automatically detects and uses Vocos when available:

```python
from app.services.voice import get_voice_synthesis, get_voice_enhancement
from app.core.voice_config import get_voice_profile

# Initialize services
voice_service = get_voice_synthesis()
enhancement_service = get_voice_enhancement()

# Check vocoder availability
print(f"Neural vocoder available: {enhancement_service.is_enhancement_available()}")
print(f"Vocoder type: {enhancement_service._vocoder_type}")

# Synthesize with automatic enhancement
profile = get_voice_profile("female_singer_1")
audio_path = voice_service.synthesize_text(
    text="Hello, this is enhanced voice synthesis.",
    voice_profile=profile,
    output_path=Path("output.wav"),
    enable_enhancement=True  # Uses Vocos if available
)

# Or enhance existing audio directly
enhanced_path = enhancement_service.enhance_audio(
    audio_path=Path("input.wav"),
    output_path=Path("enhanced.wav"),
    method="auto",  # Automatically uses Vocos if available
    quality="high"
)
```

## Technical Details

### Mel-Spectrogram Configuration

Vocos requires specific mel-spectrogram parameters:

- **Mel bins**: 100 (vs 80 for HiFi-GAN)
- **Sample rate**: 24kHz output (vs 22kHz for HiFi-GAN)
- **Hop length**: 256
- **Window length**: 1024
- **Frequency range**: 0-12kHz (vs 0-8kHz for HiFi-GAN)

The service automatically adjusts mel-spectrogram parameters based on the vocoder type.

### Model Loading

Vocos uses pretrained models from Hugging Face:

1. **Primary**: `charactr/vocos-mel-24khz`
2. **Fallback**: `facebook/tts_hifigan`
3. **Default**: Vocos without pretrained weights (if models unavailable)

Models are downloaded automatically on first use.

## Performance

- **Quality**: High-quality neural vocoder output
- **Speed**: Fast inference (GPU accelerated if available)
- **Memory**: Moderate memory usage
- **Compatibility**: Python 3.12+ fully supported

## Comparison

| Feature | Vocos | parallel-wavegan | Audio Processing |
|---------|-------|------------------|------------------|
| Python 3.12 | ✅ Yes | ❌ No | ✅ Yes |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Speed | Fast | Fast | Very Fast |
| GPU Support | ✅ Yes | ✅ Yes | ❌ No |
| Pretrained Models | ✅ Yes | ⚠️ Manual | N/A |

## Troubleshooting

### Vocos Not Available

If Vocos is not detected:

1. Check installation: `pip show vocos`
2. Verify Python version: `python --version` (should be 3.12+)
3. Check logs for import errors

### Model Loading Issues

If model loading fails:

1. Check internet connection (models download from Hugging Face)
2. Verify Hugging Face Hub access
3. Check disk space for model cache
4. Service will fallback to audio processing automatically

### Quality Issues

If output quality is poor:

1. Ensure input audio is clean
2. Check sample rate compatibility
3. Try different quality presets
4. Verify mel-spectrogram parameters

## Future Enhancements

- Support for additional Vocos model variants
- Custom model training integration
- Real-time streaming support
- Multi-GPU acceleration

## References

- [Vocos GitHub](https://github.com/charactr-platform/vocos)
- [Vocos Paper](https://arxiv.org/abs/2306.00814)
- [Hugging Face Models](https://huggingface.co/models?search=vocos)
