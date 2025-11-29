"""
Audio Enhancement Service.

Provides audio enhancement features:
- Noise reduction
- Dynamic range compression
- Stereo widening
- Audio enhancement algorithms
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger
from pydub import AudioSegment
from scipy import signal


class AudioEnhancementService:
    """Service for enhancing audio quality."""

    def __init__(self):
        """Initialize audio enhancement service."""
        logger.info("Audio enhancement service initialized")

    def reduce_noise(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        noise_reduction_strength: float = 0.5,
    ) -> Path:
        """
        Reduce background noise from audio.

        Args:
            audio_path: Input audio path
            output_path: Output audio path (defaults to input_denoised.wav)
            noise_reduction_strength: Strength (0.0-1.0)

        Returns:
            Path to denoised audio file
        """
        logger.info(f"Reducing noise: {audio_path} (strength: {noise_reduction_strength})")

        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_denoised{audio_path.suffix}"

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Apply spectral gating (simplified noise reduction)
            # This is a basic implementation - production would use more sophisticated methods
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Estimate noise floor from quietest frames
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)

            # Create mask based on signal-to-noise ratio
            snr = magnitude / (noise_floor + 1e-10)
            threshold = 1.0 + (noise_reduction_strength * 2.0)
            mask = (snr > threshold).astype(float)

            # Smooth mask to avoid artifacts
            mask = signal.medfilt2d(mask, kernel_size=(3, 3))

            # Apply mask
            magnitude_clean = magnitude * mask

            # Reconstruct signal
            stft_clean = magnitude_clean * np.exp(1j * phase)
            y_clean = librosa.istft(stft_clean)

            # Save cleaned audio
            sf.write(str(output_path), y_clean, sr)

            logger.success(f"Noise reduction complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error reducing noise: {e}")
            raise

    def compress_dynamic_range(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 100.0,
    ) -> Path:
        """
        Apply dynamic range compression.

        Args:
            audio_path: Input audio path
            output_path: Output path
            threshold_db: Compression threshold in dB
            ratio: Compression ratio (e.g., 4:1)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds

        Returns:
            Path to compressed audio
        """
        logger.info(f"Compressing dynamic range: {audio_path} (ratio: {ratio}:1)")

        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_compressed{audio_path.suffix}"

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Convert threshold from dB to linear
            threshold_linear = 10 ** (threshold_db / 20.0)

            # Calculate envelope
            hop_length = 512
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

            # Upsample RMS to match audio length
            rms_upsampled = np.interp(np.arange(len(y)), np.linspace(0, len(y), len(rms)), rms)

            # Apply compression
            gain = np.ones_like(rms_upsampled)
            above_threshold = rms_upsampled > threshold_linear

            # Calculate gain reduction for samples above threshold
            excess = rms_upsampled[above_threshold] / threshold_linear
            gain_reduction = 1.0 / (1.0 + (ratio - 1.0) * (excess - 1.0) / excess)
            gain[above_threshold] = gain_reduction

            # Smooth gain envelope (attack/release)
            attack_samples = int(sr * attack_ms / 1000.0)
            release_samples = int(sr * release_ms / 1000.0)

            gain_smooth = np.copy(gain)
            for i in range(1, len(gain)):
                if gain[i] < gain_smooth[i - 1]:  # Attack
                    alpha = 1.0 / attack_samples if attack_samples > 0 else 1.0
                else:  # Release
                    alpha = 1.0 / release_samples if release_samples > 0 else 1.0

                gain_smooth[i] = alpha * gain[i] + (1 - alpha) * gain_smooth[i - 1]

            # Apply compression
            y_compressed = y * gain_smooth

            # Normalize to prevent clipping
            max_val = np.max(np.abs(y_compressed))
            if max_val > 0.99:
                y_compressed = y_compressed * 0.99 / max_val

            # Save
            sf.write(str(output_path), y_compressed, sr)

            logger.success(f"Dynamic range compression complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error compressing dynamic range: {e}")
            raise

    def widen_stereo(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        width: float = 1.5,
    ) -> Path:
        """
        Apply stereo widening effect.

        Args:
            audio_path: Input audio path
            output_path: Output path
            width: Stereo width (1.0 = original, 2.0 = maximum width)

        Returns:
            Path to widened audio
        """
        logger.info(f"Widening stereo: {audio_path} (width: {width})")

        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_widened{audio_path.suffix}"

        try:
            # Load audio (force stereo)
            audio = AudioSegment.from_file(str(audio_path))

            # Convert to stereo if mono
            if audio.channels == 1:
                audio = audio.set_channels(2)

            # Get samples as numpy array
            samples = np.array(audio.get_array_of_samples())

            # Reshape to stereo (L, R)
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))

                # Extract left and right channels
                left = samples[:, 0].astype(float)
                right = samples[:, 1].astype(float)

                # Calculate mid and side signals
                mid = (left + right) / 2.0
                side = (left - right) / 2.0

                # Apply width adjustment
                side = side * width

                # Reconstruct left and right
                left_new = mid + side
                right_new = mid - side

                # Normalize to prevent clipping
                max_val = max(np.max(np.abs(left_new)), np.max(np.abs(right_new)))
                if max_val > 32767:
                    left_new = left_new * 32767 / max_val
                    right_new = right_new * 32767 / max_val

                # Combine channels
                samples_new = np.column_stack((left_new, right_new)).flatten()

                # Create new audio segment
                audio_widened = audio._spawn(samples_new.astype(np.int16).tobytes())

                # Export
                audio_widened.export(str(output_path), format=output_path.suffix[1:])
            else:
                # If not stereo, just copy
                audio.export(str(output_path), format=output_path.suffix[1:])

            logger.success(f"Stereo widening complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error widening stereo: {e}")
            raise

    def enhance_audio(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        reduce_noise: bool = True,
        compress: bool = True,
        widen_stereo: bool = False,
        normalize: bool = True,
    ) -> Path:
        """
        Apply multiple enhancement algorithms.

        Args:
            audio_path: Input audio
            output_path: Output path
            reduce_noise: Apply noise reduction
            compress: Apply dynamic range compression
            widen_stereo: Apply stereo widening
            normalize: Normalize loudness

        Returns:
            Path to enhanced audio
        """
        logger.info(f"Enhancing audio: {audio_path}")

        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_enhanced{audio_path.suffix}"

        temp_path = audio_path

        try:
            # Apply noise reduction
            if reduce_noise:
                temp_out = temp_path.parent / f"{temp_path.stem}_temp_nr{temp_path.suffix}"
                temp_path = self.reduce_noise(temp_path, temp_out, noise_reduction_strength=0.4)

            # Apply compression
            if compress:
                temp_out = temp_path.parent / f"{temp_path.stem}_temp_comp{temp_path.suffix}"
                temp_path = self.compress_dynamic_range(
                    temp_path, temp_out, threshold_db=-18.0, ratio=3.0
                )

            # Apply stereo widening
            if widen_stereo:
                temp_out = temp_path.parent / f"{temp_path.stem}_temp_wide{temp_path.suffix}"
                temp_path = self.widen_stereo(temp_path, temp_out, width=1.3)

            # Normalize loudness
            if normalize:
                audio = AudioSegment.from_file(str(temp_path))
                audio = audio.normalize()
                audio.export(str(output_path), format=output_path.suffix[1:])
            else:
                # Copy final temp to output
                if temp_path != output_path:
                    import shutil

                    shutil.copy(temp_path, output_path)

            # Clean up temp files
            if temp_path != audio_path and temp_path != output_path:
                if temp_path.exists():
                    temp_path.unlink()

            logger.success(f"Audio enhancement complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error enhancing audio: {e}")
            raise

    def normalize_loudness(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        target_lufs: float = -14.0,
    ) -> Path:
        """
        Normalize audio loudness to target LUFS.

        Args:
            audio_path: Input audio
            output_path: Output path
            target_lufs: Target loudness in LUFS

        Returns:
            Path to normalized audio
        """
        logger.info(f"Normalizing loudness to {target_lufs} LUFS: {audio_path}")

        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_normalized{audio_path.suffix}"

        try:
            # Load audio
            audio = AudioSegment.from_file(str(audio_path))

            # Calculate current loudness (simplified)
            samples = np.array(audio.get_array_of_samples()).astype(float)
            rms = np.sqrt(np.mean(samples**2))
            current_db = 20 * np.log10(rms / 32768.0) if rms > 0 else -100.0

            # Approximate LUFS (simplified)
            current_lufs = current_db - 3.0

            # Calculate gain adjustment
            gain_db = target_lufs - current_lufs

            # Apply gain
            audio_normalized = audio + gain_db

            # Export
            audio_normalized.export(str(output_path), format=output_path.suffix[1:])

            logger.success(f"Loudness normalization complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error normalizing loudness: {e}")
            raise


# Singleton instance
_audio_enhancement_service: Optional[AudioEnhancementService] = None


def get_audio_enhancement() -> AudioEnhancementService:
    """Get singleton audio enhancement service."""
    global _audio_enhancement_service
    if _audio_enhancement_service is None:
        _audio_enhancement_service = AudioEnhancementService()
    return _audio_enhancement_service
