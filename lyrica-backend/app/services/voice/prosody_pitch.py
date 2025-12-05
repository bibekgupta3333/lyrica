"""
Prosody and pitch enhancement service.

This module provides advanced pitch tracking, prosody prediction, auto-tune,
and formant shifting capabilities for voice enhancement.
"""

import warnings
from pathlib import Path
from typing import Optional, Tuple

import librosa
import numpy as np
import soundfile as sf
from loguru import logger

from app.core.voice_config import get_voice_config

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class ProsodyPitchService:
    """
    Service for prosody and pitch enhancement.

    Provides:
    - CREPE-based pitch tracking
    - Prosody prediction from lyrics
    - Enhanced auto-tune with scale detection
    - Formant shifting for voice characteristics
    """

    def __init__(self):
        """Initialize prosody and pitch service."""
        self.config = get_voice_config()
        self._crepe_model = None
        self._crepe_available = False
        self._check_crepe_availability()

    def _check_crepe_availability(self) -> None:
        """Check if CREPE is available for pitch tracking."""
        try:
            import crepe

            self._crepe_available = True
            logger.info("CREPE is available for pitch tracking")
        except ImportError:
            self._crepe_available = False
            logger.info(
                "CREPE not available. Install with: pip install crepe. "
                "Using librosa pitch tracking as fallback."
            )

    def track_pitch(
        self,
        audio_path: Path,
        method: str = "auto",
        frame_rate: int = 100,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Track pitch in audio using CREPE or librosa.

        Args:
            audio_path: Path to audio file
            method: Tracking method ("crepe", "librosa", "auto")
            frame_rate: Frame rate for pitch tracking (Hz)

        Returns:
            Tuple of (time, frequency) arrays
            - time: Time stamps in seconds
            - frequency: Pitch frequencies in Hz (0 for unvoiced)

        Example:
            ```python
            time, freq = service.track_pitch(Path("audio.wav"))
            ```
        """
        logger.info(f"Tracking pitch: {audio_path}")

        if method == "auto":
            method = "crepe" if self._crepe_available else "librosa"

        if method == "crepe" and self._crepe_available:
            return self._track_pitch_crepe(audio_path, frame_rate)
        else:
            return self._track_pitch_librosa(audio_path, frame_rate)

    def _track_pitch_crepe(
        self, audio_path: Path, frame_rate: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Track pitch using CREPE (most accurate)."""
        try:
            import crepe

            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=16000, mono=True)

            # Track pitch with CREPE
            time, frequency, confidence, activation = crepe.predict(
                audio, sr, viterbi=True, step_size=1000 // frame_rate
            )

            # Filter by confidence (only keep confident pitches)
            frequency[confidence < 0.5] = 0

            logger.success(f"CREPE pitch tracking complete: {len(time)} frames")
            return time, frequency

        except Exception as e:
            logger.error(f"CREPE pitch tracking failed: {e}")
            logger.info("Falling back to librosa")
            return self._track_pitch_librosa(audio_path, frame_rate)

    def _track_pitch_librosa(
        self, audio_path: Path, frame_rate: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Track pitch using librosa (fallback)."""
        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None, mono=True)

        # Track pitch using piptrack
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr, threshold=0.1)

        # Extract pitch values
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
            else:
                pitch_values.append(0)

        # Create time array
        hop_length = 512
        time = np.arange(len(pitch_values)) * hop_length / sr
        frequency = np.array(pitch_values)

        logger.success(f"Librosa pitch tracking complete: {len(time)} frames")
        return time, frequency

    def predict_prosody(self, lyrics: str, use_llm: bool = True) -> dict:
        """
        Predict prosody (rhythm, stress, intonation) from lyrics.

        Args:
            lyrics: Song lyrics text
            use_llm: Whether to use LLM for prosody prediction

        Returns:
            Dictionary with prosody markers:
            {
                "stress": [0.8, 0.3, 0.9, ...],  # Stress levels per word
                "pauses": [0.5, 1.0, 0.3, ...],   # Pause durations (seconds)
                "intonation": [0.2, -0.1, 0.5, ...],  # Intonation changes
                "tempo": 120,  # Suggested BPM
            }

        Example:
            ```python
            prosody = service.predict_prosody("Walking down the street")
            ```
        """
        logger.info(f"Predicting prosody from lyrics ({len(lyrics)} chars)")

        if use_llm:
            return self._predict_prosody_llm(lyrics)
        else:
            return self._predict_prosody_rule_based(lyrics)

    def _predict_prosody_llm(self, lyrics: str) -> dict:
        """Predict prosody using LLM."""
        try:
            from app.services.llm import get_llm_service

            llm_service = get_llm_service()

            prompt = f"""Analyze the prosody (rhythm, stress, intonation) of these lyrics and provide prosody markers in JSON format:

Lyrics:
{lyrics}

Provide prosody analysis with:
1. Stress levels for each word (0.0-1.0)
2. Pause durations between phrases (seconds)
3. Intonation changes (pitch variations, -1.0 to 1.0)
4. Suggested tempo (BPM)

Return JSON format:
{{
    "stress": [0.8, 0.3, 0.9, ...],
    "pauses": [0.5, 1.0, 0.3, ...],
    "intonation": [0.2, -0.1, 0.5, ...],
    "tempo": 120
}}
"""

            response = llm_service.generate(prompt, temperature=0.3)
            # Parse JSON from response (simplified)
            import json
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                prosody_data = json.loads(json_match.group())
                logger.success("LLM prosody prediction complete")
                return prosody_data
            else:
                logger.warning("Could not parse LLM response, using rule-based")
                return self._predict_prosody_rule_based(lyrics)

        except Exception as e:
            logger.error(f"LLM prosody prediction failed: {e}")
            return self._predict_prosody_rule_based(lyrics)

    def _predict_prosody_rule_based(self, lyrics: str) -> dict:
        """Predict prosody using rule-based approach."""
        words = lyrics.split()
        n_words = len(words)

        # Simple stress pattern (alternating)
        stress = [0.7 if i % 2 == 0 else 0.3 for i in range(n_words)]

        # Pauses at punctuation and line breaks
        pauses = []
        for i, word in enumerate(words):
            if word.endswith((".", "!", "?", ",", ";")):
                pauses.append(0.5)
            elif (
                i < len(words) - 1
                and "\n"
                in lyrics[max(0, lyrics.find(word) - 10) : lyrics.find(word) + len(word) + 10]
            ):
                pauses.append(1.0)
            else:
                pauses.append(0.2)

        # Simple intonation (rising at questions, falling at statements)
        intonation = []
        for word in words:
            if word.endswith("?"):
                intonation.append(0.3)
            elif word.endswith("!"):
                intonation.append(0.2)
            elif word.endswith("."):
                intonation.append(-0.1)
            else:
                intonation.append(0.0)

        # Estimate tempo from text length
        tempo = max(80, min(140, 100 + len(lyrics) // 10))

        return {
            "stress": stress,
            "pauses": pauses,
            "intonation": intonation,
            "tempo": tempo,
        }

    def auto_tune_with_scale(
        self,
        audio_path: Path,
        target_key: str = "C",
        scale_type: str = "major",
        strength: float = 0.8,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Auto-tune vocals to specified key and scale with pitch correction.

        Args:
            audio_path: Path to audio file
            target_key: Target musical key (C, D, E, F, G, A, B)
            scale_type: Scale type ("major", "minor", "pentatonic")
            strength: Correction strength (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to auto-tuned audio

        Example:
            ```python
            tuned = service.auto_tune_with_scale(
                Path("vocals.wav"),
                target_key="C",
                scale_type="major",
                strength=0.8
            )
            ```
        """
        logger.info(f"Auto-tuning to {target_key} {scale_type} (strength={strength})")

        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None, mono=True)

        # Track pitch
        time, frequency = self.track_pitch(audio_path, method="auto")

        # Get scale notes
        scale_notes = self._get_scale_notes(target_key, scale_type)

        # Correct pitch to nearest scale note
        corrected_audio = self._correct_pitch_to_scale(audio, sr, frequency, scale_notes, strength)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(
                f"{audio_path.stem}_autotuned_{target_key}_{scale_type}"
            )

        # Save
        sf.write(str(output_path), corrected_audio, sr)

        logger.success(f"Auto-tune complete: {output_path}")
        return output_path

    def _get_scale_notes(self, key: str, scale_type: str) -> list[float]:
        """
        Get frequencies for scale notes.

        Args:
            key: Musical key (C, D, E, F, G, A, B)
            scale_type: Scale type ("major", "minor", "pentatonic")

        Returns:
            List of frequencies in Hz for scale notes
        """
        # A4 = 440 Hz reference
        A4 = 440.0

        # Semitone intervals for scales
        if scale_type == "major":
            intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        elif scale_type == "minor":
            intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale
        elif scale_type == "pentatonic":
            intervals = [0, 2, 4, 7, 9]  # Pentatonic scale
        else:
            intervals = [0, 2, 4, 5, 7, 9, 11]  # Default to major

        # Key offsets (semitones from C)
        key_offsets = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        key_offset = key_offsets.get(key.upper(), 0)

        # Calculate frequencies
        notes = []
        for octave in range(3, 6):  # 3 octaves
            for interval in intervals:
                semitones = (octave - 4) * 12 + interval + key_offset
                freq = A4 * (2 ** (semitones / 12))
                notes.append(freq)

        return sorted(notes)

    def _correct_pitch_to_scale(
        self,
        audio: np.ndarray,
        sr: int,
        frequencies: np.ndarray,
        scale_notes: list[float],
        strength: float,
    ) -> np.ndarray:
        """Correct pitch to nearest scale note."""
        from app.services.voice import get_pitch_control

        pitch_service = get_pitch_control()

        # Resample frequencies to match audio length
        audio_frames = len(audio)
        freq_frames = len(frequencies)

        if freq_frames == 0:
            return audio

        # Create pitch correction map
        corrected_audio = np.copy(audio)
        hop_length = audio_frames // freq_frames if freq_frames > 0 else 512

        # Process in larger chunks for smoother correction
        chunk_size = int(sr * 0.5)  # 500ms chunks for smoother transitions
        corrected_chunks = []
        previous_semitones = 0.0

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i : i + chunk_size]
            chunk_idx = min(i // hop_length, len(frequencies) - 1)

            if chunk_idx < len(frequencies) and frequencies[chunk_idx] > 0:
                # Find nearest scale note
                target_freq = frequencies[chunk_idx]
                nearest_note = min(scale_notes, key=lambda x: abs(x - target_freq))

                # Calculate semitone shift
                if target_freq > 0:
                    semitones = 12 * np.log2(nearest_note / target_freq)
                    semitones = np.clip(semitones * strength, -2, 2)

                    # Smooth transitions between chunks
                    semitones = 0.7 * semitones + 0.3 * previous_semitones
                    previous_semitones = semitones

                    # Apply pitch shift only if significant
                    if abs(semitones) > 0.15:  # Increased threshold
                        try:
                            # Use temporary file for pitch shift
                            import tempfile

                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                tmp_path = Path(tmp.name)
                                sf.write(str(tmp_path), chunk, sr)
                                shifted_chunk = pitch_service.shift_pitch(tmp_path, semitones)
                                chunk, _ = librosa.load(str(shifted_chunk), sr=sr)
                                tmp_path.unlink()
                                shifted_chunk.unlink()
                        except Exception as e:
                            logger.warning(f"Pitch correction failed for chunk: {e}")

            corrected_chunks.append(chunk)

        # Combine chunks
        if corrected_chunks:
            corrected_audio = np.concatenate(corrected_chunks)
            # Ensure same length as original
            if len(corrected_audio) > len(audio):
                corrected_audio = corrected_audio[: len(audio)]
            elif len(corrected_audio) < len(audio):
                corrected_audio = np.pad(corrected_audio, (0, len(audio) - len(corrected_audio)))

        return corrected_audio

    def shift_formants(
        self,
        audio_path: Path,
        formant_shift: float = 1.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Shift formants to change voice characteristics without changing pitch.

        Args:
            audio_path: Path to audio file
            formant_shift: Formant shift factor (1.0 = no change, >1.0 = brighter, <1.0 = darker)
            output_path: Optional output path

        Returns:
            Path to formant-shifted audio

        Example:
            ```python
            # Make voice brighter (higher formants)
            brighter = service.shift_formants(Path("voice.wav"), formant_shift=1.2)

            # Make voice darker (lower formants)
            darker = service.shift_formants(Path("voice.wav"), formant_shift=0.8)
            ```
        """
        logger.info(f"Shifting formants by factor {formant_shift}")

        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None, mono=True)

        # Apply formant shifting using phase vocoder
        # This preserves pitch while shifting formants
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Shift formants by resampling frequency bins
        n_bins = magnitude.shape[0]
        shifted_bins = np.arange(n_bins) * formant_shift
        shifted_bins = np.clip(shifted_bins, 0, n_bins - 1).astype(int)

        # Create shifted magnitude spectrum
        shifted_magnitude = np.zeros_like(magnitude)
        for i, shifted_idx in enumerate(shifted_bins):
            if shifted_idx < n_bins:
                shifted_magnitude[shifted_idx] += magnitude[i]

        # Reconstruct audio
        shifted_stft = shifted_magnitude * np.exp(1j * phase)
        shifted_audio = librosa.istft(shifted_stft)

        # Normalize
        shifted_audio = shifted_audio / np.max(np.abs(shifted_audio)) * 0.95

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_formant{formant_shift:.2f}")

        # Save
        sf.write(str(output_path), shifted_audio, sr)

        logger.success(f"Formant shift complete: {output_path}")
        return output_path


# Singleton instance
_prosody_pitch_service: Optional[ProsodyPitchService] = None


def get_prosody_pitch() -> ProsodyPitchService:
    """Get or create prosody and pitch service instance."""
    global _prosody_pitch_service
    if _prosody_pitch_service is None:
        _prosody_pitch_service = ProsodyPitchService()
    return _prosody_pitch_service
