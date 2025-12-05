"""
Stereo imaging and spatial effects service for music production.

This module provides stereo width measurement, enhancement, and spatial effects
(reverb, delay) for creating professional mixes with depth and width.
"""

import warnings
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger
from scipy import signal

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class StereoImagingService:
    """Service for stereo imaging and spatial effects."""

    def __init__(self):
        """Initialize stereo imaging service."""
        logger.success("StereoImagingService initialized")

    def measure_stereo_width(self, audio_path: Path) -> dict:
        """
        Measure stereo width of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing:
            - width_score: Stereo width score (0.0 = mono, 1.0 = full stereo)
            - correlation: Inter-channel correlation (-1.0 to 1.0)
            - side_level: Side signal level relative to mid
            - mid_level: Mid signal level
            - is_mono: Boolean indicating if audio is mono
            - stereo_balance: Left/right balance (-1.0 = all left, 1.0 = all right)
        """
        logger.info(f"Measuring stereo width: {audio_path}")

        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Handle mono audio
        if y.ndim == 1:
            logger.info("Audio is mono, converting to stereo for analysis")
            y = np.array([y, y])

        # Ensure stereo
        if y.shape[0] != 2:
            logger.warning("Audio has more than 2 channels, using first 2")
            y = y[:2, :]

        left = y[0, :]
        right = y[1, :]

        # Calculate mid and side signals
        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        # Calculate correlation
        correlation = np.corrcoef(left, right)[0, 1]
        if np.isnan(correlation):
            correlation = 1.0  # Perfect correlation if identical

        # Calculate RMS levels
        mid_rms = np.sqrt(np.mean(mid**2))
        side_rms = np.sqrt(np.mean(side**2))

        # Calculate side level relative to mid
        if mid_rms > 0:
            side_level = side_rms / mid_rms
        else:
            side_level = 0.0

        # Stereo width score (0.0 = mono, 1.0 = full stereo)
        # Based on correlation and side level
        width_score = (1.0 - abs(correlation)) * (1.0 + side_level) / 2.0
        width_score = np.clip(width_score, 0.0, 1.0)

        # Check if mono (very high correlation and low side level)
        is_mono = abs(correlation) > 0.99 and side_level < 0.01

        # Calculate stereo balance
        left_rms = np.sqrt(np.mean(left**2))
        right_rms = np.sqrt(np.mean(right**2))
        total_rms = left_rms + right_rms
        if total_rms > 0:
            stereo_balance = (right_rms - left_rms) / total_rms
        else:
            stereo_balance = 0.0

        result = {
            "width_score": float(width_score),
            "correlation": float(correlation),
            "side_level": float(side_level),
            "mid_level": float(mid_rms),
            "is_mono": bool(is_mono),
            "stereo_balance": float(stereo_balance),
        }

        logger.info(
            f"Stereo width: {width_score:.2f} "
            f"(correlation: {correlation:.2f}, side: {side_level:.2f})"
        )
        return result

    def enhance_stereo_width(
        self,
        audio_path: Path,
        width_factor: float = 1.5,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Enhance stereo width of an audio file.

        Args:
            audio_path: Path to audio file
            width_factor: Width enhancement factor (1.0 = no change, >1.0 = wider, <1.0 = narrower)
            output_path: Optional output path

        Returns:
            Path to enhanced audio file
        """
        logger.info(f"Enhancing stereo width: factor={width_factor}")

        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Handle mono audio
        if y.ndim == 1:
            logger.info("Audio is mono, converting to stereo")
            y = np.array([y, y])

        # Ensure stereo
        if y.shape[0] != 2:
            logger.warning("Audio has more than 2 channels, using first 2")
            y = y[:2, :]

        left = y[0, :]
        right = y[1, :]

        # Calculate mid and side signals
        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        # Enhance side signal
        side_enhanced = side * width_factor

        # Reconstruct left and right channels
        left_enhanced = mid + side_enhanced
        right_enhanced = mid - side_enhanced

        # Normalize to prevent clipping
        max_val = max(np.max(np.abs(left_enhanced)), np.max(np.abs(right_enhanced)))
        if max_val > 1.0:
            left_enhanced = left_enhanced / max_val
            right_enhanced = right_enhanced / max_val

        # Combine channels
        y_enhanced = np.array([left_enhanced, right_enhanced])

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_stereo_enhanced")

        # Save
        sf.write(str(output_path), y_enhanced.T, sr)
        logger.success(f"Stereo width enhanced: {output_path}")
        return output_path

    def add_spatial_reverb(
        self,
        audio_path: Path,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        pre_delay_ms: float = 20.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add spatial reverb effect for depth.

        Args:
            audio_path: Path to audio file
            room_size: Room size (0.0-1.0, larger = bigger room)
            damping: High-frequency damping (0.0-1.0, higher = more damping)
            wet_level: Mix level of reverb (0.0-1.0)
            pre_delay_ms: Pre-delay in milliseconds (adds depth)
            output_path: Optional output path

        Returns:
            Path to audio with reverb
        """
        logger.info(
            f"Adding spatial reverb: room={room_size}, "
            f"damping={damping}, wet={wet_level}, pre_delay={pre_delay_ms}ms"
        )

        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Handle mono
        if y.ndim == 1:
            y = np.array([y, y])

        # Ensure stereo
        if y.shape[0] != 2:
            y = y[:2, :]

        # Process each channel separately for stereo reverb
        left = y[0, :]
        right = y[1, :]

        # Create reverb impulse response
        reverb_duration = 2.0 + (room_size * 2.0)  # 2-4 seconds
        reverb_samples = int(sr * reverb_duration)

        # Pre-delay
        pre_delay_samples = int(sr * pre_delay_ms / 1000.0)

        # Create exponential decay impulse response
        t = np.linspace(0, reverb_duration, reverb_samples)
        decay_rate = -5 * (1 - room_size)
        impulse = np.exp(decay_rate * t) * np.random.randn(reverb_samples) * 0.1

        # Apply damping (low-pass filter)
        if damping > 0:
            cutoff = 5000 * (1 - damping)
            b, a = signal.butter(4, cutoff / (sr / 2), btype="low")
            impulse = signal.filtfilt(b, a, impulse)

        # Add pre-delay
        if pre_delay_samples > 0:
            impulse_delayed = np.zeros(len(impulse) + pre_delay_samples)
            impulse_delayed[pre_delay_samples:] = impulse
            impulse = impulse_delayed

        # Apply reverb to each channel
        left_reverb = np.convolve(left, impulse, mode="same")
        right_reverb = np.convolve(right, impulse, mode="same")

        # Mix wet and dry signals
        left_mixed = (1 - wet_level) * left + wet_level * left_reverb
        right_mixed = (1 - wet_level) * right + wet_level * right_reverb

        # Normalize to prevent clipping
        max_val = max(np.max(np.abs(left_mixed)), np.max(np.abs(right_mixed)))
        if max_val > 1.0:
            left_mixed = left_mixed / max_val
            right_mixed = right_mixed / max_val

        # Combine channels
        y_reverb = np.array([left_mixed, right_mixed])

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_spatial_reverb")

        # Save
        sf.write(str(output_path), y_reverb.T, sr)
        logger.success(f"Spatial reverb applied: {output_path}")
        return output_path

    def add_spatial_delay(
        self,
        audio_path: Path,
        delay_ms: float = 500.0,
        feedback: float = 0.3,
        wet_level: float = 0.4,
        ping_pong: bool = True,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add spatial delay effect (ping-pong delay for stereo).

        Args:
            audio_path: Path to audio file
            delay_ms: Delay time in milliseconds
            feedback: Feedback amount (0.0-1.0)
            wet_level: Mix level of delay (0.0-1.0)
            ping_pong: Enable ping-pong delay (left delays to right, right delays to left)
            output_path: Optional output path

        Returns:
            Path to audio with delay
        """
        logger.info(
            f"Adding spatial delay: delay={delay_ms}ms, "
            f"feedback={feedback}, ping_pong={ping_pong}"
        )

        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Handle mono
        if y.ndim == 1:
            y = np.array([y, y])

        # Ensure stereo
        if y.shape[0] != 2:
            y = y[:2, :]

        left = y[0, :]
        right = y[1, :]

        delay_samples = int((delay_ms / 1000.0) * sr)

        if ping_pong:
            # Ping-pong delay: left delays to right, right delays to left
            left_delayed = np.zeros_like(left)
            right_delayed = np.zeros_like(right)

            # Left channel delays to right
            if delay_samples < len(left):
                right_delayed[delay_samples:] = left[:-delay_samples] * wet_level

            # Right channel delays to left
            if delay_samples < len(right):
                left_delayed[delay_samples:] = right[:-delay_samples] * wet_level

            # Add feedback
            if feedback > 0:
                # Feedback from delayed signals
                for i in range(1, 4):  # Up to 3 feedback iterations
                    fb_delay = delay_samples * i
                    if fb_delay < len(left):
                        right_delayed[fb_delay:] += (
                            left_delayed[: len(right_delayed) - fb_delay] * feedback**i
                        )
                        left_delayed[fb_delay:] += (
                            right_delayed[: len(left_delayed) - fb_delay] * feedback**i
                        )

            # Mix original and delayed signals
            left_final = left + left_delayed
            right_final = right + right_delayed
        else:
            # Standard delay (same on both channels)
            left_delayed = np.zeros_like(left)
            right_delayed = np.zeros_like(right)

            if delay_samples < len(left):
                left_delayed[delay_samples:] = left[:-delay_samples] * wet_level
                right_delayed[delay_samples:] = right[:-delay_samples] * wet_level

            # Add feedback
            if feedback > 0:
                for i in range(1, 4):
                    fb_delay = delay_samples * i
                    if fb_delay < len(left):
                        left_delayed[fb_delay:] += (
                            left_delayed[: len(left_delayed) - fb_delay] * feedback**i
                        )
                        right_delayed[fb_delay:] += (
                            right_delayed[: len(right_delayed) - fb_delay] * feedback**i
                        )

            left_final = left + left_delayed
            right_final = right + right_delayed

        # Normalize to prevent clipping
        max_val = max(np.max(np.abs(left_final)), np.max(np.abs(right_final)))
        if max_val > 1.0:
            left_final = left_final / max_val
            right_final = right_final / max_val

        # Combine channels
        y_delayed = np.array([left_final, right_final])

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_spatial_delay")

        # Save
        sf.write(str(output_path), y_delayed.T, sr)
        logger.success(f"Spatial delay applied: {output_path}")
        return output_path

    def process_vocals_and_music_separately(
        self,
        vocals_path: Path,
        music_path: Path,
        vocals_width: float = 1.0,
        music_width: float = 1.5,
        vocals_reverb: Optional[dict] = None,
        music_reverb: Optional[dict] = None,
        vocals_delay: Optional[dict] = None,
        music_delay: Optional[dict] = None,
        output_vocals_path: Optional[Path] = None,
        output_music_path: Optional[Path] = None,
    ) -> tuple[Path, Path]:
        """
        Process vocals and music separately with different spatial effects.

        Args:
            vocals_path: Path to vocals audio file
            music_path: Path to music audio file
            vocals_width: Stereo width factor for vocals (1.0 = no change)
            music_width: Stereo width factor for music (1.5 = wider)
            vocals_reverb: Optional reverb settings for vocals
            music_reverb: Optional reverb settings for music
            vocals_delay: Optional delay settings for vocals
            music_delay: Optional delay settings for music
            output_vocals_path: Optional output path for processed vocals
            output_music_path: Optional output path for processed music

        Returns:
            Tuple of (processed_vocals_path, processed_music_path)
        """
        logger.info("Processing vocals and music separately with spatial effects")

        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Process vocals
            current_vocals = vocals_path
            temp_vocals = temp_dir / "vocals_temp.wav"

            # Apply stereo width to vocals
            if vocals_width != 1.0:
                current_vocals = self.enhance_stereo_width(
                    current_vocals, width_factor=vocals_width, output_path=temp_vocals
                )
                temp_vocals = current_vocals

            # Apply reverb to vocals
            if vocals_reverb:
                current_vocals = self.add_spatial_reverb(
                    current_vocals,
                    room_size=vocals_reverb.get("room_size", 0.3),
                    damping=vocals_reverb.get("damping", 0.5),
                    wet_level=vocals_reverb.get("wet_level", 0.2),
                    pre_delay_ms=vocals_reverb.get("pre_delay_ms", 20.0),
                    output_path=temp_vocals,
                )

            # Apply delay to vocals
            if vocals_delay:
                current_vocals = self.add_spatial_delay(
                    current_vocals,
                    delay_ms=vocals_delay.get("delay_ms", 300.0),
                    feedback=vocals_delay.get("feedback", 0.2),
                    wet_level=vocals_delay.get("wet_level", 0.3),
                    ping_pong=vocals_delay.get("ping_pong", True),
                    output_path=temp_vocals,
                )

            # Process music
            current_music = music_path
            temp_music = temp_dir / "music_temp.wav"

            # Apply stereo width to music
            if music_width != 1.0:
                current_music = self.enhance_stereo_width(
                    current_music, width_factor=music_width, output_path=temp_music
                )
                temp_music = current_music

            # Apply reverb to music
            if music_reverb:
                current_music = self.add_spatial_reverb(
                    current_music,
                    room_size=music_reverb.get("room_size", 0.5),
                    damping=music_reverb.get("damping", 0.5),
                    wet_level=music_reverb.get("wet_level", 0.3),
                    pre_delay_ms=music_reverb.get("pre_delay_ms", 30.0),
                    output_path=temp_music,
                )

            # Apply delay to music
            if music_delay:
                current_music = self.add_spatial_delay(
                    current_music,
                    delay_ms=music_delay.get("delay_ms", 500.0),
                    feedback=music_delay.get("feedback", 0.3),
                    wet_level=music_delay.get("wet_level", 0.4),
                    ping_pong=music_delay.get("ping_pong", True),
                    output_path=temp_music,
                )

            # Generate output paths
            if output_vocals_path is None:
                output_vocals_path = vocals_path.with_stem(f"{vocals_path.stem}_spatial_processed")
            if output_music_path is None:
                output_music_path = music_path.with_stem(f"{music_path.stem}_spatial_processed")

            # Copy to final output paths
            import shutil

            shutil.copy2(current_vocals, output_vocals_path)
            shutil.copy2(current_music, output_music_path)

            logger.success(
                f"Separate processing complete: vocals={output_vocals_path}, "
                f"music={output_music_path}"
            )
            return output_vocals_path, output_music_path

        finally:
            # Cleanup temp directory
            import shutil

            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)


# Singleton instance
_stereo_imaging_service: Optional[StereoImagingService] = None


def get_stereo_imaging() -> StereoImagingService:
    """Get or create stereo imaging service instance."""
    global _stereo_imaging_service
    if _stereo_imaging_service is None:
        _stereo_imaging_service = StereoImagingService()
    return _stereo_imaging_service
