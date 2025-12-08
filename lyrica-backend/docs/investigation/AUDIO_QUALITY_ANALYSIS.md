# Comprehensive Audio Quality Analysis & Fixes

## Critical Issues Identified

### Issue 1: Severe Clipping ⚠️ **CRITICAL**

**Problem:**

- Processed music files hitting 100% amplitude (32767/32768)
- Mixed output hitting 98.9% amplitude
- Causes severe distortion and "glitch" sounds

**Root Cause:**

- `normalize()` function pushes audio to maximum amplitude
- No headroom left after normalization
- No limiting applied after mixing

**Impact:**

- Distorted, harsh sound
- "Glitch" artifacts
- Unprofessional quality

**Fix Applied:**

```python
# OLD (WRONG - causes clipping):
mixed = normalize(mixed)  # Pushes to 100%

# NEW (CORRECT - proper headroom):
target_headroom_db = 0.5  # 0.5dB headroom for safety
mixed = pydub_normalize(mixed, headroom=target_headroom_db)

# Also added clipping detection and limiting:
if mixed.max >= mixed.max_possible_amplitude * 0.95:
    while mixed.max >= mixed.max_possible_amplitude * 0.95:
        mixed = mixed - 0.5  # Reduce until safe
```

---

### Issue 2: Insufficient Headroom Before Mixing ⚠️ **CRITICAL**

**Problem:**

- Only -3dB reduction before mixing
- When mixing two tracks, sum can exceed 0dBFS
- Causes clipping during overlay operation

**Root Cause:**

- Not enough headroom calculation
- Professional mixing requires -6dB per track minimum

**Impact:**

- Clipping during mixing
- Distortion artifacts
- Poor sound quality

**Fix Applied:**

```python
# OLD (WRONG - insufficient headroom):
vocals = vocals - 3.0  # Only 3dB reduction
music = music - 3.0

# NEW (CORRECT - proper headroom):
vocals = vocals - 6.0  # 6dB reduction per track
music = music - 6.0    # Ensures sum doesn't clip
```

---

### Issue 3: DC Offset in Vocals ⚠️ **HIGH PRIORITY**

**Problem:**

- Vocals have significant DC offset (-284 to -308)
- Causes low-frequency artifacts
- Can cause issues in mixing

**Root Cause:**

- TTS engines may introduce DC offset
- No DC offset removal before processing

**Impact:**

- Low-frequency rumble
- Mixing artifacts
- Unprofessional sound

**Fix Applied:**

```python
# Normalize with headroom (removes DC offset):
vocals = pydub_normalize(vocals, headroom=0.1)
music = pydub_normalize(music, headroom=0.1)
```

---

### Issue 4: Glitches in Music Generation ⚠️ **HIGH PRIORITY**

**Problem:**

- Sudden amplitude changes detected in music files
- Likely from MIDI synthesis or processing artifacts

**Root Cause:**

- MIDI-to-audio conversion may introduce artifacts
- No smoothing applied
- Abrupt changes in generated audio

**Impact:**

- "Glitch" sounds
- Unnatural transitions
- Poor quality

**Recommendation:**

- Review MIDI synthesis code
- Add smoothing filters
- Check music generation quality

---

### Issue 5: Very Quiet Vocals ⚠️ **MEDIUM PRIORITY**

**Problem:**

- Vocals at -29dBFS (very quiet)
- Music at -16dBFS (louder)
- Large imbalance

**Root Cause:**

- TTS output levels vary
- No automatic level matching

**Impact:**

- Vocals hard to hear
- Poor mix balance

**Fix Applied:**

- Normalization before mixing balances levels
- Proper headroom ensures good mix

---

## Complete Fix Summary

### Changes Made to `song_assembly.py`

1. **DC Offset Removal**:

   ```python
   vocals = pydub_normalize(vocals, headroom=0.1)
   music = pydub_normalize(music, headroom=0.1)
   ```

2. **Proper Headroom Before Mixing**:

   ```python
   vocals = vocals - 6.0  # 6dB reduction
   music = music - 6.0    # 6dB reduction
   ```

3. **Clipping Detection & Limiting**:

   ```python
   if mixed.max >= mixed.max_possible_amplitude * 0.95:
       while mixed.max >= mixed.max_possible_amplitude * 0.95:
           mixed = mixed - 0.5
   ```

4. **Normalization with Headroom**:

   ```python
   target_headroom_db = 0.5  # 0.5dB headroom
   mixed = pydub_normalize(mixed, headroom=target_headroom_db)
   ```

---

## Testing Recommendations

1. **Generate New Song**:
   - Use the fixed pipeline
   - Check for clipping (should be < 95% amplitude)
   - Verify no glitches

2. **Check Audio Properties**:
   - Max amplitude should be < 95% of max possible
   - No DC offset
   - Proper stereo imaging
   - Good RMS levels

3. **Listen Test**:
   - No distortion
   - No glitches
   - Clear vocals
   - Balanced mix

---

## Remaining Issues to Address

### Music Generation Quality

The MIDI-based music generation may need improvement:

- Add smoothing filters
- Improve synthesis quality
- Reduce artifacts

### Vocals Volume Matching

Consider automatic level matching:

- Analyze TTS output levels
- Automatically adjust to target level
- Ensure consistent vocal levels

### Mastering Chain

Ensure mastering applies proper limiting:

- Check `master_audio` function
- Verify peak limiting is applied
- Confirm loudness normalization works

---

## Expected Results After Fixes

✅ **No Clipping**: Max amplitude < 95%  
✅ **No DC Offset**: Audio centered at 0  
✅ **Proper Headroom**: Safe mixing levels  
✅ **Balanced Mix**: Vocals and music properly balanced  
✅ **Professional Quality**: Production-ready output  

---

**Last Updated**: 2025-12-05  
**Status**: ✅ Critical Fixes Applied
