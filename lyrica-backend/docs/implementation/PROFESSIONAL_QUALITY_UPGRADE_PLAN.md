# Professional Song Quality Upgrade Plan

## Current Status: 5% Professional Quality

### Critical Issues

1. **❌ Music Generation**: Using MIDI fallback (NOT AI-powered)
2. **❌ AudioCraft/MusicGen**: Not installed (Python 3.12 compatibility)
3. **❌ Vocals**: Too quiet, no professional processing
4. **❌ Mixing**: Basic volume balancing only
5. **❌ Mastering**: Missing professional chain

---

## Solution: Integrate YuE (Full-Song Generation) ⭐ **RECOMMENDED**

### Why YuE?

- ✅ **Full-song generation**: Vocals + Music together
- ✅ **Professional quality**: Similar to Suno.ai
- ✅ **Open-source**: Apache 2.0 license
- ✅ **Python compatible**: Likely works with Python 3.12
- ✅ **Style transfer**: Can match reference tracks
- ✅ **Voice cloning**: Can use custom voices

### YuE GitHub Repository

**Repository**: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation

**Key Features:**
- Dual-track in-context learning
- Style transfer
- Voice cloning
- Lyric alignment
- Full-song generation

---

## Implementation Steps

### Step 1: Research YuE Installation

```bash
# Clone YuE repository
git clone https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation.git
cd YuE-Open-Full-song-Music-Generation

# Check requirements
cat requirements.txt

# Check Python compatibility
python --version  # Should work with Python 3.12
```

### Step 2: Create YuE Service Integration

**File**: `lyrica-backend/app/services/music/yue_generation.py`

```python
"""
YuE Full-Song Generation Service.

Integrates YuE model for professional-quality full-song generation.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.music_config import MusicGenre


class YueGenerationService:
    """Service for YuE full-song generation."""
    
    def __init__(self):
        """Initialize YuE service."""
        self._yue_model = None
        self._yue_available = self._check_yue_availability()
    
    def _check_yue_availability(self) -> bool:
        """Check if YuE is available."""
        try:
            # Try importing YuE
            # from yue import YueModel  # Adjust import based on actual package
            return False  # Placeholder until we verify installation
        except ImportError:
            logger.info("YuE not available. Install from: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation")
            return False
    
    def generate_full_song(
        self,
        lyrics: str,
        genre: MusicGenre,
        duration: int = 180,
        style: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate full song with vocals and music using YuE.
        
        Args:
            lyrics: Song lyrics
            genre: Music genre
            duration: Duration in seconds
            style: Optional style reference
            output_path: Output path
            
        Returns:
            Path to generated full song
        """
        if not self._yue_available:
            raise ImportError("YuE not installed. See installation guide.")
        
        # Load model if needed
        if self._yue_model is None:
            self._load_yue_model()
        
        logger.info(f"Generating full song with YuE: {genre.value}, {duration}s")
        
        # Generate full song
        # song = self._yue_model.generate(
        #     lyrics=lyrics,
        #     genre=genre.value,
        #     duration=duration,
        #     style=style,
        # )
        
        # Save to file
        # song.save(str(output_path))
        
        logger.success(f"YuE full song generated: {output_path}")
        return output_path
    
    def _load_yue_model(self):
        """Load YuE model."""
        # Implementation depends on YuE API
        # self._yue_model = YueModel.from_pretrained("yue-model")
        pass
```

### Step 3: Update Music Generation Service

**File**: `lyrica-backend/app/services/music/generation.py`

Add YuE as primary method:

```python
def generate_by_genre(
    self,
    genre: MusicGenre,
    mood: Optional[MusicMood] = None,
    key: Optional[MusicKey] = None,
    bpm: int = 120,
    duration: int = 180,
    output_path: Optional[Path] = None,
) -> Path:
    """Generate music by genre."""
    
    # PRIORITY 1: Try YuE (full-song generation)
    if self._yue_available:
        try:
            return self._generate_with_yue(genre, duration, output_path)
        except Exception as e:
            logger.warning(f"YuE generation failed: {e}, falling back")
    
    # PRIORITY 2: Try AudioCraft/MusicGen
    if self._audiocraft_available:
        try:
            return self._generate_with_musicgen(genre, duration, output_path)
        except Exception as e:
            logger.warning(f"MusicGen generation failed: {e}, falling back")
    
    # FALLBACK: MIDI synthesis (NOT professional)
    logger.warning("Using MIDI fallback - NOT professional quality")
    return self._generate_midi_music(genre, key, bpm, duration, output_path)
```

### Step 4: Update Song Generation Pipeline

**File**: `lyrica-backend/app/api/v1/endpoints/production.py`

Use YuE for full-song generation:

```python
# Option 1: Generate full song with YuE (vocals + music together)
if yue_available:
    full_song_path = yue_service.generate_full_song(
        lyrics=lyrics_text,
        genre=genre_enum,
        duration=duration,
        output_path=full_song_path,
    )
    # Extract vocals and music separately if needed
    # Or use full song directly
else:
    # Fallback to separate generation
    vocals_path = voice_service.synthesize_lyrics(...)
    music_path = music_service.generate_by_genre(...)
    mixed_path = assembly_service.assemble_song(...)
```

---

## Alternative: ACE-Step Integration

### Why ACE-Step?

- ✅ **Fast generation**: 20 seconds for 4 minutes
- ✅ **Good quality**: Professional sound
- ✅ **Open-source**: Available on GitHub
- ✅ **Python compatible**: Likely works with Python 3.12

### ACE-Step Integration

**Repository**: Check arXiv paper for implementation details

**File**: `lyrica-backend/app/services/music/ace_step_generation.py`

```python
class ACEStepGenerationService:
    """Service for ACE-Step music generation."""
    
    def generate_music(
        self,
        prompt: str,
        duration: int = 180,
        genre: Optional[MusicGenre] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Generate music with ACE-Step."""
        # Implementation based on ACE-Step API
        pass
```

---

## Quick Wins (Can Implement Now)

### 1. Improve MIDI Fallback Quality

**File**: `lyrica-backend/app/services/music/generation.py`

**Improvements:**
- Use better soundfonts (FluidSynth with professional soundfonts)
- Add more tracks (pads, strings, brass)
- Add effects (reverb, delay, compression)
- Better arrangement (intro/verse/chorus structure)

### 2. Improve Vocal Processing

**File**: `lyrica-backend/app/services/voice/synthesis.py`

**Improvements:**
- Normalize vocals to -12dBFS (not -30dBFS)
- Add reverb and delay
- Add compression
- Add harmony layers
- Pitch correction (already available)

### 3. Improve Mixing

**File**: `lyrica-backend/app/services/production/song_assembly.py`

**Improvements:**
- Better EQ (genre-specific presets)
- Sidechain compression (already available)
- Stereo imaging (already available)
- Reverb and delay (already available)

### 4. Improve Mastering

**File**: `lyrica-backend/app/services/production/mastering.py`

**Improvements:**
- LUFS normalization (already available)
- Peak limiting (already available)
- Stereo enhancement
- Harmonic enhancement

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 days) ⚡ **DO THIS FIRST**

1. **Improve Vocal Volume**
   - Normalize vocals to -12dBFS
   - Add compression
   - Add reverb

2. **Improve MIDI Quality**
   - Better soundfonts
   - More tracks
   - Better arrangement

3. **Improve Mixing**
   - Genre-specific EQ
   - Better volume balancing
   - Sidechain compression

**Expected Result**: 20% professional quality (up from 5%)

### Phase 2: YuE Integration (1 week) ⭐ **CRITICAL**

1. **Research YuE**
   - Check installation requirements
   - Test generation quality
   - Verify Python 3.12 compatibility

2. **Integrate YuE**
   - Create YuE service
   - Update music generation pipeline
   - Test full-song generation

3. **Update Pipeline**
   - Use YuE for full-song generation
   - Extract vocals/music if needed
   - Apply professional mixing/mastering

**Expected Result**: 60% professional quality

### Phase 3: Professional Processing (1 week)

1. **Vocal Processing**
   - Pitch correction
   - Timing correction
   - Harmony layers
   - Vocal effects

2. **Mixing & Mastering**
   - Multi-band EQ
   - Dynamic processing
   - Spatial effects
   - Mastering chain

**Expected Result**: 90% professional quality

---

## Installation Guide

### YuE Installation

```bash
# Clone repository
git clone https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation.git
cd YuE-Open-Full-song-Music-Generation

# Install dependencies
pip install -r requirements.txt

# Download model weights
# (Follow YuE documentation)

# Test installation
python -c "from yue import YueModel; print('YuE installed successfully')"
```

### Update requirements.txt

```txt
# Full-Song Generation (YuE)
# Install from: https://github.com/Decentralised-AI/YuE-Open-Full-song-Music-Generation
# yue>=1.0.0  # Uncomment when YuE package is available
```

---

## Testing Plan

### Test 1: YuE Generation Quality

```python
# Test YuE generation
yue_service = YueGenerationService()
song_path = yue_service.generate_full_song(
    lyrics="Test lyrics here",
    genre=MusicGenre.POP,
    duration=180,
)

# Check quality
# - Listen to output
# - Check audio properties
# - Compare with current MIDI output
```

### Test 2: Integration with Pipeline

```python
# Test full pipeline with YuE
response = await generate_complete_song(
    lyrics_prompt="Write a pop song",
    genre="pop",
    voice_profile_id="female_singer_1",
    duration_seconds=180,
)

# Check final song quality
# - Professional sound?
# - Good mixing?
# - Good mastering?
```

---

## Expected Quality Improvement

### Current: 5% Professional
- ❌ MIDI music (robotic)
- ❌ Quiet vocals (-30dBFS)
- ❌ Basic mixing
- ❌ No mastering

### After Quick Wins: 20% Professional
- ⚠️ Better MIDI (still robotic)
- ✅ Louder vocals (-12dBFS)
- ✅ Better mixing
- ⚠️ Basic mastering

### After YuE Integration: 60% Professional
- ✅ AI-generated music
- ✅ Professional vocals
- ✅ Good mixing
- ✅ Good mastering

### After Full Implementation: 90% Professional
- ✅ AI-generated music (YuE)
- ✅ Professional vocal processing
- ✅ Professional mixing
- ✅ Professional mastering
- ✅ Music structure

---

## Next Steps

1. **⭐ PRIORITY: Research YuE**
   - Check GitHub repository
   - Verify installation requirements
   - Test generation quality
   - Check Python 3.12 compatibility

2. **Implement Quick Wins**
   - Improve vocal volume
   - Improve MIDI quality
   - Improve mixing

3. **Integrate YuE**
   - Create YuE service
   - Update pipeline
   - Test generation

4. **Professional Processing**
   - Vocal processing
   - Mixing & mastering
   - Music structure

---

**Last Updated**: 2025-12-05  
**Status**: ⚠️ **CRITICAL - NEEDS IMMEDIATE ATTENTION**  
**Priority**: ⭐ **HIGHEST - This will improve quality from 5% to 60%**
