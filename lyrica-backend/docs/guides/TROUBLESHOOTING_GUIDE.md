# Troubleshooting Guide

## Common Issues and Solutions

### Audio Quality Issues

#### 1. Vocals Sound Over-Processed

**Symptoms**: Vocals sound robotic, unnatural, or too "perfect"

**Solutions**:
- Reduce auto-tune strength (try 0.5-0.7 instead of 0.8-1.0)
- Disable vocal doubling or reduce delay/detune
- Use less aggressive compression
- Check if enhancement is being applied multiple times

**Code Fix**:
```python
# Reduce auto-tune strength
prosody_service.auto_tune_with_scale(
    audio_path=vocals_path,
    strength=0.6  # Reduced from 0.8
)
```

#### 2. Vocals Too Quiet

**Symptoms**: Vocals are barely audible in the mix

**Solutions**:
- Check vocal normalization level (should be -12dBFS)
- Increase vocals volume in mixing (try +2dB to +4dB)
- Reduce music volume (try -6dB to -8dB)
- Check sidechain compression settings

**Code Fix**:
```python
# Increase vocals volume
assembly_service.assemble_song(
    vocals_path=vocals_path,
    music_path=music_path,
    vocals_volume_db=2.0,  # Increased from 0.0
    music_volume_db=-6.0
)
```

#### 3. Music Sounds Muddy

**Symptoms**: Low frequencies are overwhelming, unclear sound

**Solutions**:
- Apply high-pass filter to remove sub-bass (< 40Hz)
- Use multi-band compression on low frequencies
- Reduce bass boost in EQ
- Check frequency balance

**Code Fix**:
```python
# Apply high-pass filter
from app.services.voice.effects import get_vocal_effects
effects = get_vocal_effects()
filtered = effects.apply_eq(
    audio_path=music_path,
    low_shelf_db=-3.0,  # Reduce low frequencies
    mid_db=0.0,
    high_shelf_db=0.0
)
```

#### 4. Clipping or Distortion

**Symptoms**: Audio sounds distorted, especially at loud parts

**Solutions**:
- Reduce input levels before processing
- Increase headroom (use -6dB reduction before mixing)
- Check peak limiting in mastering
- Ensure proper normalization

**Code Fix**:
```python
# Add headroom before mixing
from pydub import AudioSegment
vocals = AudioSegment.from_file(str(vocals_path))
vocals = vocals - 6  # Reduce by 6dB for headroom
music = AudioSegment.from_file(str(music_path))
music = music - 6  # Reduce by 6dB for headroom
```

#### 5. Stereo Issues

**Symptoms**: Audio sounds mono, no width, or phase issues

**Solutions**:
- Check if audio is mono (convert to stereo if needed)
- Apply stereo enhancement in mastering
- Verify stereo imaging settings
- Check for phase cancellation

**Code Fix**:
```python
# Enhance stereo width
from app.services.audio.mastering import AudioMasteringService
mastering = AudioMasteringService()
widened = mastering.enhance_stereo_width(
    audio_path=song_path,
    width_factor=1.2  # Increase width
)
```

---

### Performance Issues

#### 1. Slow Generation

**Symptoms**: Song generation takes too long

**Solutions**:
- Use GPU acceleration if available
- Reduce processing quality settings
- Disable unnecessary enhancements
- Use caching for repeated operations

**Optimization**:
```python
# Disable unnecessary processing
effects_service.apply_professional_vocal_chain(
    audio_path=vocals_path,
    enable_auto_tune=True,
    enable_timing=False,  # Disable if not needed
    enable_doubling=False,  # Disable if not needed
    enable_harmony=False,
    enable_ad_libs=False
)
```

#### 2. High Memory Usage

**Symptoms**: System runs out of memory during processing

**Solutions**:
- Process audio in chunks
- Reduce sample rate for intermediate processing
- Clear temporary files
- Use streaming processing

**Code Fix**:
```python
# Process in chunks
import librosa
y, sr = librosa.load(audio_path, sr=22050)  # Lower sample rate
chunk_size = sr * 10  # 10 second chunks
for i in range(0, len(y), chunk_size):
    chunk = y[i:i+chunk_size]
    # Process chunk
```

#### 3. YuE Generation Fails

**Symptoms**: YuE service not available or generation fails

**Solutions**:
- Check YuE installation (see YUE_INSTALLATION.md)
- Verify model weights are downloaded
- Check Python compatibility
- Use fallback to MusicGen or MIDI

**Troubleshooting**:
```python
from app.services.music import get_yue_generation
yue_service = get_yue_generation()
if not yue_service.is_available():
    print("YuE not available, using fallback")
    # Fallback to MusicGen or MIDI
```

---

### Integration Issues

#### 1. Import Errors

**Symptoms**: `ImportError` or `ModuleNotFoundError`

**Solutions**:
- Check all dependencies are installed
- Verify virtual environment is activated
- Check Python version compatibility
- Reinstall dependencies

**Fix**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.12+
```

#### 2. Circular Import Errors

**Symptoms**: `ImportError: cannot import name ... from partially initialized module`

**Solutions**:
- Check import order
- Use local imports inside functions
- Refactor to break circular dependencies

**Fix**:
```python
# Instead of top-level import
# from app.services.memory import get_feedback_loop

# Use local import
def my_function():
    from app.services.memory import get_feedback_loop
    feedback_loop = get_feedback_loop()
```

#### 3. Service Not Found

**Symptoms**: Service instance is None or not initialized

**Solutions**:
- Use getter functions instead of direct instantiation
- Check service initialization
- Verify service is exported in __init__.py

**Fix**:
```python
# Correct way
from app.services.voice import get_vocal_effects
effects = get_vocal_effects()

# Wrong way
from app.services.voice.effects import VocalEffectsService
effects = VocalEffectsService()  # May not be singleton
```

---

### File System Issues

#### 1. "Directory not empty" Error

**Symptoms**: `[Errno 66] Directory not empty`

**Solutions**:
- Use `shutil.rmtree()` instead of `rmdir()`
- Add `ignore_errors=True` for cleanup
- Check file permissions

**Fix**:
```python
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)
```

#### 2. "No such file or directory" Error

**Symptoms**: `[Errno 2] No such file or directory`

**Solutions**:
- Check file exists before accessing
- Ensure parent directories exist
- Copy files to permanent locations before cleanup

**Fix**:
```python
# Check before accessing
if file_path.exists():
    # Process file
else:
    logger.warning(f"File not found: {file_path}")

# Ensure parent exists
output_path.parent.mkdir(parents=True, exist_ok=True)
```

#### 3. Permission Errors

**Symptoms**: Permission denied when writing files

**Solutions**:
- Check file permissions
- Ensure directory is writable
- Use appropriate file paths

**Fix**:
```python
# Check permissions
import os
if os.access(output_dir, os.W_OK):
    # Write file
else:
    logger.error(f"Directory not writable: {output_dir}")
```

---

### Quality Metrics Issues

#### 1. PESQ/STOI Not Available

**Symptoms**: Quality metrics return None or fallback values

**Solutions**:
- Install required packages: `pip install pesq pystoi`
- Check Python version compatibility
- Use alternative metrics

**Fix**:
```bash
pip install pesq pystoi
```

#### 2. Metrics Calculation Fails

**Symptoms**: Error during quality metric calculation

**Solutions**:
- Check audio file format (must be WAV)
- Verify sample rate (PESQ requires 8000 or 16000 Hz)
- Ensure audio files are valid

**Fix**:
```python
# Resample for PESQ
import librosa
y, sr = librosa.load(audio_path, sr=16000)  # PESQ requires 16kHz
```

---

## Getting Help

### Logs

Check application logs for detailed error messages:
```bash
tail -f logs/app.log
```

### Debug Mode

Enable debug logging:
```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### Common Error Codes

- `ImportError`: Missing dependency or circular import
- `FileNotFoundError`: File path issue
- `PermissionError`: File system permissions
- `MemoryError`: Out of memory
- `ValueError`: Invalid parameter value

---

## Prevention

### Best Practices

1. **Always check file existence** before processing
2. **Use proper error handling** with try-except blocks
3. **Validate inputs** before processing
4. **Clean up temporary files** after processing
5. **Use logging** for debugging
6. **Test with small files** first
7. **Monitor memory usage** during processing

### Code Patterns

```python
# Good: Check before processing
if audio_path.exists():
    process_audio(audio_path)
else:
    logger.error(f"Audio not found: {audio_path}")

# Good: Error handling
try:
    result = process_audio(audio_path)
except Exception as e:
    logger.error(f"Processing failed: {e}")
    # Fallback or re-raise

# Good: Cleanup
try:
    # Process
    result = process_audio(audio_path)
finally:
    # Cleanup
    cleanup_temp_files()
```

---

## Additional Resources

- [Professional Processing Guide](./PROFESSIONAL_PROCESSING_GUIDE.md)
- [YuE Installation Guide](./YUE_INSTALLATION.md)
- [API Documentation](../../app/api/v1/endpoints/enhancement.py)
- [Technical Documentation](../implementation/ENHANCEMENT_TECHNICAL_DOCS.md)
