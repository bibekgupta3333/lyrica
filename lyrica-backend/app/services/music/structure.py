"""
Music structure analysis and generation service.

PHASE 3: This module provides song structure analysis and generation capabilities
including intro/verse/chorus/bridge/outro detection and dynamic changes.
"""

from pathlib import Path
from typing import Optional

import librosa
import numpy as np
from loguru import logger

from app.core.music_config import MusicGenre


class MusicStructureService:
    """
    PHASE 3: Service for analyzing and generating music structure.

    Provides:
    - Song structure analysis (intro/verse/chorus/bridge/outro)
    - Dynamic changes (build-ups, drops, transitions)
    - Genre-specific arrangements
    - Rhythm matching with lyrics
    """

    def __init__(self):
        """Initialize music structure service."""
        logger.success("MusicStructureService initialized")

    def analyze_structure(self, audio_path: Path, bpm: Optional[float] = None) -> dict:
        """
        Analyze song structure from audio.

        Detects intro, verse, chorus, bridge, and outro sections based on
        audio features like energy, tempo, and spectral characteristics.

        Args:
            audio_path: Path to audio file
            bpm: Optional BPM (if None, will be detected)

        Returns:
            Dictionary containing:
            - sections: List of section dictionaries with type, start_time, end_time
            - bpm: Detected BPM
            - structure: Overall structure string (e.g., "Intro-Verse-Chorus-Verse-Chorus-Outro")

        Example:
            ```python
            structure = service.analyze_structure(Path("song.wav"))
            print(structure["structure"])
            ```
        """
        logger.info(f"Analyzing song structure: {audio_path}")

        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None)

        # Detect BPM if not provided
        if bpm is None:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo)
            logger.info(f"Detected BPM: {bpm}")

        # Analyze energy over time
        frame_length = 2048
        hop_length = 512
        energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

        # Detect sections based on energy changes
        sections = self._detect_sections_from_energy(energy, sr, hop_length, bpm)

        # Classify sections (intro, verse, chorus, bridge, outro)
        classified_sections = self._classify_sections(sections, energy, sr, hop_length)

        # Generate structure string
        structure_string = "-".join([s["type"] for s in classified_sections])

        result = {
            "sections": classified_sections,
            "bpm": bpm,
            "structure": structure_string,
            "duration": len(y) / sr,
        }

        logger.success(f"Structure analyzed: {structure_string}")
        return result

    def _detect_sections_from_energy(
        self, energy: np.ndarray, sr: int, hop_length: int, bpm: float
    ) -> list[dict]:
        """Detect section boundaries from energy changes."""
        # Calculate time per frame
        time_per_frame = hop_length / sr

        # Find energy changes (potential section boundaries)
        energy_diff = np.diff(energy)
        threshold = np.std(energy_diff) * 1.5

        # Find significant changes
        change_points = []
        for i in range(1, len(energy_diff)):
            if abs(energy_diff[i]) > threshold:
                change_points.append(i * time_per_frame)

        # Ensure we have at least intro and outro
        if not change_points:
            duration = len(energy) * time_per_frame
            return [
                {"start_time": 0.0, "end_time": duration / 2},
                {"start_time": duration / 2, "end_time": duration},
            ]

        # Add start and end
        duration = len(energy) * time_per_frame
        if change_points[0] > 5.0:  # If first change is after 5 seconds, add intro
            change_points.insert(0, 0.0)
        if change_points[-1] < duration - 5.0:  # If last change is before end, add outro
            change_points.append(duration)

        # Create sections
        sections = []
        for i in range(len(change_points) - 1):
            sections.append(
                {
                    "start_time": change_points[i],
                    "end_time": change_points[i + 1],
                }
            )

        return sections

    def _classify_sections(
        self, sections: list[dict], energy: np.ndarray, sr: int, hop_length: int
    ) -> list[dict]:
        """Classify sections as intro, verse, chorus, bridge, or outro."""
        time_per_frame = hop_length / sr

        classified = []
        for i, section in enumerate(sections):
            start_frame = int(section["start_time"] / time_per_frame)
            end_frame = int(section["end_time"] / time_per_frame)
            section_energy = np.mean(energy[start_frame:end_frame])

            # Classify based on position and energy
            if i == 0:
                section_type = "Intro"
            elif i == len(sections) - 1:
                section_type = "Outro"
            elif section_energy > np.mean(energy) * 1.2:
                section_type = "Chorus"
            elif section_energy < np.mean(energy) * 0.8:
                section_type = "Bridge"
            else:
                section_type = "Verse"

            classified.append(
                {
                    "type": section_type,
                    "start_time": section["start_time"],
                    "end_time": section["end_time"],
                    "energy": float(section_energy),
                }
            )

        return classified

    def generate_structure_template(self, genre: MusicGenre, duration: int = 180) -> dict:
        """
        PHASE 3: Generate genre-specific song structure template.

        Creates a structure template with intro/verse/chorus/bridge/outro
        sections based on genre conventions.

        Args:
            genre: Music genre
            duration: Total duration in seconds

        Returns:
            Dictionary containing:
            - sections: List of section templates with type, duration, start_time
            - structure: Structure string
            - bpm: Typical BPM for genre

        Example:
            ```python
            template = service.generate_structure_template(
                MusicGenre.POP,
                duration=180
            )
            ```
        """
        logger.info(f"Generating {genre.value} structure template: {duration}s")

        # Genre-specific structure templates
        templates = {
            MusicGenre.POP: {
                "structure": [
                    "Intro",
                    "Verse",
                    "Chorus",
                    "Verse",
                    "Chorus",
                    "Bridge",
                    "Chorus",
                    "Outro",
                ],
                "durations": [0.08, 0.15, 0.20, 0.15, 0.20, 0.10, 0.20, 0.07],  # Percentages
                "bpm": 120,
            },
            MusicGenre.ROCK: {
                "structure": [
                    "Intro",
                    "Verse",
                    "Chorus",
                    "Verse",
                    "Chorus",
                    "Solo",
                    "Chorus",
                    "Outro",
                ],
                "durations": [0.10, 0.18, 0.22, 0.18, 0.22, 0.15, 0.22, 0.08],
                "bpm": 130,
            },
            MusicGenre.HIPHOP: {
                "structure": ["Intro", "Verse", "Hook", "Verse", "Hook", "Bridge", "Hook", "Outro"],
                "durations": [0.05, 0.20, 0.25, 0.20, 0.25, 0.10, 0.25, 0.05],
                "bpm": 90,
            },
            MusicGenre.ELECTRONIC: {
                "structure": [
                    "Intro",
                    "Build",
                    "Drop",
                    "Verse",
                    "Build",
                    "Drop",
                    "Breakdown",
                    "Outro",
                ],
                "durations": [0.10, 0.15, 0.25, 0.15, 0.15, 0.25, 0.10, 0.10],
                "bpm": 128,
            },
            MusicGenre.JAZZ: {
                "structure": ["Intro", "Head", "Solo", "Head", "Outro"],
                "durations": [0.10, 0.25, 0.40, 0.25, 0.10],
                "bpm": 100,
            },
        }

        # Get template for genre (default to POP)
        template = templates.get(genre, templates[MusicGenre.POP])

        # Generate sections
        sections = []
        current_time = 0.0
        for section_type, duration_ratio in zip(template["structure"], template["durations"]):
            section_duration = duration * duration_ratio
            sections.append(
                {
                    "type": section_type,
                    "start_time": current_time,
                    "end_time": current_time + section_duration,
                    "duration": section_duration,
                }
            )
            current_time += section_duration

        structure_string = "-".join(template["structure"])

        result = {
            "sections": sections,
            "structure": structure_string,
            "bpm": template["bpm"],
            "duration": duration,
        }

        logger.success(f"Structure template generated: {structure_string}")
        return result

    def add_dynamic_changes(
        self,
        audio_path: Path,
        structure: dict,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        PHASE 3: Add dynamic changes (build-ups, drops, transitions) based on structure.

        Applies volume and filtering changes to create dynamic interest
        throughout the song.

        Args:
            audio_path: Path to audio file
            structure: Structure dictionary from analyze_structure() or generate_structure_template()
            output_path: Optional output path

        Returns:
            Path to audio with dynamic changes

        Example:
            ```python
            structure = service.generate_structure_template(MusicGenre.POP, duration=180)
            dynamic = service.add_dynamic_changes(Path("song.wav"), structure)
            ```
        """
        logger.info("Adding dynamic changes based on structure")

        y, sr = librosa.load(str(audio_path), sr=None)
        duration = len(y) / sr

        # Create dynamic envelope
        envelope = np.ones(len(y))

        for section in structure["sections"]:
            section_type = section["type"]
            start_sample = int(section["start_time"] * sr)
            end_sample = int(min(section["end_time"] * sr, len(y)))

            if start_sample >= len(y):
                break

            # Apply dynamic changes based on section type
            if section_type == "Intro":
                # Fade in
                fade_samples = min(int(2 * sr), end_sample - start_sample)
                envelope[start_sample : start_sample + fade_samples] = np.linspace(
                    0.3, 1.0, fade_samples
                )
            elif section_type in ["Chorus", "Hook", "Drop"]:
                # Boost energy (volume increase)
                envelope[start_sample:end_sample] *= 1.1
            elif section_type == "Build":
                # Gradual build-up
                build_samples = end_sample - start_sample
                envelope[start_sample:end_sample] *= np.linspace(0.9, 1.2, build_samples)
            elif section_type == "Breakdown":
                # Reduce energy
                envelope[start_sample:end_sample] *= 0.85
            elif section_type == "Outro":
                # Fade out
                fade_samples = min(int(3 * sr), end_sample - start_sample)
                envelope[end_sample - fade_samples : end_sample] = np.linspace(
                    1.0, 0.0, fade_samples
                )

        # Apply envelope
        y_dynamic = y * envelope

        # Normalize
        max_val = np.max(np.abs(y_dynamic))
        if max_val > 0.95:
            y_dynamic = y_dynamic / max_val * 0.95

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_dynamic")

        # Save
        import soundfile as sf

        sf.write(str(output_path), y_dynamic, sr)

        logger.success(f"Dynamic changes applied: {output_path}")
        return output_path


def get_music_structure() -> MusicStructureService:
    """Get or create music structure service instance."""
    global _music_structure_service
    if "_music_structure_service" not in globals():
        _music_structure_service = MusicStructureService()
    return _music_structure_service
