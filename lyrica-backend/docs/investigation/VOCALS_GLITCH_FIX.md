# Vocals Glitch Sound - Root Cause & Fix

## Problem Description

Vocals generated using Edge TTS (`female_singer_1`) sound like "glitch" - not clear female voice, just corrupted/static-like sound.

## Root Cause Analysis

### Issue 1: Aggressive Noise Reduction ⚠️ **CRITICAL**

**Problem:**
- Noise reduction uses spectral gating with threshold = noise_floor * 1.5
- This is TOO AGGRESSIVE for TTS output
- Edge TTS produces clean audio, but noise reduction removes voice content
- Results in "glitch" sound with missing voice frequencies

**Root Cause:**
- TTS engines (especially Edge TTS) produce high-quality, clean audio
- Noise reduction assumes noisy input and removes frequencies
- Voice content gets removed along with noise
- Creates artifacts and "glitch" sounds

**Fix Applied:**
```python
# OLD (WRONG - too aggressive):
threshold = noise_floor * 1.5
mask = magnitude > threshold  # Hard gate - removes too much
magnitude_clean = magnitude * mask

# NEW (CORRECT - conservative for TTS):
# Check if audio is already clean
if rms > max_val * 0.1:  # Good signal quality
    # Use soft gate with higher threshold
    threshold = noise_floor * 3.0  # Much higher threshold
    mask = np.maximum(0, 1 - (threshold / (magnitude + 1e-10)))
    magnitude_clean = magnitude * np.maximum(mask, 0.3)  # Keep 30% minimum
```

---

### Issue 2: Aggressive EQ Enhancement ⚠️ **HIGH PRIORITY**

**Problem:**
- EQ uses 4th-order high-pass filter at 80Hz
- Parametric boost at 2kHz with 0.3 gain
- Can introduce phase artifacts and distortion
- Too aggressive for clean TTS output

**Root Cause:**
- TTS audio is already well-EQ'd
- Additional EQ processing introduces artifacts
- Phase issues from high-order filters

**Fix Applied:**
```python
# OLD (WRONG - too aggressive):
sos_hp = signal.butter(4, 80, "hp", fs=sr)  # 4th order, 80Hz
b, a = signal.iirpeak(2000, Q=2, fs=sr)
audio = signal.filtfilt(b, a, audio * 0.3) + audio  # 30% boost

# NEW (CORRECT - conservative):
sos_hp = signal.butter(2, 60, "hp", fs=sr)  # 2nd order, 60Hz (gentler)
# Only boost if mid frequencies are weak
if mid_energy < total_energy * 0.3:
    b, a = signal.iirpeak(2000, Q=3, fs=sr)  # Narrower boost
    boost = signal.filtfilt(b, a, audio * 0.15)  # Only 15% boost
    audio = audio + boost
```

---

### Issue 3: Enhancement Applied to Clean TTS Output ⚠️ **CRITICAL**

**Problem:**
- Enhancement always applies full processing chain
- Edge TTS produces clean audio that doesn't need enhancement
- Full enhancement corrupts clean audio

**Root Cause:**
- No detection of TTS output quality
- Same processing applied to all audio
- Clean TTS audio gets corrupted by enhancement

**Fix Applied:**
```python
# NEW: Detect TTS output quality
signal_quality = rms / max_val

if signal_quality > 0.15:  # High-quality TTS output
    logger.info("Detected high-quality TTS, using minimal enhancement")
    # Only normalize - skip noise reduction and aggressive EQ
    audio = self._normalize_audio(audio)
else:
    # Noisy audio - apply full enhancement
    audio = self._reduce_noise(audio, sr)
    audio = self._enhance_eq(audio, sr, quality)
    audio = self._apply_compression(audio, sr, quality)
    audio = self._normalize_audio(audio)
```

---

### Issue 4: Edge TTS Async Call Issues ⚠️ **MEDIUM PRIORITY**

**Problem:**
- Edge TTS async call might not wait properly
- File might be written incompletely
- No verification of output file

**Root Cause:**
- `run_async_in_thread` might not wait for completion
- No file validation after synthesis

**Fix Applied:**
```python
# Added file verification:
if not output_path.exists():
    raise RuntimeError(f"Edge TTS output file not created")
if output_path.stat().st_size == 0:
    raise RuntimeError(f"Edge TTS output file is empty")

# Use temporary file for atomic write:
temp_path = str(output_path) + ".tmp"
await communicate.save(temp_path)
shutil.move(temp_path, str(output_path))
```

---

## Complete Fix Summary

### Changes Made to `enhancement.py`:

1. **Conservative Noise Reduction**:
   - Detects clean TTS output
   - Uses soft gating instead of hard gating
   - Higher threshold (3x instead of 1.5x)
   - Preserves minimum 30% of signal

2. **Gentle EQ Enhancement**:
   - 2nd-order filter instead of 4th-order
   - Lower cutoff (60Hz instead of 80Hz)
   - Only boosts if mid frequencies are weak
   - Reduced boost amount (15% instead of 30%)

3. **Smart Enhancement Detection**:
   - Detects high-quality TTS output
   - Skips aggressive processing for clean audio
   - Only applies minimal normalization

4. **Better Error Handling**:
   - Returns original audio if enhancement fails
   - No exceptions that break the pipeline

### Changes Made to `synthesis.py`:

1. **Edge TTS File Verification**:
   - Verifies file exists and has content
   - Uses temporary file for atomic write
   - Better error messages

---

## Testing Recommendations

1. **Generate New Vocals**:
   - Use `female_singer_1` profile
   - Check that vocals are clear (not glitchy)
   - Verify female voice is audible

2. **Check Audio Properties**:
   - Should have good RMS levels
   - No excessive noise reduction artifacts
   - Clear voice frequencies present

3. **Listen Test**:
   - Should sound like clear female voice
   - No "glitch" or static sounds
   - Natural speech quality

---

## Expected Results After Fixes

✅ **Clear Female Voice**: Vocals sound like natural female speech  
✅ **No Glitches**: No static or corrupted sounds  
✅ **Good Quality**: High-quality TTS output preserved  
✅ **Minimal Processing**: Clean audio gets minimal enhancement  

---

**Last Updated**: 2025-12-05  
**Status**: ✅ Critical Fixes Applied
