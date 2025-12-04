"""
Music generation service using MusicGen/AudioCraft.

This module provides AI-powered music generation capabilities including
genre-based generation, melody creation, and instrumental composition.
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.music_config import (
    MusicGenre,
    MusicKey,
    MusicMood,
    get_genre_bpm_range,
    get_music_config,
)


class MusicGenerationService:
    """Service for AI-powered music generation."""

    def __init__(self):
        """Initialize music generation service."""
        self.config = get_music_config()
        self._musicgen_model = None
        self._audiocraft_available = self._check_audiocraft_availability()

        # Create directories
        self.config.generated_music_path.mkdir(parents=True, exist_ok=True)
        self.config.music_models_path.mkdir(parents=True, exist_ok=True)

    def _check_audiocraft_availability(self) -> bool:
        """
        Check if AudioCraft is available and functional.

        Note: AudioCraft requires Python 3.9-3.11 and specific dependency versions.
        On Python 3.12, it may have compatibility issues.
        """
        try:
            import audiocraft.models  # noqa: F401
            from audiocraft.models import MusicGen  # noqa: F401

            return True
        except ImportError as e:
            logger.info(
                f"AudioCraft not available: {e}. "
                "Using MIDI-based music generation with open-source libraries."
            )
            return False
        except Exception as e:
            logger.info(
                f"AudioCraft import failed: {e}. "
                "Using MIDI-based music generation with open-source libraries."
            )
            return False

    def _load_musicgen_model(self):
        """Load MusicGen model (lazy loading)."""
        if not self._audiocraft_available:
            raise ImportError("AudioCraft not installed. Install with: pip install audiocraft")

        if self._musicgen_model is None:
            try:
                from audiocraft.models import MusicGen

                logger.info(f"Loading MusicGen model: {self.config.model_name}")
                self._musicgen_model = MusicGen.get_pretrained(
                    self.config.model_name,
                    device="cuda" if self.config.use_gpu else "cpu",
                )
                logger.success("MusicGen model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load MusicGen model: {e}")
                raise

    def _generate_midi_music(
        self,
        genre: MusicGenre,
        key: Optional[MusicKey],
        bpm: int,
        duration: int,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music using MIDI synthesis (fallback when AudioCraft unavailable).

        Creates multi-track MIDI with drums, bass, chords, and melody, then synthesizes to audio.

        Args:
            genre: Music genre
            key: Optional musical key
            bpm: Tempo in beats per minute
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file
        """
        import random

        import numpy as np
        import pretty_midi
        import soundfile as sf

        logger.info(
            f"Generating MIDI-based {genre.value} music ({duration}s, {bpm} BPM)"
            + (f" in {key.value}" if key else "")
        )

        if output_path is None:
            output_path = (
                self.config.generated_music_path / f"midi_music_{genre.value}_{duration}s.wav"
            )

        # Create MIDI object
        midi = pretty_midi.PrettyMIDI()

        # Determine key
        if key is None:
            key = MusicKey.C_MAJOR  # Default key
        key_str = key.value
        is_minor = key_str.endswith("m")
        root_note = key_str.replace("m", "").replace("#", "")

        # Map root note to MIDI note number (C4 = 60)
        note_map = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
        root_midi = note_map.get(root_note, 60)
        if "#" in key_str:
            root_midi += 1

        # Get scale intervals
        if is_minor:
            scale_intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor
        else:
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]  # Major

        # Generate scale notes
        scale_notes = [
            (root_midi + interval) % 12 + (root_midi // 12) * 12 for interval in scale_intervals
        ]
        scale_notes.extend([n + 12 for n in scale_notes])  # Add octave above

        # Calculate timing
        beats_per_second = bpm / 60.0
        total_beats = duration * beats_per_second
        beat_duration = 1.0 / beats_per_second

        # Track 1: Drums (program 0 = Acoustic Grand, but we'll use percussion)
        # For drums, use channel 9 (percussion channel in General MIDI)
        drum_instrument = pretty_midi.Instrument(program=0, is_drum=True)

        # Simple drum pattern: kick on 1, snare on 2 and 4, hi-hat on off-beats
        for beat in range(int(total_beats)):
            beat_time = beat * beat_duration
            beat_pos = beat % 4

            # Kick drum (note 36) on beats 1 and 3
            if beat_pos == 0 or beat_pos == 2:
                note = pretty_midi.Note(
                    velocity=100, pitch=36, start=beat_time, end=beat_time + beat_duration * 0.5
                )
                drum_instrument.notes.append(note)

            # Snare (note 38) on beats 2 and 4
            if beat_pos == 1 or beat_pos == 3:
                note = pretty_midi.Note(
                    velocity=90, pitch=38, start=beat_time, end=beat_time + beat_duration * 0.5
                )
                drum_instrument.notes.append(note)

            # Hi-hat (note 42) on off-beats (every 0.5 beats)
            if beat % 2 == 0:  # On even beats, add hi-hat at 0.5 offset
                hihat_time = beat_time + beat_duration * 0.5
                if hihat_time < duration:
                    note = pretty_midi.Note(
                        velocity=70,
                        pitch=42,
                        start=hihat_time,
                        end=hihat_time + beat_duration * 0.25,
                    )
                    drum_instrument.notes.append(note)

        midi.instruments.append(drum_instrument)

        # Track 2: Bass (Electric Bass - program 33)
        bass_instrument = pretty_midi.Instrument(program=33)
        bass_notes = [n for n in scale_notes if n < root_midi + 24]  # Lower octave

        # Generate chord progression first (needed for bass line)
        from app.services.music.chords import ChordProgressionService

        chord_service = ChordProgressionService()
        measures = int(total_beats / 4)
        chord_progression = chord_service.generate_progression(
            key=key, genre=genre, num_chords=max(measures // 2, 1)
        )

        # Generate bass line following chord progression
        chord_duration = 4 * beat_duration  # One chord per measure

        for measure in range(measures):
            measure_start = measure * 4 * beat_duration
            # Get chord for this measure
            chord_idx = min(measure // 1, len(chord_progression) - 1)
            chord_name = chord_progression[chord_idx]

            # Get chord root note
            chord_root_note = self._chord_name_to_midi(chord_name, root_midi, is_minor)
            # Find closest bass note (one octave below)
            bass_note = min(bass_notes, key=lambda x: abs(x - (chord_root_note - 12)))

            # Play bass note on beats 1 and 3 (more musical)
            for beat_in_measure in [0, 2]:
                note_start = measure_start + beat_in_measure * beat_duration
                note = pretty_midi.Note(
                    velocity=85,
                    pitch=bass_note,
                    start=note_start,
                    end=note_start + beat_duration * 1.5,
                )
                bass_instrument.notes.append(note)

        midi.instruments.append(bass_instrument)

        # Track 3: Chords (Acoustic Guitar - program 25)
        chord_instrument = pretty_midi.Instrument(program=25)

        # Use the chord progression already generated for bass
        # Play chords
        chord_duration = 4 * beat_duration  # One chord per measure
        for i, chord_name in enumerate(chord_progression):
            chord_start = i * chord_duration
            if chord_start >= duration:
                break

            # Get chord root note
            chord_root_note = self._chord_name_to_midi(chord_name, root_midi, is_minor)

            # Determine if chord is minor
            is_minor_chord = "m" in chord_name.lower() and not chord_name.lower().startswith("maj")

            # Build triad: root, third, fifth
            if is_minor_chord:
                third = 3  # Minor third
            else:
                third = 4  # Major third

            chord_notes = [
                chord_root_note,  # Root
                chord_root_note + third,  # Third
                chord_root_note + 7,  # Fifth
            ]

            # Play chord (arpeggiated for more musical sound)
            for idx, note_pitch in enumerate(chord_notes):
                note_start = chord_start + (idx * beat_duration * 0.1)
                note = pretty_midi.Note(
                    velocity=70,
                    pitch=note_pitch,
                    start=note_start,
                    end=min(chord_start + chord_duration, duration),
                )
                chord_instrument.notes.append(note)

        midi.instruments.append(chord_instrument)

        # Track 4: Melody (Lead Synth - program 81)
        melody_instrument = pretty_midi.Instrument(program=81)
        melody_notes = [n for n in scale_notes if root_midi <= n < root_midi + 24]

        # Generate more musical melody following chord progression
        current_melody_note = melody_notes[len(melody_notes) // 2]  # Start in middle range
        notes_per_measure = 4

        for measure in range(measures):
            measure_start = measure * 4 * beat_duration
            # Get chord for this measure
            chord_idx = min(measure // 1, len(chord_progression) - 1)
            chord_name = chord_progression[chord_idx]
            chord_root_note = self._chord_name_to_midi(chord_name, root_midi, is_minor)

            # Prefer melody notes that are in the current chord
            chord_notes_in_scale = [
                n
                for n in melody_notes
                if (n % 12) in [(chord_root_note + i) % 12 for i in [0, 3, 4, 7]]
            ]
            if not chord_notes_in_scale:
                chord_notes_in_scale = melody_notes

            for note_idx in range(notes_per_measure):
                note_start = measure_start + note_idx * beat_duration
                if note_start >= duration:
                    break

                # 70% chance to use chord tone, 30% chance for any scale note
                if random.random() < 0.7 and chord_notes_in_scale:
                    melody_note = random.choice(chord_notes_in_scale)
                else:
                    melody_note = random.choice(melody_notes)

                # Slight preference for notes close to current note (smoother melody)
                if random.random() < 0.6:
                    nearby_notes = [n for n in melody_notes if abs(n - current_melody_note) <= 4]
                    if nearby_notes:
                        melody_note = random.choice(nearby_notes)

                current_melody_note = melody_note

                note = pretty_midi.Note(
                    velocity=75,
                    pitch=melody_note,
                    start=note_start,
                    end=note_start + beat_duration * 0.8,
                )
                melody_instrument.notes.append(note)

        midi.instruments.append(melody_instrument)

        # Synthesize MIDI to audio
        try:
            # Try fluidsynth first (better quality)
            audio = midi.fluidsynth(fs=self.config.sample_rate)
        except Exception as e:
            logger.warning(f"fluidsynth failed: {e}, using synthesizer fallback")
            # Fallback: synthesize using simple sine waves
            audio = self._synthesize_midi_simple(midi, duration, self.config.sample_rate)

        # Apply basic effects based on genre
        audio = self._apply_genre_effects(audio, genre, self.config.sample_rate)

        # Save audio
        sf.write(str(output_path), audio, self.config.sample_rate)

        logger.success(f"MIDI-based music generated: {output_path}")
        return output_path

    def _chord_name_to_midi(self, chord_name: str, root_midi: int, is_minor_key: bool) -> int:
        """
        Convert chord name to MIDI note number relative to root.

        Args:
            chord_name: Chord name (e.g., "C", "Am", "F", "G7")
            root_midi: MIDI note number of the key root
            is_minor_key: Whether the key is minor

        Returns:
            MIDI note number for the chord root
        """
        # Map note names to semitones from C
        note_map = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11,
        }

        # Extract base note name (handle sharps/flats)
        base_note = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in ["#", "b"]:
            base_note = chord_name[:2]

        # Get semitones from C for the chord root
        chord_semitones = note_map.get(base_note, 0)

        # Calculate MIDI note: root_midi is the key root, we need the chord root
        # If root_midi is C4 (60), and chord is D, we need D4 (62)
        # So: root_midi + (chord_semitones - root_semitones)
        root_semitones = root_midi % 12
        chord_root_midi = root_midi + ((chord_semitones - root_semitones) % 12)

        return chord_root_midi

    def _synthesize_midi_simple(self, midi, duration: float, sample_rate: int):
        """
        Simple MIDI synthesis using sine waves (fallback when fluidsynth unavailable).

        Includes basic drum synthesis using noise for percussion.
        """
        import numpy as np
        import pretty_midi

        audio = np.zeros(int(duration * sample_rate))

        # Drum frequencies (approximate)
        drum_freqs = {
            36: 60,  # Kick
            38: 200,  # Snare
            42: 800,  # Hi-hat
        }

        for instrument in midi.instruments:
            if instrument.is_drum:
                # Synthesize drums using filtered noise
                for note in instrument.notes:
                    start_sample = int(note.start * sample_rate)
                    end_sample = int(note.end * sample_rate)
                    duration_samples = end_sample - start_sample

                    if duration_samples > 0 and start_sample + duration_samples <= len(audio):
                        # Generate noise
                        noise = np.random.randn(duration_samples) * 0.5

                        # Filter based on drum type
                        freq = drum_freqs.get(note.pitch, 200)
                        if freq < 100:  # Kick - low pass
                            from scipy import signal

                            b, a = signal.butter(2, freq / (sample_rate / 2), "low")
                            noise = signal.filtfilt(b, a, noise)
                        elif freq < 300:  # Snare - band pass
                            from scipy import signal

                            b, a = signal.butter(
                                2, [100 / (sample_rate / 2), 500 / (sample_rate / 2)], "band"
                            )
                            noise = signal.filtfilt(b, a, noise)
                        else:  # Hi-hat - high pass
                            from scipy import signal

                            b, a = signal.butter(2, freq / (sample_rate / 2), "high")
                            noise = signal.filtfilt(b, a, noise)

                        # Apply envelope
                        envelope = np.linspace(0.1, 1.0, min(500, duration_samples // 5))
                        envelope = np.concatenate(
                            [
                                envelope,
                                np.ones(duration_samples - len(envelope) * 2),
                                envelope[::-1],
                            ]
                        )
                        noise *= envelope[:duration_samples]
                        noise *= note.velocity / 127.0

                        audio[start_sample : start_sample + duration_samples] += noise

            else:
                # Synthesize melodic instruments using sine waves
                for note in instrument.notes:
                    # Generate sine wave for note
                    frequency = pretty_midi.note_number_to_hz(note.pitch)
                    start_sample = int(note.start * sample_rate)
                    end_sample = int(note.end * sample_rate)
                    duration_samples = end_sample - start_sample

                    if duration_samples > 0:
                        t = np.linspace(0, note.end - note.start, duration_samples)
                        # Use richer waveform (sine + harmonics for better sound)
                        wave = np.sin(2 * np.pi * frequency * t)
                        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # Second harmonic
                        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)  # Third harmonic
                        wave /= 1.4  # Normalize

                        # Apply envelope
                        envelope_length = min(1000, duration_samples // 10)
                        envelope = np.linspace(0.1, 1.0, envelope_length)
                        envelope = np.concatenate(
                            [
                                envelope,
                                np.ones(duration_samples - len(envelope) * 2),
                                envelope[::-1],
                            ]
                        )
                        wave *= envelope[:duration_samples]
                        wave *= note.velocity / 127.0  # Velocity scaling

                        if start_sample + duration_samples <= len(audio):
                            audio[start_sample : start_sample + duration_samples] += wave

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.8  # 80% volume

        return audio

    def _apply_genre_effects(
        self, audio: "np.ndarray", genre: MusicGenre, sample_rate: int
    ) -> "np.ndarray":
        """Apply basic audio effects based on genre."""
        import numpy as np
        import scipy.signal

        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            audio = np.array(audio)

        # Apply EQ based on genre
        if genre == MusicGenre.ROCK:
            # Boost low and high frequencies
            b, a = scipy.signal.butter(
                3, [80 / (sample_rate / 2), 8000 / (sample_rate / 2)], "bandpass"
            )
            audio = scipy.signal.filtfilt(b, a, audio)
        elif genre == MusicGenre.ELECTRONIC:
            # Boost bass
            b, a = scipy.signal.butter(2, 200 / (sample_rate / 2), "low")
            bass_boost = scipy.signal.filtfilt(b, a, audio)
            audio = audio + bass_boost * 0.3
        elif genre == MusicGenre.JAZZ:
            # Slight high-frequency rolloff
            b, a = scipy.signal.butter(2, 5000 / (sample_rate / 2), "low")
            audio = scipy.signal.filtfilt(b, a, audio)

        # Apply light compression
        threshold = 0.7
        ratio = 3.0
        compressed = np.copy(audio)
        mask = np.abs(audio) > threshold
        compressed[mask] = threshold + (audio[mask] - threshold) / ratio
        audio = compressed * 0.9 + audio * 0.1  # Mix

        return audio

    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        output_path: Optional[Path] = None,
        temperature: float = 1.0,
    ) -> Path:
        """
        Generate music from text prompt.

        Args:
            prompt: Text description of desired music
            duration: Duration in seconds
            output_path: Optional output path
            temperature: Sampling temperature (0.5-2.0)

        Returns:
            Path to generated audio file

        Example:
            ```python
            service = MusicGenerationService()
            audio_path = service.generate_music(
                prompt="upbeat pop music with piano and drums",
                duration=30
            )
            ```
        """
        # If AudioCraft is not available, use MIDI-based generation
        if not self._audiocraft_available:
            if output_path is None:
                output_path = self.config.generated_music_path / f"music_{prompt[:20]}.wav"
            # Extract genre from prompt or use default
            genre = MusicGenre.POP
            for g in MusicGenre:
                if g.value in prompt.lower():
                    genre = g
                    break
            return self._generate_midi_music(
                genre=genre, key=None, bpm=120, duration=duration, output_path=output_path
            )

        self._load_musicgen_model()

        logger.info(f"Generating music: '{prompt}' ({duration}s)")

        try:
            # Set generation parameters
            self._musicgen_model.set_generation_params(
                duration=min(duration, self.config.max_generation_length),
                temperature=temperature,
            )

            # Generate music
            wav = self._musicgen_model.generate([prompt])

            # Save to file
            if output_path is None:
                output_path = self.config.generated_music_path / f"music_{prompt[:20]}.wav"

            import torchaudio

            torchaudio.save(
                str(output_path),
                wav[0].cpu(),
                sample_rate=self._musicgen_model.sample_rate,
            )

            logger.success(f"Music generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            raise

    def generate_by_genre(
        self,
        genre: MusicGenre,
        mood: Optional[MusicMood] = None,
        key: Optional[MusicKey] = None,
        bpm: Optional[int] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music for specific genre.

        Args:
            genre: Music genre
            mood: Optional mood/emotion
            key: Optional musical key
            bpm: Optional tempo (beats per minute)
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            audio_path = service.generate_by_genre(
                genre=MusicGenre.POP,
                mood=MusicMood.HAPPY,
                key=MusicKey.C_MAJOR,
                bpm=120,
                duration=30
            )
            ```
        """
        # Build prompt from parameters
        prompt_parts = [genre.value, "music"]

        if mood:
            prompt_parts.insert(0, mood.value)

        if key:
            prompt_parts.append(f"in {key.value}")

        if bpm:
            prompt_parts.append(f"at {bpm} BPM")
        else:
            # Use typical BPM for genre
            min_bpm, max_bpm = get_genre_bpm_range(genre)
            typical_bpm = (min_bpm + max_bpm) // 2
            prompt_parts.append(f"at {typical_bpm} BPM")

        prompt = " ".join(prompt_parts)

        logger.info(f"Generating {genre.value} music with prompt: '{prompt}'")

        # If AudioCraft is not available, use MIDI-based generation
        if not self._audiocraft_available:
            return self._generate_midi_music(
                genre=genre, key=key, bpm=bpm or 120, duration=duration, output_path=output_path
            )

        return self.generate_music(prompt=prompt, duration=duration, output_path=output_path)

    def generate_instrumental(
        self,
        instruments: list[str],
        genre: Optional[MusicGenre] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate instrumental music with specific instruments.

        Args:
            instruments: List of instruments (e.g., ["piano", "guitar", "drums"])
            genre: Optional genre
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            audio_path = service.generate_instrumental(
                instruments=["piano", "violin", "cello"],
                genre=MusicGenre.CLASSICAL,
                duration=60
            )
            ```
        """
        # Build prompt
        instruments_str = ", ".join(instruments)
        prompt_parts = [instruments_str]

        if genre:
            prompt_parts.append(genre.value)

        prompt_parts.append("instrumental music")
        prompt = " ".join(prompt_parts)

        logger.info(f"Generating instrumental with: {instruments_str}")

        return self.generate_music(prompt=prompt, duration=duration, output_path=output_path)

    def generate_with_melody(
        self,
        melody_audio_path: Path,
        genre: Optional[MusicGenre] = None,
        duration: int = 30,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music based on a melody audio file.

        Args:
            melody_audio_path: Path to melody audio file
            genre: Optional genre
            duration: Duration in seconds
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Note:
            This uses MusicGen's melody conditioning feature.
        """
        self._load_musicgen_model()

        logger.info(f"Generating music from melody: {melody_audio_path}")

        try:
            import torchaudio

            # Load melody audio
            melody, sr = torchaudio.load(str(melody_audio_path))

            # Build prompt
            prompt = f"{genre.value} music" if genre else "music"

            # Generate with melody conditioning
            self._musicgen_model.set_generation_params(duration=duration)
            wav = self._musicgen_model.generate_with_chroma(
                descriptions=[prompt], melody_wavs=melody[None], melody_sample_rate=sr
            )

            # Save to file
            if output_path is None:
                output_path = self.config.generated_music_path / f"music_melody_{duration}s.wav"

            torchaudio.save(
                str(output_path),
                wav[0].cpu(),
                sample_rate=self._musicgen_model.sample_rate,
            )

            logger.success(f"Music generated with melody: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Melody-based generation failed: {e}")
            raise

    def generate_structure(
        self,
        sections: list[tuple[str, int]],
        genre: MusicGenre,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate music with specific structure (intro, verse, chorus, etc.).

        Args:
            sections: List of (section_name, duration) tuples
            genre: Music genre
            output_path: Optional output path

        Returns:
            Path to generated audio file

        Example:
            ```python
            sections = [
                ("intro", 8),
                ("verse", 16),
                ("chorus", 16),
                ("verse", 16),
                ("chorus", 16),
                ("outro", 8)
            ]
            audio_path = service.generate_structure(
                sections=sections,
                genre=MusicGenre.POP
            )
            ```
        """
        from pydub import AudioSegment

        logger.info(f"Generating structured {genre.value} music")

        segments = []

        for section_name, section_duration in sections:
            logger.info(f"Generating {section_name} ({section_duration}s)")

            # Customize prompt based on section
            if section_name == "intro":
                prompt = f"intro for {genre.value} song, gentle build-up"
            elif section_name == "verse":
                prompt = f"{genre.value} verse, melodic and rhythmic"
            elif section_name == "chorus":
                prompt = f"{genre.value} chorus, energetic and catchy"
            elif section_name == "bridge":
                prompt = f"{genre.value} bridge, contrasting section"
            elif section_name == "outro":
                prompt = f"{genre.value} outro, fade out"
            else:
                prompt = f"{genre.value} {section_name}"

            # Generate section
            temp_path = self.config.generated_music_path / f"temp_{section_name}.wav"
            self.generate_music(prompt=prompt, duration=section_duration, output_path=temp_path)

            # Load and add to segments
            segment = AudioSegment.from_file(str(temp_path))
            segments.append(segment)

            # Cleanup temp file
            temp_path.unlink()

        # Combine all sections
        combined = sum(segments)

        # Save final audio
        if output_path is None:
            output_path = self.config.generated_music_path / f"music_structured_{genre.value}.wav"

        combined.export(str(output_path), format="wav")

        logger.success(f"Structured music generated: {output_path}")
        return output_path


# Singleton instance
_music_generation_service: Optional[MusicGenerationService] = None


def get_music_generation() -> MusicGenerationService:
    """Get or create music generation service instance."""
    global _music_generation_service
    if _music_generation_service is None:
        _music_generation_service = MusicGenerationService()
    return _music_generation_service
