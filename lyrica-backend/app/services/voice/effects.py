"""
Vocal effects service.

This module provides various vocal effects including reverb, echo,
compression, EQ, and other audio enhancements.
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range

from app.core.voice_config import get_voice_config


class VocalEffectsService:
    """Service for applying vocal effects."""

    def __init__(self):
        """Initialize vocal effects service."""
        self.config = get_voice_config()

    def add_reverb(
        self,
        audio_path: Path,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add reverb effect to vocals.

        Args:
            audio_path: Path to audio file
            room_size: Room size (0.0-1.0)
            damping: High-frequency damping (0.0-1.0)
            wet_level: Mix level of effect (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to audio with reverb

        Note:
            This is a simplified reverb using convolution.
            Professional reverb requires specialized libraries like pedalboard.
        """
        logger.info(f"Adding reverb: room={room_size}, damping={damping}, wet={wet_level}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Create simple reverb using convolution with exponential decay
        reverb_duration = 2.0  # seconds
        reverb_samples = int(sr * reverb_duration)

        # Create exponential decay impulse response
        decay_rate = -5 * (1 - room_size)  # Smaller room = faster decay
        t = np.linspace(0, reverb_duration, reverb_samples)
        impulse = np.exp(decay_rate * t) * np.random.randn(reverb_samples) * 0.1

        # Apply damping (low-pass filter)
        if damping > 0:
            from scipy.signal import butter, filtfilt

            cutoff = 5000 * (1 - damping)  # Hz
            b, a = butter(4, cutoff / (sr / 2), btype="low")
            impulse = filtfilt(b, a, impulse)

        # Convolve audio with impulse response
        y_reverb = np.convolve(y, impulse, mode="same")

        # Mix wet and dry signals
        y_mixed = (1 - wet_level) * y + wet_level * y_reverb

        # Normalize to prevent clipping
        y_mixed = y_mixed / np.max(np.abs(y_mixed))

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_reverb")

        # Save
        sf.write(str(output_path), y_mixed, sr)

        logger.success(f"Reverb applied: {output_path}")
        return output_path

    def add_echo(
        self,
        audio_path: Path,
        delay_ms: int = 500,
        decay: float = 0.3,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add echo effect to vocals.

        Args:
            audio_path: Path to audio file
            delay_ms: Echo delay in milliseconds
            decay: Echo decay factor (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to audio with echo
        """
        logger.info(f"Adding echo: delay={delay_ms}ms, decay={decay}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Calculate delay in samples
        delay_samples = int((delay_ms / 1000) * sr)

        # Create echo
        y_echo = np.zeros_like(y)
        y_echo[delay_samples:] = y[:-delay_samples] * decay

        # Mix original and echo
        y_mixed = y + y_echo

        # Normalize
        y_mixed = y_mixed / np.max(np.abs(y_mixed))

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_echo")

        # Save
        sf.write(str(output_path), y_mixed, sr)

        logger.success(f"Echo applied: {output_path}")
        return output_path

    def apply_compression(
        self,
        audio_path: Path,
        threshold: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 50.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply dynamic range compression to vocals.

        Args:
            audio_path: Path to audio file
            threshold: Compression threshold in dB
            ratio: Compression ratio (e.g., 4:1 = 4.0)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            output_path: Optional output path

        Returns:
            Path to compressed audio
        """
        logger.info(f"Applying compression: threshold={threshold}dB, ratio={ratio}:1")

        # Load with pydub
        audio = AudioSegment.from_file(str(audio_path))

        # Apply compression
        compressed = compress_dynamic_range(
            audio,
            threshold=threshold,
            ratio=ratio,
            attack=attack_ms,
            release=release_ms,
        )

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_compressed")

        # Save
        compressed.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Compression applied: {output_path}")
        return output_path

    def apply_eq(
        self,
        audio_path: Path,
        low_shelf_db: float = 0.0,
        mid_db: float = 0.0,
        high_shelf_db: float = 0.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply basic 3-band EQ to vocals.

        Args:
            audio_path: Path to audio file
            low_shelf_db: Low frequencies adjustment (dB)
            mid_db: Mid frequencies adjustment (dB)
            high_shelf_db: High frequencies adjustment (dB)
            output_path: Optional output path

        Returns:
            Path to EQ'd audio

        Note:
            This is a simplified EQ. Professional EQ requires specialized DSP.
        """
        logger.info(
            f"Applying EQ: low={low_shelf_db:+.1f}dB, "
            f"mid={mid_db:+.1f}dB, high={high_shelf_db:+.1f}dB"
        )

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Get STFT
        D = librosa.stft(y)

        # Frequency bands (simplified 3-band)
        freq_bins = D.shape[0]
        low_cutoff = int(freq_bins * 0.2)  # Up to 20%
        high_cutoff = int(freq_bins * 0.8)  # From 80%

        # Apply gain to frequency bands
        if low_shelf_db != 0:
            D[:low_cutoff] *= 10 ** (low_shelf_db / 20)

        if mid_db != 0:
            D[low_cutoff:high_cutoff] *= 10 ** (mid_db / 20)

        if high_shelf_db != 0:
            D[high_cutoff:] *= 10 ** (high_shelf_db / 20)

        # Inverse STFT
        y_eq = librosa.istft(D)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_eq")

        # Save
        sf.write(str(output_path), y_eq, sr)

        logger.success(f"EQ applied: {output_path}")
        return output_path

    def add_harmony(
        self,
        audio_path: Path,
        harmony_intervals: list[int],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add harmony vocals by pitch-shifting.

        Args:
            audio_path: Path to audio file
            harmony_intervals: List of intervals in semitones (e.g., [3, 7] for third and fifth)
            output_path: Optional output path

        Returns:
            Path to audio with harmonies

        Example:
            Add major third and perfect fifth: harmony_intervals=[4, 7]
        """
        logger.info(f"Adding harmonies: {harmony_intervals}")

        from pydub import AudioSegment

        # Load original
        original = AudioSegment.from_file(str(audio_path))

        # Generate harmonies
        for interval in harmony_intervals:
            # Create harmony track with pitch shift
            temp_path = audio_path.with_stem(f"{audio_path.stem}_harmony{interval}")
            self.shift_pitch(audio_path, interval, temp_path)

            # Load and mix
            harmony = AudioSegment.from_file(str(temp_path))
            # Reduce volume of harmony (typically -6dB)
            harmony = harmony - 6
            # Mix with original
            original = original.overlay(harmony)

            # Cleanup
            temp_path.unlink()

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_harmony")

        # Save
        original.export(str(output_path), format=audio_path.suffix[1:])

        logger.success(f"Harmonies added: {output_path}")
        return output_path

    def denoise(
        self,
        audio_path: Path,
        noise_reduction_strength: float = 0.5,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Reduce background noise from vocals.

        Args:
            audio_path: Path to audio file
            noise_reduction_strength: Strength of noise reduction (0.0-1.0)
            output_path: Optional output path

        Returns:
            Path to denoised audio

        Note:
            This is a basic spectral gating approach.
            Professional denoising requires specialized models.
        """
        logger.info(f"Denoising audio (strength={noise_reduction_strength})")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Get magnitude spectrogram
        D = librosa.stft(y)
        magnitude, phase = librosa.magphase(D)

        # Estimate noise floor (from quietest parts)
        noise_floor = np.percentile(magnitude, 10 * noise_reduction_strength)

        # Apply spectral gate
        mask = magnitude > (noise_floor * (1 + noise_reduction_strength))
        magnitude_cleaned = magnitude * mask

        # Reconstruct audio
        D_cleaned = magnitude_cleaned * phase
        y_cleaned = librosa.istft(D_cleaned)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_denoised")

        # Save
        sf.write(str(output_path), y_cleaned, sr)

        logger.success(f"Denoising applied: {output_path}")
        return output_path

    def shift_pitch(
        self,
        audio_path: Path,
        semitones: int,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Shift pitch of audio (used internally by harmony method).

        Args:
            audio_path: Path to audio file
            semitones: Number of semitones to shift (positive = higher)
            output_path: Optional output path

        Returns:
            Path to pitch-shifted audio
        """
        from app.services.voice import get_pitch_control

        pitch_service = get_pitch_control()
        return pitch_service.shift_pitch(
            audio_path=audio_path, semitones=semitones, output_path=output_path
        )

    def apply_effects(
        self,
        audio_path: Path,
        effects: dict,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply multiple vocal effects from a dictionary.

        Args:
            audio_path: Path to audio file
            effects: Dictionary of effects to apply, e.g.:
                {
                    "reverb": 0.3,
                    "echo": 0.15,
                    "delay": 0.15,  # alias for echo
                    "compression": 0.2,
                    "eq": {"low": 2.0, "mid": 0.0, "high": -1.0},
                    "harmony": [3, 7],  # intervals in semitones
                    "denoise": 0.5,
                }
            output_path: Optional output path

        Returns:
            Path to audio with effects applied

        Note:
            Effects are applied in order: reverb -> echo/delay -> compression ->
            EQ -> harmony -> denoise
        """
        logger.info(f"Applying vocal effects: {list(effects.keys())}")

        import tempfile

        # Use temporary file for intermediate processing
        with tempfile.NamedTemporaryFile(
            suffix=audio_path.suffix, delete=False, dir=audio_path.parent
        ) as tmp_file:
            temp_path = Path(tmp_file.name)

        try:
            current_path = audio_path
            effects_applied = False

            # Apply reverb
            if "reverb" in effects:
                reverb_level = effects["reverb"]
                current_path = self.add_reverb(
                    audio_path=current_path,
                    room_size=reverb_level,
                    wet_level=reverb_level,
                    output_path=temp_path,
                )
                effects_applied = True

            # Apply echo/delay
            if "echo" in effects or "delay" in effects:
                delay_level = effects.get("echo") or effects.get("delay", 0.15)
                delay_ms = int(delay_level * 1000)  # Convert to milliseconds
                current_path = self.add_echo(
                    audio_path=current_path,
                    delay_ms=delay_ms,
                    decay=delay_level,
                    output_path=temp_path,
                )
                effects_applied = True

            # Apply compression
            if "compression" in effects:
                compression_level = effects["compression"]
                threshold = -20.0 - (compression_level * 10)  # Lower threshold = more compression
                current_path = self.apply_compression(
                    audio_path=current_path,
                    threshold=threshold,
                    ratio=4.0,
                    output_path=temp_path,
                )
                effects_applied = True

            # Apply EQ
            if "eq" in effects:
                eq_params = effects["eq"]
                if isinstance(eq_params, dict):
                    current_path = self.apply_eq(
                        audio_path=current_path,
                        low_shelf_db=eq_params.get("low", 0.0),
                        mid_db=eq_params.get("mid", 0.0),
                        high_shelf_db=eq_params.get("high", 0.0),
                        output_path=temp_path,
                    )
                    effects_applied = True

            # Apply harmony
            if "harmony" in effects:
                harmony_intervals = effects["harmony"]
                if isinstance(harmony_intervals, list):
                    current_path = self.add_harmony(
                        audio_path=current_path,
                        harmony_intervals=harmony_intervals,
                        output_path=temp_path,
                    )
                    effects_applied = True

            # Apply denoise (usually last)
            if "denoise" in effects:
                denoise_strength = effects["denoise"]
                current_path = self.denoise(
                    audio_path=current_path,
                    noise_reduction_strength=denoise_strength,
                    output_path=temp_path,
                )
                effects_applied = True

            # Copy final result to output path
            if output_path:
                import shutil

                shutil.copy2(current_path, output_path)
                final_path = output_path
            else:
                final_path = current_path

            # Cleanup temp file if it was used
            if effects_applied and temp_path.exists() and temp_path != final_path:
                temp_path.unlink()

            if not effects_applied:
                logger.warning("No valid effects found in effects dictionary")
                if output_path:
                    import shutil

                    shutil.copy2(audio_path, output_path)
                    return output_path
                return audio_path

            logger.success(f"Vocal effects applied: {final_path}")
            return final_path

        except Exception as e:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            raise


# Singleton instance
_effects_service: Optional[VocalEffectsService] = None


def get_vocal_effects() -> VocalEffectsService:
    """Get or create vocal effects service instance."""
    global _effects_service
    if _effects_service is None:
        _effects_service = VocalEffectsService()
    return _effects_service
