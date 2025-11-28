"""
Pitch and tempo control service for voice manipulation.

This module provides pitch shifting and tempo adjustment capabilities
using pyrubberband and librosa.
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger

from app.core.voice_config import get_voice_config


class PitchControlService:
    """Service for pitch and tempo manipulation."""

    def __init__(self):
        """Initialize pitch control service."""
        self.config = get_voice_config()

    def shift_pitch(
        self,
        audio_path: Path,
        semitones: float,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Shift pitch by semitones without changing tempo.

        Args:
            audio_path: Path to audio file
            semitones: Pitch shift in semitones (-12 to +12)
            output_path: Optional output path

        Returns:
            Path to pitch-shifted audio

        Example:
            Shift up one octave: semitones=+12
            Shift down one octave: semitones=-12
            Shift up a perfect fifth: semitones=+7
        """
        min_pitch, max_pitch = self.config.pitch_shift_semitones_range

        if not (min_pitch <= semitones <= max_pitch):
            raise ValueError(f"Pitch shift must be between {min_pitch} and {max_pitch} semitones")

        logger.info(f"Shifting pitch by {semitones:+.1f} semitones")

        try:
            # Try using pyrubberband first (higher quality)
            return self._shift_pitch_rubberband(audio_path, semitones, output_path)
        except ImportError:
            logger.warning("pyrubberband not available, falling back to librosa")
            return self._shift_pitch_librosa(audio_path, semitones, output_path)

    def _shift_pitch_rubberband(
        self, audio_path: Path, semitones: float, output_path: Optional[Path]
    ) -> Path:
        """Shift pitch using pyrubberband (highest quality)."""
        import pyrubberband as pyrb

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Shift pitch
        y_shifted = pyrb.pitch_shift(y, sr, semitones)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_pitch{semitones:+.0f}")

        # Save
        sf.write(str(output_path), y_shifted, sr)

        logger.success(f"Pitch shifted (rubberband): {output_path}")
        return output_path

    def _shift_pitch_librosa(
        self, audio_path: Path, semitones: float, output_path: Optional[Path]
    ) -> Path:
        """Shift pitch using librosa (fallback)."""
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Shift pitch
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_pitch{semitones:+.0f}")

        # Save
        sf.write(str(output_path), y_shifted, sr)

        logger.success(f"Pitch shifted (librosa): {output_path}")
        return output_path

    def change_tempo(
        self,
        audio_path: Path,
        tempo_factor: float,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Change tempo without changing pitch.

        Args:
            audio_path: Path to audio file
            tempo_factor: Tempo multiplier (0.5 = half speed, 2.0 = double speed)
            output_path: Optional output path

        Returns:
            Path to tempo-adjusted audio

        Example:
            Slow down by 50%: tempo_factor=0.5
            Speed up by 50%: tempo_factor=1.5
            Double speed: tempo_factor=2.0
        """
        min_tempo, max_tempo = self.config.tempo_range

        if not (min_tempo <= tempo_factor <= max_tempo):
            raise ValueError(f"Tempo factor must be between {min_tempo} and {max_tempo}")

        logger.info(f"Changing tempo by {tempo_factor}x")

        try:
            return self._change_tempo_rubberband(audio_path, tempo_factor, output_path)
        except ImportError:
            logger.warning("pyrubberband not available, falling back to librosa")
            return self._change_tempo_librosa(audio_path, tempo_factor, output_path)

    def _change_tempo_rubberband(
        self, audio_path: Path, tempo_factor: float, output_path: Optional[Path]
    ) -> Path:
        """Change tempo using pyrubberband."""
        import pyrubberband as pyrb

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Change tempo
        y_stretched = pyrb.time_stretch(y, sr, tempo_factor)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_tempo{tempo_factor:.1f}x")

        # Save
        sf.write(str(output_path), y_stretched, sr)

        logger.success(f"Tempo changed (rubberband): {output_path}")
        return output_path

    def _change_tempo_librosa(
        self, audio_path: Path, tempo_factor: float, output_path: Optional[Path]
    ) -> Path:
        """Change tempo using librosa."""
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Change tempo
        y_stretched = librosa.effects.time_stretch(y, rate=tempo_factor)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_tempo{tempo_factor:.1f}x")

        # Save
        sf.write(str(output_path), y_stretched, sr)

        logger.success(f"Tempo changed (librosa): {output_path}")
        return output_path

    def pitch_and_tempo(
        self,
        audio_path: Path,
        semitones: float,
        tempo_factor: float,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Adjust both pitch and tempo simultaneously.

        Args:
            audio_path: Path to audio file
            semitones: Pitch shift in semitones
            tempo_factor: Tempo multiplier
            output_path: Optional output path

        Returns:
            Path to adjusted audio
        """
        logger.info(f"Adjusting pitch ({semitones:+.1f} semitones) and tempo ({tempo_factor}x)")

        try:
            import pyrubberband as pyrb

            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Apply both transformations
            y_adjusted = pyrb.pitch_shift(y, sr, semitones)
            y_adjusted = pyrb.time_stretch(y_adjusted, sr, tempo_factor)

            # Generate output path
            if output_path is None:
                output_path = audio_path.with_stem(
                    f"{audio_path.stem}_p{semitones:+.0f}_t{tempo_factor:.1f}x"
                )

            # Save
            sf.write(str(output_path), y_adjusted, sr)

            logger.success(f"Pitch & tempo adjusted: {output_path}")
            return output_path

        except ImportError:
            logger.warning("Using librosa fallback for pitch & tempo")
            # Apply transformations separately
            temp_path = audio_path.with_stem(f"{audio_path.stem}_temp_pitch")
            temp_path = self._shift_pitch_librosa(audio_path, semitones, temp_path)
            final_path = self._change_tempo_librosa(temp_path, tempo_factor, output_path)
            temp_path.unlink(missing_ok=True)
            return final_path

    def auto_tune(
        self,
        audio_path: Path,
        target_key: str = "C",
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Auto-tune vocals to specified key (basic implementation).

        Args:
            audio_path: Path to audio file
            target_key: Target musical key
            output_path: Optional output path

        Returns:
            Path to auto-tuned audio

        Note:
            This is a simplified implementation. Professional auto-tune
            requires more sophisticated pitch detection and correction.
        """
        logger.info(f"Auto-tuning to key: {target_key}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Detect pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # This is a placeholder - full auto-tune requires complex pitch correction
        # For now, we'll just return the original
        logger.warning("Full auto-tune not implemented yet (placeholder)")

        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_autotuned")

        sf.write(str(output_path), y, sr)

        return output_path


# Singleton instance
_pitch_control_service: Optional[PitchControlService] = None


def get_pitch_control() -> PitchControlService:
    """Get or create pitch control service instance."""
    global _pitch_control_service
    if _pitch_control_service is None:
        _pitch_control_service = PitchControlService()
    return _pitch_control_service
