# User Acceptance Testing (UAT) Guide

**Comprehensive guide for conducting User Acceptance Testing (UAT) for Lyrica's voice and mixing enhancement features.**

---

## Overview

This guide provides step-by-step instructions for conducting UAT to validate:
- Voice enhancement quality improvements
- Mixing enhancement effectiveness
- Complete song generation pipeline
- User experience and satisfaction
- Performance and reliability

---

## Prerequisites

### System Requirements
- Backend API running (`make run` or `uvicorn app.main:app --reload`)
- Database initialized and migrated
- Test audio files available
- API access (authentication token)

### Test Data
- Sample lyrics (various genres, moods, themes)
- Reference audio files (for comparison)
- Test user accounts

---

## UAT Test Scenarios

### 1. Voice Enhancement Testing

#### Test Case 1.1: Basic Voice Enhancement
**Objective**: Validate that voice enhancement improves audio quality

**Steps**:
1. Generate vocals using TTS with a test voice profile
2. Apply voice enhancement via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/enhancement/voice" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "audio_path": "audio_files/test/vocals_raw.wav",
       "enable_neural_vocoder": true,
       "enable_prosody": true,
       "enable_auto_tune": false
     }'
   ```
3. Compare original vs enhanced audio
4. Verify quality metrics show improvement

**Expected Results**:
- Enhanced audio file created
- Quality metrics (MOS, PESQ, STOI) improved
- Audio sounds more natural and clear

**Acceptance Criteria**:
- ✅ MOS score improvement > 0.5 points
- ✅ Audio quality subjectively better
- ✅ Processing completes without errors

---

#### Test Case 1.2: Auto-Tune Enhancement
**Objective**: Validate auto-tune functionality

**Steps**:
1. Generate vocals with slight pitch issues
2. Apply auto-tune via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/enhancement/voice" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "audio_path": "audio_files/test/vocals.wav",
       "enable_auto_tune": true,
       "target_key": "C major"
     }'
   ```
3. Verify pitch correction applied correctly

**Expected Results**:
- Pitch corrected to target key
- Audio remains natural sounding
- No artifacts introduced

**Acceptance Criteria**:
- ✅ Pitch matches target key
- ✅ No audible artifacts
- ✅ Natural vocal quality maintained

---

### 2. Mixing Enhancement Testing

#### Test Case 2.1: Intelligent Frequency Balancing
**Objective**: Validate frequency balancing improves mix quality

**Steps**:
1. Generate vocals and music separately
2. Apply mixing enhancement via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/enhancement/mixing" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "vocals_path": "audio_files/test/vocals.wav",
       "music_path": "audio_files/test/music.wav",
       "genre": "pop",
       "enable_frequency_balancing": true,
       "enable_sidechain": true,
       "enable_stereo_imaging": true
     }'
   ```
3. Compare before/after mix
4. Verify frequency conflicts resolved

**Expected Results**:
- Vocals and music balanced properly
- No frequency masking
- Clear separation between elements

**Acceptance Criteria**:
- ✅ Vocals clearly audible
- ✅ Music doesn't overpower vocals
- ✅ Frequency conflicts resolved
- ✅ Overall mix quality improved

---

#### Test Case 2.2: Genre-Specific Mixing
**Objective**: Validate genre-specific mixing presets

**Steps**:
1. Test mixing with different genres (pop, rock, hip-hop, jazz)
2. Verify genre-specific EQ and effects applied
3. Compare results across genres

**Expected Results**:
- Each genre has appropriate mixing characteristics
- Genre-specific presets applied correctly
- Mixes match genre expectations

**Acceptance Criteria**:
- ✅ Genre-specific EQ applied
- ✅ Mix characteristics match genre
- ✅ Consistent quality across genres

---

### 3. Complete Song Enhancement Testing

#### Test Case 3.1: End-to-End Enhancement Pipeline
**Objective**: Validate complete enhancement workflow

**Steps**:
1. Generate a complete song (lyrics + vocals + music)
2. Apply complete enhancement via API:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/enhancement/complete" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "song_id": "SONG_UUID",
       "enhancement_config": {
         "enable_voice_enhancement": true,
         "enable_intelligent_mixing": true,
         "enable_memory_learning": true,
         "track_quality_metrics": true
       }
     }'
   ```
3. Verify all enhancements applied
4. Check quality metrics tracked

**Expected Results**:
- Voice enhancement applied
- Mixing enhancement applied
- Quality metrics calculated
- Enhanced song file created

**Acceptance Criteria**:
- ✅ All enhancements applied successfully
- ✅ Quality metrics tracked
- ✅ Enhanced song quality improved
- ✅ Processing completes in reasonable time

---

### 4. Performance Testing

#### Test Case 4.1: Processing Time
**Objective**: Validate processing times are acceptable

**Steps**:
1. Run performance benchmark script:
   ```bash
   python scripts/benchmark_performance.py \
     --voice audio_files/test/vocals.wav \
     --iterations 5 \
     --output reports/benchmark_voice.json
   ```
2. Verify processing times meet targets

**Expected Results**:
- Voice enhancement: < 30 seconds per minute of audio
- Mixing: < 10 seconds per minute of audio
- Complete pipeline: < 3 minutes for 3-minute song

**Acceptance Criteria**:
- ✅ Processing times within targets
- ✅ No memory leaks
- ✅ Consistent performance across iterations

---

#### Test Case 4.2: Concurrent Processing
**Objective**: Validate system handles concurrent requests

**Steps**:
1. Send multiple enhancement requests simultaneously
2. Monitor system resources
3. Verify all requests complete successfully

**Expected Results**:
- All requests processed successfully
- No resource exhaustion
- Reasonable response times maintained

**Acceptance Criteria**:
- ✅ Handles 5+ concurrent requests
- ✅ No crashes or errors
- ✅ Response times acceptable

---

### 5. User Experience Testing

#### Test Case 5.1: API Usability
**Objective**: Validate API is easy to use

**Steps**:
1. Test API endpoints with various configurations
2. Verify error messages are clear
3. Check response formats are consistent

**Expected Results**:
- API endpoints intuitive to use
- Clear error messages
- Consistent response formats

**Acceptance Criteria**:
- ✅ API documentation clear
- ✅ Error messages helpful
- ✅ Response formats consistent

---

#### Test Case 5.2: Quality Feedback Loop
**Objective**: Validate feedback collection and learning

**Steps**:
1. Generate multiple songs with different configurations
2. Provide feedback via feedback endpoints
3. Verify system learns from feedback
4. Check optimized configurations created

**Expected Results**:
- Feedback collected successfully
- System learns from feedback
- Optimized configurations created

**Acceptance Criteria**:
- ✅ Feedback stored correctly
- ✅ Quality metrics tracked over time
- ✅ Optimized configurations generated

---

## Test Execution Checklist

### Pre-Testing
- [ ] Backend API running and accessible
- [ ] Database initialized and migrated
- [ ] Test audio files prepared
- [ ] Authentication tokens obtained
- [ ] Test environment configured

### During Testing
- [ ] Execute all test cases systematically
- [ ] Document results and observations
- [ ] Capture screenshots/audio samples
- [ ] Note any issues or bugs
- [ ] Measure performance metrics

### Post-Testing
- [ ] Compile test results
- [ ] Generate quality validation reports
- [ ] Generate performance benchmark reports
- [ ] Document findings and recommendations
- [ ] Create bug reports for issues found

---

## Quality Validation

### Automated Validation
Use the quality validation script:

```bash
# Validate voice enhancement
python scripts/validate_quality_improvements.py \
  --voice audio_files/test/vocals_raw.wav audio_files/test/vocals_enhanced.wav \
  --output reports/voice_validation.json

# Validate mixing improvements
python scripts/validate_quality_improvements.py \
  --mixing audio_files/test/mixed_before.wav audio_files/test/mixed_after.wav \
  --genre pop \
  --output reports/mixing_validation.json
```

### Manual Validation
- Listen to before/after audio samples
- Compare quality subjectively
- Check for artifacts or issues
- Verify improvements are noticeable

---

## Performance Benchmarking

### Run Benchmarks
```bash
# Voice enhancement benchmark
python scripts/benchmark_performance.py \
  --voice audio_files/test/vocals.wav \
  --iterations 5 \
  --output reports/benchmark_voice.json

# Mixing benchmark
python scripts/benchmark_performance.py \
  --mixing audio_files/test/vocals.wav audio_files/test/music.wav \
  --iterations 5 \
  --output reports/benchmark_mixing.json
```

### Performance Targets
- **Voice Enhancement**: < 30s per minute of audio
- **Mixing**: < 10s per minute of audio
- **Complete Pipeline**: < 3 minutes for 3-minute song
- **Memory Usage**: < 2GB peak
- **API Response Time**: < 5s for enhancement requests

---

## Reporting

### Test Report Template
1. **Executive Summary**
   - Overall test results
   - Key findings
   - Recommendations

2. **Test Results**
   - Test case results
   - Pass/fail status
   - Issues found

3. **Quality Metrics**
   - Before/after comparisons
   - Improvement percentages
   - Validation results

4. **Performance Metrics**
   - Processing times
   - Memory usage
   - Throughput

5. **User Feedback**
   - Subjective quality assessments
   - User satisfaction scores
   - Feature requests

---

## Acceptance Criteria Summary

### Voice Enhancement
- ✅ MOS score improvement > 0.5 points
- ✅ Audio quality subjectively better
- ✅ Processing time < 30s per minute
- ✅ No artifacts introduced

### Mixing Enhancement
- ✅ Vocals clearly audible
- ✅ Frequency conflicts resolved
- ✅ Genre-specific presets work correctly
- ✅ Processing time < 10s per minute

### Complete Pipeline
- ✅ All enhancements applied successfully
- ✅ Quality metrics tracked
- ✅ Processing time < 3 minutes for 3-minute song
- ✅ Memory usage < 2GB peak

### System Reliability
- ✅ Handles 5+ concurrent requests
- ✅ No crashes or errors
- ✅ Error handling works correctly
- ✅ Feedback loop functional

---

## Next Steps

After UAT completion:
1. Review test results and feedback
2. Address identified issues
3. Optimize performance bottlenecks
4. Update documentation based on findings
5. Plan production deployment

---

## Support

For questions or issues during UAT:
- Check API documentation: `/docs` endpoint
- Review logs: `logs/` directory
- Contact development team
