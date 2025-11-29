# Audio Quality & Optimization Guide

> **Professional audio enhancement, analysis, and quality control for AI-generated music**

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
  - [Quality Validation](#quality-validation)
  - [Noise Reduction](#noise-reduction)
  - [Dynamic Range Compression](#dynamic-range-compression)
  - [Stereo Widening](#stereo-widening)
  - [Audio Analysis](#audio-analysis)
  - [Enhancement Pipeline](#enhancement-pipeline)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Integration](#integration)

---

## Overview

The Audio Quality & Optimization system provides professional-grade tools for validating, analyzing, and enhancing audio files. Built on industry-standard audio processing libraries, it offers comprehensive quality control for AI-generated songs.

### Key Capabilities

- **🔍 Quality Validation**: Detect clipping, silence, DC offset, and quality issues
- **🎚️ Noise Reduction**: Remove background noise using spectral gating
- **📊 Dynamic Compression**: Control dynamic range for consistent loudness
- **🎼 Stereo Widening**: Enhance stereo image with M/S processing
- **📈 Audio Analysis**: Comprehensive loudness, clarity, and spectral analysis
- **🚀 Enhancement Pipeline**: Multi-algorithm processing chain
- **📦 Batch Processing**: Process multiple files efficiently

### Technologies

- **librosa**: Advanced audio analysis and feature extraction
- **soundfile**: High-quality audio I/O operations
- **scipy**: Signal processing algorithms
- **pydub**: Audio manipulation and format conversion
- **numpy**: Numerical computations and array operations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Audio Quality & Optimization System               │
│                /api/v1/audio-quality/*                      │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┼─────────┬──────────────┬────────────┐
    │        │         │              │            │
    v        v         v              v            v
┌─────────┐ ┌───────────┐ ┌────────────┐ ┌──────────┐ ┌──────┐
│Validate │ │Enhancement│ │  Analysis  │ │  Batch   │ │ API  │
│ Service │ │  Service  │ │  Service   │ │Processing│ │Schema│
├─────────┤ ├───────────┤ ├────────────┤ ├──────────┤ ├──────┤
│Quality  │ │Noise      │ │Loudness    │ │Multi-file│ │25+   │
│Scoring  │ │Reduction  │ │Analysis    │ │Validation│ │Models│
│Clipping │ │Compression│ │Clarity     │ │Multi-file│ │      │
│Detection│ │Stereo     │ │Spectral    │ │Enhance   │ │      │
│Silence  │ │Widening   │ │Performance │ │          │ │      │
│Analysis │ │Normalize  │ │Metrics     │ │          │ │      │
└─────────┘ └───────────┘ └────────────┘ └──────────┘ └──────┘
```

### Processing Flow

**Quality Validation**:

```
Audio File → Load → Check Duration → Check Sample Rate → 
Check Clipping → Check Silence → Analyze Dynamic Range → 
Calculate Quality Score → Generate Grade
```

**Enhancement Pipeline**:

```
Audio File → Noise Reduction → Dynamic Compression → 
Stereo Widening → Loudness Normalization → Enhanced Output
```

**Comprehensive Analysis**:

```
Audio File → Loudness Metrics → Clarity Metrics → 
Spectral Analysis → Performance Metrics → 
Combined Quality Score → Overall Grade
```

---

## Features

### Quality Validation

Comprehensive validation against quality standards and best practices.

**Checks Performed**:

- **Duration**: Validates audio length is within acceptable range
- **Sample Rate**: Ensures minimum sample rate for quality
- **File Size**: Checks file size against limits
- **Clipping**: Detects samples exceeding threshold (>99%)
- **Silence**: Measures silent portions of audio
- **Dynamic Range**: Calculates peak-to-RMS ratio in dB
- **DC Offset**: Detects DC component in signal

**Quality Scoring**:

- Base score: 100 points
- Deductions: 20 points per error, 5 points per warning
- Bonuses: Good metrics earn bonus points
- Final grade: A-F based on score

**Example Output**:

```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Audio clipping detected: 2.5% of samples"],
  "metrics": {
    "duration_seconds": 180.5,
    "sample_rate": 44100,
    "channels": 2,
    "bit_depth": 16,
    "clipping_ratio": 0.025,
    "silence_ratio": 0.05,
    "dynamic_range_db": 12.5,
    "dc_offset": 0.0001,
    "file_size_mb": 31.2
  },
  "quality_score": 85.0,
  "grade": "B"
}
```

---

### Noise Reduction

Remove background noise while preserving audio quality using spectral gating.

**How It Works**:

1. **Analyze**: Compute STFT (Short-Time Fourier Transform)
2. **Estimate**: Calculate noise floor from quietest frames
3. **Create Mask**: Generate frequency-dependent mask based on SNR
4. **Apply**: Multiply spectrum by mask
5. **Reconstruct**: Inverse STFT to time domain

**Parameters**:

- `strength` (0.0-1.0): Aggressiveness of noise reduction
  - 0.3-0.5: Subtle (preserve natural sound)
  - 0.5-0.7: Moderate (balanced)
  - 0.7-1.0: Aggressive (maximum reduction)

**Use Cases**:

- Clean up home recordings
- Remove HVAC noise
- Reduce microphone hiss
- Improve podcast audio

**Example**:

```python
# Moderate noise reduction
curl -X POST "http://localhost:8000/api/v1/audio-quality/reduce-noise" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_path": "audio_files/noisy_recording.wav",
    "strength": 0.6
  }'
```

---

### Dynamic Range Compression

Control the dynamic range for more consistent loudness levels.

**How It Works**:

1. **Envelope Detection**: Calculate RMS envelope of audio
2. **Threshold Detection**: Identify samples above threshold
3. **Gain Calculation**: Compute gain reduction based on ratio
4. **Smooth Envelope**: Apply attack/release times
5. **Apply Gain**: Multiply audio by smooth gain envelope

**Parameters**:

- `threshold_db`: Level above which compression starts (e.g., -20 dB)
- `ratio`: Compression ratio (e.g., 4:1 means 4 dB in → 1 dB out)
- `attack_ms`: How fast compressor responds to loud signals (e.g., 5 ms)
- `release_ms`: How fast compressor returns to normal (e.g., 100 ms)

**Common Settings**:

```python
# Light compression (natural)
{"threshold_db": -18, "ratio": 2.0, "attack_ms": 10, "release_ms": 150}

# Moderate compression (balanced)
{"threshold_db": -20, "ratio": 4.0, "attack_ms": 5, "release_ms": 100}

# Heavy compression (broadcast)
{"threshold_db": -24, "ratio": 6.0, "attack_ms": 3, "release_ms": 50}
```

**Use Cases**:

- Reduce volume differences between sections
- Increase perceived loudness
- Meet broadcast standards
- Improve clarity in noisy environments

---

### Stereo Widening

Enhance the stereo image for a more spacious sound.

**How It Works**:

1. **M/S Decomposition**: Split into Mid (L+R) and Side (L-R) signals
2. **Widen Side**: Multiply side signal by width factor
3. **Reconstruct**: Combine back into L/R channels
4. **Normalize**: Prevent clipping from increased levels

**Parameters**:

- `width` (0.0-3.0): Stereo width multiplier
  - 0.0: Mono (no stereo)
  - 1.0: Original width
  - 1.5: Moderately wider
  - 2.0: Significantly wider
  - 3.0: Maximum width

**Important Notes**:

- ⚠️ Only works on stereo content
- ⚠️ Mono files are converted to stereo first
- ⚠️ Excessive widening can cause phase issues
- ⚠️ Test on headphones AND speakers

**Use Cases**:

- Enhance stereo recordings
- Create immersive mixes
- Improve spatial separation
- Modernize narrow mixes

---

### Audio Analysis

Comprehensive analysis of audio characteristics and quality.

#### Loudness Analysis

**Metrics Provided**:

- **RMS (dB)**: Root Mean Square average level
- **Peak (dB)**: Maximum sample value
- **True Peak (dB)**: Inter-sample peak (upsampled detection)
- **Estimated LUFS**: Loudness Units Full Scale (broadcast standard)
- **Crest Factor (dB)**: Peak-to-RMS ratio
- **Loudness Range (dB)**: Difference between loud and quiet parts
- **Headroom (dB)**: Distance from true peak to 0 dBFS
- **Is Clipping**: Boolean indicating clipping

**Target Values**:

- **LUFS**: -14.0 for streaming, -16.0 for broadcast
- **True Peak**: < -1.0 dB (safety margin)
- **Headroom**: > 1.0 dB
- **Crest Factor**: 8-14 dB for music

**Example Output**:

```json
{
  "rms_db": -18.5,
  "peak_db": -3.2,
  "true_peak_db": -2.8,
  "estimated_lufs": -15.2,
  "crest_factor_db": 10.8,
  "loudness_range_db": 8.5,
  "is_clipping": false,
  "headroom_db": 2.8
}
```

#### Clarity Analysis

**Metrics Provided**:

- **Spectral Centroid (Hz)**: "Brightness" of sound
- **Spectral Rolloff (Hz)**: Frequency below which 85% of energy lies
- **Spectral Bandwidth (Hz)**: Range of frequencies
- **Zero Crossing Rate**: Noisiness indicator
- **Estimated SNR (dB)**: Signal-to-noise ratio
- **Spectral Contrast (dB)**: Dynamic range across frequency bands
- **Clarity Score (0-100)**: Overall clarity rating
- **Quality Grade**: Excellent, Very Good, Good, Fair, Poor, Very Poor

**Interpretation**:

- **High Centroid**: Bright, trebly sound
- **Low Centroid**: Dark, bass-heavy sound
- **High ZCR**: Noisy, distorted
- **Low ZCR**: Clean, pure tones
- **High SNR**: Clean recording (>40 dB excellent)
- **Low SNR**: Noisy recording (<20 dB poor)

#### Spectral Analysis

**Frequency Bands**:

- **Sub-bass**: 20-60 Hz (felt more than heard)
- **Bass**: 60-250 Hz (body, warmth)
- **Low-mid**: 250-500 Hz (fullness)
- **Mid**: 500-2000 Hz (presence, clarity)
- **High-mid**: 2000-4000 Hz (definition)
- **Presence**: 4000-6000 Hz (intelligibility)
- **Brilliance**: 6000-20000 Hz (air, sparkle)

**Metrics**:

- **Band Energy (dB)**: Average level in each band
- **Spectral Flatness**: Tonal (0.0) vs Noisy (1.0)
- **Is Tonal**: Flatness < 0.1
- **Is Noisy**: Flatness > 0.5

**Use Cases**:

- Check frequency balance
- Identify missing frequencies
- Detect resonances
- Guide EQ decisions

#### Performance Metrics

**File Metrics**:

- **File Size (MB)**: Storage requirement
- **Duration (seconds)**: Length
- **Sample Rate (Hz)**: 44100, 48000, 96000, etc.
- **Bit Depth**: 16, 24, 32-bit
- **Channels**: Mono (1) or Stereo (2)
- **Estimated Bitrate (kbps)**: Compression ratio

**Quality Indicators**:

- **High Frequency Preservation**: Ratio of HF energy
- **Encoding Quality**: Excellent, Good, Acceptable, Poor

**Ideal Values**:

- Sample Rate: ≥ 44100 Hz
- Bit Depth: ≥ 16-bit
- Bitrate: ≥ 192 kbps for music
- HF Preservation: > 0.01 for lossless

---

### Enhancement Pipeline

Apply multiple algorithms in an optimized processing chain.

**Processing Order** (optimized):

1. **Noise Reduction**: Remove unwanted background noise
2. **Dynamic Compression**: Control dynamic range
3. **Stereo Widening**: Enhance stereo image (optional)
4. **Loudness Normalization**: Achieve target loudness

**Why This Order?**:

- Noise reduction first (clean signal for other processing)
- Compression second (controls dynamics before spatial processing)
- Widening third (works better on compressed signal)
- Normalization last (final loudness adjustment)

**Example**:

```python
# Full enhancement pipeline
{
  "audio_path": "audio_files/raw.wav",
  "reduce_noise": true,      # Clean it
  "compress": true,           # Control it
  "widen_stereo": false,      # Skip widening
  "normalize": true           # Match loudness target
}
```

**Presets**:

**Minimal Enhancement**:

```json
{"reduce_noise": false, "compress": false, "normalize": true}
```

**Podcast Enhancement**:

```json
{"reduce_noise": true, "compress": true, "normalize": true}
```

**Music Enhancement**:

```json
{"reduce_noise": true, "compress": false, "normalize": true}
```

**Full Enhancement**:

```json
{"reduce_noise": true, "compress": true, "widen_stereo": true, "normalize": true}
```

---

## API Endpoints

### Validation Endpoints

#### POST `/api/v1/audio-quality/validate`

Validate audio file against quality standards.

**Request**:

```json
{
  "audio_path": "audio_files/my_song.wav",
  "min_duration_seconds": 30.0,
  "max_duration_seconds": 300.0,
  "min_sample_rate": 16000,
  "max_file_size_mb": 100.0
}
```

**Response**:

```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Audio clipping detected: 1.5%"],
  "metrics": {
    "duration_seconds": 180.5,
    "sample_rate": 44100,
    "channels": 2,
    "clipping_ratio": 0.015,
    "silence_ratio": 0.05,
    "dynamic_range_db": 12.5
  }
}
```

---

#### POST `/api/v1/audio-quality/quality-score`

Calculate overall quality score (0-100).

**Request**:

```json
{
  "audio_path": "audio_files/my_song.wav"
}
```

**Response**:

```json
{
  "quality_score": 85.0,
  "grade": "B",
  "validation": { /* full validation results */ }
}
```

---

#### POST `/api/v1/audio-quality/validate-batch`

Validate multiple files.

**Request**:

```json
{
  "audio_paths": [
    "audio_files/song1.wav",
    "audio_files/song2.wav"
  ],
  "min_duration_seconds": 30.0,
  "max_duration_seconds": 300.0
}
```

**Response**:

```json
{
  "results": [ /* individual validation results */ ],
  "summary": {
    "total": 2,
    "passed": 2,
    "failed": 0,
    "total_warnings": 3
  }
}
```

---

### Enhancement Endpoints

#### POST `/api/v1/audio-quality/reduce-noise`

Apply noise reduction.

**Request**:

```json
{
  "audio_path": "audio_files/noisy.wav",
  "strength": 0.6
}
```

**Response**:

```json
{
  "success": true,
  "output_path": "audio_files/noisy_denoised.wav",
  "message": "Noise reduction applied successfully (strength: 0.6)",
  "processing_time_seconds": 3.2
}
```

---

#### POST `/api/v1/audio-quality/compress`

Apply dynamic range compression.

**Request**:

```json
{
  "audio_path": "audio_files/dynamic.wav",
  "threshold_db": -20.0,
  "ratio": 4.0,
  "attack_ms": 5.0,
  "release_ms": 100.0
}
```

**Response**:

```json
{
  "success": true,
  "output_path": "audio_files/dynamic_compressed.wav",
  "message": "Compression applied (ratio: 4.0:1, threshold: -20.0dB)",
  "processing_time_seconds": 2.8
}
```

---

#### POST `/api/v1/audio-quality/widen-stereo`

Apply stereo widening.

**Request**:

```json
{
  "audio_path": "audio_files/narrow.wav",
  "width": 1.5
}
```

**Response**:

```json
{
  "success": true,
  "output_path": "audio_files/narrow_widened.wav",
  "message": "Stereo widening applied (width: 1.5x)",
  "processing_time_seconds": 1.5
}
```

---

#### POST `/api/v1/audio-quality/enhance`

Apply full enhancement pipeline.

**Request**:

```json
{
  "audio_path": "audio_files/raw.wav",
  "reduce_noise": true,
  "compress": true,
  "widen_stereo": false,
  "normalize": true
}
```

**Response**:

```json
{
  "success": true,
  "output_path": "audio_files/raw_enhanced.wav",
  "message": "Enhancement complete: noise reduction, compression, normalization",
  "processing_time_seconds": 8.5
}
```

---

#### POST `/api/v1/audio-quality/normalize-loudness`

Normalize to target LUFS.

**Request**:

```json
{
  "audio_path": "audio_files/quiet.wav",
  "target_lufs": -14.0
}
```

**Response**:

```json
{
  "success": true,
  "output_path": "audio_files/quiet_normalized.wav",
  "message": "Loudness normalized to -14.0 LUFS",
  "processing_time_seconds": 1.2
}
```

---

### Analysis Endpoints

#### GET `/api/v1/audio-quality/analyze/loudness`

Analyze loudness metrics.

**Request**:

```
GET /api/v1/audio-quality/analyze/loudness?audio_path=audio_files/song.wav
```

**Response**:

```json
{
  "rms_db": -18.5,
  "peak_db": -3.2,
  "true_peak_db": -2.8,
  "estimated_lufs": -15.2,
  "crest_factor_db": 10.8,
  "loudness_range_db": 8.5,
  "is_clipping": false,
  "headroom_db": 2.8
}
```

---

#### GET `/api/v1/audio-quality/analyze/clarity`

Analyze clarity and quality.

**Request**:

```
GET /api/v1/audio-quality/analyze/clarity?audio_path=audio_files/song.wav
```

**Response**:

```json
{
  "spectral_centroid_hz": 2500.5,
  "spectral_rolloff_hz": 8000.2,
  "spectral_bandwidth_hz": 5500.0,
  "zero_crossing_rate": 0.05,
  "estimated_snr_db": 35.2,
  "spectral_contrast_db": 18.5,
  "clarity_score": 85.0,
  "quality_grade": "Very Good"
}
```

---

#### GET `/api/v1/audio-quality/analyze/spectral`

Analyze frequency spectrum.

**Request**:

```
GET /api/v1/audio-quality/analyze/spectral?audio_path=audio_files/song.wav
```

**Response**:

```json
{
  "frequency_band_energy_db": {
    "sub_bass": -35.2,
    "bass": -28.5,
    "low_mid": -22.8,
    "mid": -18.2,
    "high_mid": -20.5,
    "presence": -22.0,
    "brilliance": -28.5
  },
  "spectral_flatness": 0.08,
  "is_tonal": true,
  "is_noisy": false
}
```

---

#### GET `/api/v1/audio-quality/analyze/performance`

Analyze file and encoding metrics.

**Request**:

```
GET /api/v1/audio-quality/analyze/performance?audio_path=audio_files/song.wav
```

**Response**:

```json
{
  "file_size_mb": 31.5,
  "duration_seconds": 180.5,
  "sample_rate_hz": 44100,
  "channels": 2,
  "bit_depth": 16,
  "estimated_bitrate_kbps": 1411.2,
  "high_frequency_preservation": 0.012,
  "encoding_quality": "Excellent"
}
```

---

#### GET `/api/v1/audio-quality/analyze/comprehensive`

Complete analysis with all metrics.

**Request**:

```
GET /api/v1/audio-quality/analyze/comprehensive?audio_path=audio_files/song.wav
```

**Response**:

```json
{
  "file_path": "audio_files/song.wav",
  "loudness": { /* loudness metrics */ },
  "clarity": { /* clarity metrics */ },
  "spectral": { /* spectral metrics */ },
  "performance": { /* performance metrics */ },
  "overall": {
    "quality_score": 85.0,
    "grade": "A-",
    "loudness_score": 88.0,
    "clarity_score": 85.0,
    "spectral_score": 82.0
  }
}
```

---

## Usage Examples

### Workflow 1: Quality Check Before Publishing

```python
import httpx

async def check_quality(audio_path: str):
    async with httpx.AsyncClient() as client:
        # 1. Run comprehensive analysis
        analysis = await client.get(
            f"http://localhost:8000/api/v1/audio-quality/analyze/comprehensive",
            params={"audio_path": audio_path}
        )
        result = analysis.json()
        
        # 2. Check overall grade
        grade = result["overall"]["grade"]
        score = result["overall"]["quality_score"]
        
        print(f"Quality: {grade} ({score}/100)")
        
        # 3. Check for issues
        if result["loudness"]["is_clipping"]:
            print("⚠️ Warning: Clipping detected!")
        
        if result["clarity"]["clarity_score"] < 70:
            print("⚠️ Warning: Low clarity score!")
        
        # 4. Make decision
        if score >= 80:
            print("✅ Ready for publishing!")
            return True
        else:
            print("❌ Enhancement recommended")
            return False
```

---

### Workflow 2: Automatic Enhancement

```python
async def enhance_audio(audio_path: str):
    async with httpx.AsyncClient() as client:
        # 1. Validate first
        validation = await client.post(
            "http://localhost:8000/api/v1/audio-quality/validate",
            json={"audio_path": audio_path}
        )
        
        if not validation.json()["is_valid"]:
            print("❌ Validation failed")
            return None
        
        # 2. Analyze to determine what's needed
        clarity = await client.get(
            "http://localhost:8000/api/v1/audio-quality/analyze/clarity",
            params={"audio_path": audio_path}
        )
        snr = clarity.json()["estimated_snr_db"]
        
        # 3. Apply appropriate enhancement
        needs_noise_reduction = snr < 30
        
        enhanced = await client.post(
            "http://localhost:8000/api/v1/audio-quality/enhance",
            json={
                "audio_path": audio_path,
                "reduce_noise": needs_noise_reduction,
                "compress": True,
                "normalize": True
            }
        )
        
        return enhanced.json()["output_path"]
```

---

### Workflow 3: Batch Quality Control

```python
async def check_album_quality(audio_paths: list[str]):
    async with httpx.AsyncClient() as client:
        # 1. Batch validation
        validation = await client.post(
            "http://localhost:8000/api/v1/audio-quality/validate-batch",
            json={"audio_paths": audio_paths}
        )
        
        results = validation.json()
        
        # 2. Print summary
        summary = results["summary"]
        print(f"Validated {summary['total']} tracks:")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⚠️  Warnings: {summary['total_warnings']}")
        
        # 3. Identify problems
        for i, result in enumerate(results["results"]):
            if not result["is_valid"]:
                print(f"\nTrack {i+1} issues:")
                for error in result["errors"]:
                    print(f"  ❌ {error}")
            elif result["warnings"]:
                print(f"\nTrack {i+1} warnings:")
                for warning in result["warnings"]:
                    print(f"  ⚠️  {warning}")
```

---

### Workflow 4: Targeted Enhancement

```python
async def fix_specific_issues(audio_path: str):
    async with httpx.AsyncClient() as client:
        # 1. Analyze to identify issues
        analysis = await client.get(
            "http://localhost:8000/api/v1/audio-quality/analyze/comprehensive",
            params={"audio_path": audio_path}
        )
        result = analysis.json()
        
        output_path = audio_path
        
        # 2. Fix clipping with compression
        if result["loudness"]["is_clipping"]:
            print("Fixing clipping with compression...")
            compressed = await client.post(
                "http://localhost:8000/api/v1/audio-quality/compress",
                json={
                    "audio_path": output_path,
                    "threshold_db": -20,
                    "ratio": 4.0
                }
            )
            output_path = compressed.json()["output_path"]
        
        # 3. Improve clarity with noise reduction
        if result["clarity"]["estimated_snr_db"] < 30:
            print("Improving clarity with noise reduction...")
            cleaned = await client.post(
                "http://localhost:8000/api/v1/audio-quality/reduce-noise",
                json={
                    "audio_path": output_path,
                    "strength": 0.5
                }
            )
            output_path = cleaned.json()["output_path"]
        
        # 4. Match broadcast loudness
        if abs(result["loudness"]["estimated_lufs"] - (-14.0)) > 2.0:
            print("Normalizing loudness...")
            normalized = await client.post(
                "http://localhost:8000/api/v1/audio-quality/normalize-loudness",
                json={
                    "audio_path": output_path,
                    "target_lufs": -14.0
                }
            )
            output_path = normalized.json()["output_path"]
        
        print(f"✅ Enhanced: {output_path}")
        return output_path
```

---

## Best Practices

### 1. **Always Validate First**

```python
# ✅ Good: Check quality before processing
validation = validate(audio_path)
if validation["is_valid"]:
    enhance(audio_path)

# ❌ Bad: Enhance without validation
enhance(audio_path)  # Might enhance already-good audio
```

### 2. **Use Appropriate Strength**

```python
# ✅ Good: Start subtle, increase if needed
reduce_noise(audio_path, strength=0.4)  # Preserve naturalness

# ❌ Bad: Maximum strength by default
reduce_noise(audio_path, strength=1.0)  # May sound artificial
```

### 3. **Match Target Platform**

```python
# Streaming platforms (Spotify, Apple Music)
normalize_loudness(audio_path, target_lufs=-14.0)

# Broadcast (TV, radio)
normalize_loudness(audio_path, target_lufs=-16.0)

# YouTube
normalize_loudness(audio_path, target_lufs=-13.0)

# CD mastering
normalize_loudness(audio_path, target_lufs=-9.0)
```

### 4. **Preserve Headroom**

```python
# ✅ Good: Leave headroom for safety
if analysis["loudness"]["true_peak_db"] > -1.0:
    print("Warning: Insufficient headroom")

# ❌ Bad: Maximize to 0 dBFS
# This risks clipping in format conversion
```

### 5. **Test Stereo Widening Carefully**

```python
# ✅ Good: Moderate widening
widen_stereo(audio_path, width=1.3)  # Subtle enhancement

# ⚠️ Caution: Excessive widening
widen_stereo(audio_path, width=3.0)  # May cause phase issues
```

### 6. **Batch Process Similar Content**

```python
# ✅ Good: Batch process album
batch_enhance(album_tracks, same_settings_for_all)

# ❌ Bad: Different settings per track
for track in album_tracks:
    enhance(track, random_settings)  # Inconsistent
```

### 7. **Monitor Processing Time**

```python
# ✅ Good: Track performance
start = time.time()
result = enhance(audio_path)
duration = time.time() - start
print(f"Processed in {duration:.1f}s")

# Consider async/parallel for multiple files
```

### 8. **Keep Originals**

```python
# ✅ Good: Never overwrite originals
output_path = enhance(original_path)  # Creates new file

# ❌ Bad: Overwrite original
enhance(original_path, output_path=original_path)  # Destructive!
```

---

## Troubleshooting

### Issue: Excessive Noise Reduction Artifacts

**Symptoms**: Audio sounds "bubbly", "watery", or "swirly"

**Solution**:

```python
# Reduce strength
reduce_noise(audio_path, strength=0.3)  # Instead of 0.8
```

---

### Issue: Compression Making Audio Sound Lifeless

**Symptoms**: Loss of dynamics, everything same loudness

**Solution**:

```python
# Reduce ratio or increase threshold
compress(audio_path, threshold_db=-16, ratio=2.0)  # Lighter compression
```

---

### Issue: Stereo Widening Causing Phase Problems

**Symptoms**: Sounds thin in mono, bass disappears

**Solution**:

```python
# Reduce width
widen_stereo(audio_path, width=1.2)  # More subtle

# Or skip for bass-heavy content
```

---

### Issue: Analysis Taking Too Long

**Symptoms**: Comprehensive analysis >30 seconds

**Solution**:

```python
# Use specific analysis instead of comprehensive
analyze_loudness(audio_path)  # Faster, focused analysis
```

---

### Issue: Validation Warnings for Good Audio

**Symptoms**: Warnings on professionally mastered audio

**Solution**:

```python
# Adjust validation thresholds
validate(audio_path, 
         min_duration_seconds=1.0,  # More lenient
         max_file_size_mb=200.0)     # Higher limit
```

---

## Integration

### Integration with Song Generation

```python
# After generating song
song_id = generate_complete_song(...)

# Get song file path
song_path = f"audio_files/songs/{song_id}/{song_id}.wav"

# Validate quality
validation = validate_audio(song_path)

# If quality issues, enhance
if validation["quality_score"] < 80:
    enhanced_path = enhance_audio(
        song_path,
        reduce_noise=True,
        compress=True,
        normalize=True
    )
    
    # Update song with enhanced version
    update_song_file(song_id, enhanced_path)
```

---

### Integration with Frontend

```typescript
// Real-time quality monitoring
const AnalysisDashboard: React.FC<{audioPath: string}> = ({audioPath}) => {
  const [analysis, setAnalysis] = useState(null);
  
  useEffect(() => {
    // Fetch comprehensive analysis
    fetch(`/api/v1/audio-quality/analyze/comprehensive?audio_path=${audioPath}`)
      .then(res => res.json())
      .then(data => setAnalysis(data));
  }, [audioPath]);
  
  if (!analysis) return <Loading />;
  
  return (
    <div>
      <QualityScore score={analysis.overall.quality_score} />
      <LoudnessMeter lufs={analysis.loudness.estimated_lufs} />
      <SpectralGraph bands={analysis.spectral.frequency_band_energy_db} />
      <ClarityIndicator score={analysis.clarity.clarity_score} />
    </div>
  );
};
```

---

### Integration with Mobile

```typescript
// React Native audio enhancement
import { AudioQualityAPI } from './api/audioQuality';

const enhanceRecording = async (recordingPath: string) => {
  // Show progress
  setStatus('Analyzing...');
  
  // Check quality
  const score = await AudioQualityAPI.getQualityScore(recordingPath);
  
  if (score.quality_score < 70) {
    setStatus('Enhancing...');
    
    // Apply enhancement
    const result = await AudioQualityAPI.enhance({
      audio_path: recordingPath,
      reduce_noise: true,
      compress: true,
      normalize: true
    });
    
    setStatus('Complete!');
    return result.output_path;
  }
  
  return recordingPath;
};
```

---

## Performance

### Expected Processing Times

| Operation | Duration | File Size | Notes |
|-----------|----------|-----------|-------|
| Validation | 1-3s | 3-5 min song | Fast checks |
| Noise Reduction | 5-15s | 3-5 min song | CPU intensive |
| Compression | 3-8s | 3-5 min song | Moderate |
| Stereo Widening | 2-5s | 3-5 min song | Fast |
| Full Enhancement | 10-30s | 3-5 min song | All algorithms |
| Loudness Analysis | 2-4s | 3-5 min song | Quick |
| Clarity Analysis | 3-6s | 3-5 min song | Moderate |
| Spectral Analysis | 4-8s | 3-5 min song | FFT computation |
| Comprehensive | 10-20s | 3-5 min song | All analyses |

### Optimization Tips

1. **Use targeted analysis**: Only run needed analyses
2. **Batch processing**: Process multiple files together
3. **Async operations**: Don't block on analysis
4. **Cache results**: Store analysis results in database
5. **Progressive enhancement**: Start with basic, add more if needed

---

## Conclusion

The Audio Quality & Optimization system provides professional-grade tools for ensuring your AI-generated songs meet industry standards. From validation to enhancement to comprehensive analysis, you have everything needed for quality control.

**Key Takeaways**:

- Always validate before enhancement
- Use appropriate settings for your use case
- Monitor quality metrics throughout pipeline
- Keep originals and track processing
- Test enhancements on various playback systems

For more information:

- [API Reference](./API_REFERENCE.md)
- [Complete Song API Guide](./COMPLETE_SONG_API_GUIDE.md)
- [Voice Synthesis Guide](./VOICE_SYNTHESIS_GUIDE.md)

---

**Last Updated**: 2024-01-15  
**API Version**: v1  
**Backend**: FastAPI + librosa + scipy + pydub
