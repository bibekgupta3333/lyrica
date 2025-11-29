"""
Chord progression generation service.

This module provides music theory-based chord progression generation
and analysis capabilities.
"""

import random
from typing import Optional

from loguru import logger

from app.core.music_config import (
    GENRE_CHORD_PROGRESSIONS,
    MusicGenre,
    MusicKey,
    get_genre_chord_progressions,
    get_music_config,
)


class ChordProgressionService:
    """Service for generating and analyzing chord progressions."""

    def __init__(self):
        """Initialize chord progression service."""
        self.config = get_music_config()

        # Chord quality mappings
        self.chord_qualities = {
            "": "major",
            "m": "minor",
            "7": "dominant7",
            "maj7": "major7",
            "m7": "minor7",
            "dim": "diminished",
            "aug": "augmented",
            "sus2": "sus2",
            "sus4": "sus4",
        }

        # Roman numeral to scale degree
        self.roman_numerals = {
            "I": 0,
            "bII": 1,
            "II": 2,
            "bIII": 3,
            "III": 4,
            "IV": 5,
            "bV": 6,
            "V": 7,
            "bVI": 8,
            "VI": 9,
            "bVII": 10,
            "VII": 11,
        }

    def generate_progression(
        self,
        key: MusicKey,
        genre: Optional[MusicGenre] = None,
        num_chords: int = 4,
    ) -> list[str]:
        """
        Generate chord progression for given key and genre.

        Args:
            key: Musical key
            genre: Optional music genre
            num_chords: Number of chords in progression

        Returns:
            List of chord names

        Example:
            ```python
            service = ChordProgressionService()
            chords = service.generate_progression(
                key=MusicKey.C_MAJOR,
                genre=MusicGenre.POP,
                num_chords=4
            )
            # Returns: ['C', 'G', 'Am', 'F']
            ```
        """
        logger.info(
            f"Generating {num_chords}-chord progression in {key.value}"
            + (f" ({genre.value})" if genre else "")
        )

        # Get genre-specific progressions
        if genre:
            progressions = get_genre_chord_progressions(genre)
        else:
            progressions = GENRE_CHORD_PROGRESSIONS[MusicGenre.POP]

        # Select random progression
        roman_progression = random.choice(progressions)

        # Trim or extend to desired length
        if len(roman_progression) > num_chords:
            roman_progression = roman_progression[:num_chords]
        elif len(roman_progression) < num_chords:
            # Repeat pattern
            while len(roman_progression) < num_chords:
                roman_progression.extend(roman_progression)
            roman_progression = roman_progression[:num_chords]

        # Convert to actual chords in the key
        chords = self._roman_to_chords(roman_progression, key)

        logger.success(f"Generated progression: {' - '.join(chords)}")
        return chords

    def _roman_to_chords(self, roman_numerals: list[str], key: MusicKey) -> list[str]:
        """
        Convert Roman numerals to chord names in given key.

        Args:
            roman_numerals: List of Roman numeral chords
            key: Musical key

        Returns:
            List of chord names
        """
        # Chromatic scale
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        # Get root note and scale type from key
        key_str = key.value
        is_minor = key_str.endswith("m")
        root_note = key_str.replace("m", "")

        # Find root note index
        root_idx = notes.index(root_note)

        chords = []

        for roman in roman_numerals:
            # Parse Roman numeral and quality
            base_roman = roman.replace("maj7", "").replace("m7", "").replace("7", "")
            quality = ""

            if "maj7" in roman:
                quality = "maj7"
            elif "m7" in roman:
                quality = "m7"
            elif "7" in roman:
                quality = "7"
            elif base_roman.lower() == base_roman:  # lowercase = minor
                quality = "m"

            # Get scale degree
            base_roman = base_roman.upper()
            if base_roman in self.roman_numerals:
                degree = self.roman_numerals[base_roman]
            else:
                # Handle lowercase (minor)
                degree = self.roman_numerals.get(base_roman, 0)

            # Calculate chord root
            chord_idx = (root_idx + degree) % 12
            chord_root = notes[chord_idx]

            # Build chord name
            chord_name = chord_root + quality
            chords.append(chord_name)

        return chords

    def generate_random_progression(
        self,
        key: MusicKey,
        num_chords: int = 4,
        allow_complex: bool = True,
    ) -> list[str]:
        """
        Generate random chord progression using music theory.

        Args:
            key: Musical key
            num_chords: Number of chords
            allow_complex: Allow 7th chords and extensions

        Returns:
            List of chord names
        """
        logger.info(f"Generating random progression in {key.value}")

        # Common chord progressions rules
        # Start with I, end with V or I
        progressions = []

        # Start with tonic
        progressions.append("I")

        for i in range(num_chords - 2):
            # Add common progressions
            choices = ["IV", "V", "vi", "ii", "iii"]
            if allow_complex:
                choices.extend(["IIm7", "V7", "Imaj7", "VImaj7"])
            progressions.append(random.choice(choices))

        # End with V (dominant) or I (tonic)
        progressions.append(random.choice(["V", "I"]))

        # Convert to chords
        chords = self._roman_to_chords(progressions, key)

        logger.success(f"Random progression: {' - '.join(chords)}")
        return chords

    def analyze_progression(self, chords: list[str]) -> dict:
        """
        Analyze a chord progression.

        Args:
            chords: List of chord names

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "num_chords": len(chords),
            "unique_chords": len(set(chords)),
            "chord_types": {},
            "complexity": "simple",
        }

        # Count chord types
        for chord in chords:
            # Determine chord type
            if "maj7" in chord or "7" in chord or "m7" in chord:
                chord_type = "extended"
            elif "m" in chord:
                chord_type = "minor"
            else:
                chord_type = "major"

            analysis["chord_types"][chord_type] = analysis["chord_types"].get(chord_type, 0) + 1

        # Determine complexity
        if any(k in ["extended", "dim", "aug"] for k in analysis["chord_types"]):
            analysis["complexity"] = "complex"
        elif len(set(chords)) > 5:
            analysis["complexity"] = "moderate"

        return analysis

    def transpose_progression(self, chords: list[str], semitones: int) -> list[str]:
        """
        Transpose chord progression by semitones.

        Args:
            chords: Original chord names
            semitones: Number of semitones to transpose (+/-)

        Returns:
            Transposed chord names
        """
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        transposed = []

        for chord in chords:
            # Extract root note and quality
            root = chord[0]
            if len(chord) > 1 and chord[1] in ["#", "b"]:
                root = chord[:2]
                quality = chord[2:]
            else:
                quality = chord[1:]

            # Handle flat notation
            if "b" in root:
                root_idx = (notes.index(root.replace("b", "")) - 1) % 12
            else:
                root_idx = notes.index(root)

            # Transpose
            new_idx = (root_idx + semitones) % 12
            new_root = notes[new_idx]

            transposed.append(new_root + quality)

        logger.info(f"Transposed {semitones:+d} semitones: {' - '.join(transposed)}")
        return transposed


# Singleton instance
_chord_service: Optional[ChordProgressionService] = None


def get_chord_service() -> ChordProgressionService:
    """Get or create chord progression service instance."""
    global _chord_service
    if _chord_service is None:
        _chord_service = ChordProgressionService()
    return _chord_service
