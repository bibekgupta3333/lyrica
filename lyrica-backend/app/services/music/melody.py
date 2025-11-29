"""
Melody generation service.

This module provides melody generation capabilities using MIDI
and music theory principles.
"""

import random
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.music_config import MusicGenre, MusicKey, get_music_config


class MelodyGenerationService:
    """Service for generating melodies."""

    def __init__(self):
        """Initialize melody generation service."""
        self.config = get_music_config()

        # Major scale intervals (semitones from root)
        self.major_scale = [0, 2, 4, 5, 7, 9, 11]

        # Minor scale intervals
        self.minor_scale = [0, 2, 3, 5, 7, 8, 10]

        # Pentatonic major
        self.pentatonic_major = [0, 2, 4, 7, 9]

        # Pentatonic minor
        self.pentatonic_minor = [0, 3, 5, 7, 10]

    def generate_melody(
        self,
        key: MusicKey,
        num_notes: int = 16,
        duration_seconds: int = 8,
        genre: Optional[MusicGenre] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate MIDI melody file.

        Args:
            key: Musical key
            num_notes: Number of notes in melody
            duration_seconds: Total duration in seconds
            genre: Optional genre for style
            output_path: Optional output path

        Returns:
            Path to generated MIDI file

        Example:
            ```python
            service = MelodyGenerationService()
            midi_path = service.generate_melody(
                key=MusicKey.C_MAJOR,
                num_notes=16,
                duration_seconds=8,
                genre=MusicGenre.POP
            )
            ```
        """
        import pretty_midi

        logger.info(
            f"Generating melody: {num_notes} notes in {key.value}"
            + (f" ({genre.value})" if genre else "")
        )

        # Create MIDI object
        midi = pretty_midi.PrettyMIDI()

        # Create instrument
        instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

        # Get scale notes
        scale = self._get_scale(key)

        # Generate notes
        current_time = 0.0
        note_duration = duration_seconds / num_notes

        min_note, max_note = self.config.melody_note_range
        current_note = random.randint(min_note, max_note)

        for i in range(num_notes):
            # Choose note from scale
            scale_degree = random.choice(scale)

            # Calculate MIDI note number
            octave = current_note // 12
            note_in_scale = (scale_degree + (octave * 12)) % 128

            # Keep within range
            if note_in_scale < min_note:
                note_in_scale += 12
            elif note_in_scale > max_note:
                note_in_scale -= 12

            # Create note
            velocity = random.randint(80, 120)  # Dynamics
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=note_in_scale,
                start=current_time,
                end=current_time + note_duration,
            )

            instrument.notes.append(note)

            # Move to next note (melodic contour)
            step = random.choice([-2, -1, 0, 1, 2])  # Small melodic intervals
            current_note = max(min_note, min(max_note, current_note + step))

            current_time += note_duration

        # Add instrument to MIDI
        midi.instruments.append(instrument)

        # Save MIDI file
        if output_path is None:
            output_path = self.config.generated_music_path / f"melody_{key.value}.mid"

        midi.write(str(output_path))

        logger.success(f"Melody generated: {output_path}")
        return output_path

    def generate_pentatonic_melody(
        self,
        key: MusicKey,
        num_notes: int = 16,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate pentatonic melody (easier, more consonant).

        Args:
            key: Musical key
            num_notes: Number of notes
            output_path: Optional output path

        Returns:
            Path to MIDI file
        """
        import pretty_midi

        logger.info(f"Generating pentatonic melody in {key.value}")

        is_minor = "m" in key.value
        scale = self.pentatonic_minor if is_minor else self.pentatonic_major

        # Create MIDI
        midi = pretty_midi.PrettyMIDI()
        instrument = pretty_midi.Instrument(program=0)

        current_time = 0.0
        note_duration = 0.5  # seconds

        min_note, max_note = self.config.melody_note_range
        current_note = 60  # Middle C

        for i in range(num_notes):
            scale_degree = random.choice(scale)
            note_in_scale = current_note + scale_degree

            # Keep in range
            while note_in_scale < min_note:
                note_in_scale += 12
            while note_in_scale > max_note:
                note_in_scale -= 12

            velocity = random.randint(70, 110)
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=note_in_scale,
                start=current_time,
                end=current_time + note_duration,
            )

            instrument.notes.append(note)
            current_time += note_duration

            # Melodic movement
            current_note += random.choice([-12, -7, -5, 0, 5, 7, 12])
            current_note = max(min_note, min(max_note, current_note))

        midi.instruments.append(instrument)

        if output_path is None:
            output_path = self.config.generated_music_path / f"melody_pentatonic_{key.value}.mid"

        midi.write(str(output_path))

        logger.success(f"Pentatonic melody generated: {output_path}")
        return output_path

    def midi_to_audio(self, midi_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert MIDI to audio (WAV).

        Args:
            midi_path: Path to MIDI file
            output_path: Optional output audio path

        Returns:
            Path to audio file
        """
        import pretty_midi
        import soundfile as sf

        logger.info(f"Converting MIDI to audio: {midi_path}")

        # Load MIDI
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))

        # Synthesize audio
        audio = midi_data.fluidsynth(fs=self.config.sample_rate)

        # Save audio
        if output_path is None:
            output_path = midi_path.with_suffix(".wav")

        sf.write(str(output_path), audio, self.config.sample_rate)

        logger.success(f"MIDI converted to audio: {output_path}")
        return output_path

    def _get_scale(self, key: MusicKey) -> list[int]:
        """
        Get scale intervals for given key.

        Args:
            key: Musical key

        Returns:
            List of semitone intervals from root
        """
        key_str = key.value
        is_minor = key_str.endswith("m")

        return self.minor_scale if is_minor else self.major_scale


# Singleton instance
_melody_service: Optional[MelodyGenerationService] = None


def get_melody_service() -> MelodyGenerationService:
    """Get or create melody generation service instance."""
    global _melody_service
    if _melody_service is None:
        _melody_service = MelodyGenerationService()
    return _melody_service
