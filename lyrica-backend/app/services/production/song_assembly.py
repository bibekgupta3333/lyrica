"""
Song assembly service for combining lyrics, voice, and music.

This module provides the complete song production pipeline, combining
generated lyrics, synthesized vocals, and AI-composed music into
a finished song.
"""

from pathlib import Path
from typing import Optional

from loguru import logger
from pydub import AudioSegment

from app.core.music_config import MusicGenre, MusicKey


class SongAssemblyService:
    """Service for assembling complete songs from components."""

    def __init__(self):
        """Initialize song assembly service."""
        self.output_path = Path("audio_files/songs")
        self.output_path.mkdir(parents=True, exist_ok=True)

    def assemble_song(
        self,
        vocals_path: Path,
        music_path: Path,
        output_path: Optional[Path] = None,
        vocals_volume_db: float = 0.0,
        music_volume_db: float = -3.0,
        crossfade_ms: int = 0,
        use_intelligent_mixing: bool = True,
        genre: Optional[MusicGenre] = None,
    ) -> Path:
        """
        Assemble complete song by mixing vocals with instrumental music.

        Args:
            vocals_path: Path to vocals audio file
            music_path: Path to instrumental music file
            output_path: Optional output path
            vocals_volume_db: Vocal track volume adjustment (dB)
            music_volume_db: Music track volume adjustment (dB, typically lower)
            crossfade_ms: Crossfade duration at boundaries (milliseconds)
            use_intelligent_mixing: Enable intelligent frequency balancing and sidechain compression
            genre: Optional genre for genre-specific EQ

        Returns:
            Path to assembled song

        Example:
            ```python
            service = SongAssemblyService()
            song = service.assemble_song(
                vocals_path=Path("vocals.wav"),
                music_path=Path("music.wav"),
                vocals_volume_db=0,
                music_volume_db=-5,  # Music quieter than vocals
                crossfade_ms=500,
                use_intelligent_mixing=True,
                genre=MusicGenre.POP
            )
            ```
        """
        logger.info(
            f"Assembling song: vocals + music (intelligent mixing: {use_intelligent_mixing})"
        )

        # Apply intelligent frequency balancing if enabled
        if use_intelligent_mixing:
            from app.services.production.frequency_balancing import (
                get_dynamic_eq,
                get_sidechain_compression,
            )

            dynamic_eq = get_dynamic_eq()
            sidechain = get_sidechain_compression()

            # Create temporary paths for processed audio
            import tempfile

            temp_dir = Path(tempfile.mkdtemp())

            try:
                # Apply dynamic EQ to vocals
                vocals_eq_path = temp_dir / "vocals_eq.wav"
                vocals_eq_path = dynamic_eq.apply_dynamic_eq(
                    vocals_path, genre=genre, output_path=vocals_eq_path
                )

                # Apply sidechain compression to music (music ducks for vocals)
                music_sidechain_path = temp_dir / "music_sidechain.wav"
                music_sidechain_path = sidechain.apply_sidechain_compression(
                    vocals_path, music_path, output_path=music_sidechain_path
                )

                # Apply stereo imaging and spatial effects separately
                from app.services.production.stereo_imaging import get_stereo_imaging

                stereo_imaging = get_stereo_imaging()
                vocals_spatial_path = temp_dir / "vocals_spatial.wav"
                music_spatial_path = temp_dir / "music_spatial.wav"

                vocals_spatial_path, music_spatial_path = (
                    stereo_imaging.process_vocals_and_music_separately(
                        vocals_path=vocals_eq_path,
                        music_path=music_sidechain_path,
                        vocals_width=1.0,  # Keep vocals centered
                        music_width=1.5,  # Widen music
                        vocals_reverb={
                            "room_size": 0.3,
                            "damping": 0.5,
                            "wet_level": 0.2,
                            "pre_delay_ms": 20.0,
                        },
                        music_reverb={
                            "room_size": 0.5,
                            "damping": 0.5,
                            "wet_level": 0.3,
                            "pre_delay_ms": 30.0,
                        },
                        output_vocals_path=vocals_spatial_path,
                        output_music_path=music_spatial_path,
                    )
                )

                # Use processed audio
                vocals_path = vocals_spatial_path
                music_path = music_spatial_path
            except Exception as e:
                logger.warning(f"Intelligent mixing failed, using basic mixing: {e}")
                # Fall back to basic mixing
            finally:
                # Cleanup temp directory
                import shutil

                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)

        # Load audio files
        vocals = AudioSegment.from_file(str(vocals_path))
        music = AudioSegment.from_file(str(music_path))

        # Adjust volumes
        if vocals_volume_db != 0:
            vocals = vocals + vocals_volume_db

        if music_volume_db != 0:
            music = music + music_volume_db

        # Synchronize lengths (match music to vocals length)
        if len(music) > len(vocals):
            # Trim music to vocals length
            music = music[: len(vocals)]
        elif len(music) < len(vocals):
            # Loop music to match vocals length
            repetitions = (len(vocals) // len(music)) + 1
            music = music * repetitions
            music = music[: len(vocals)]

        # Apply crossfade if specified
        if crossfade_ms > 0 and len(music) > crossfade_ms:
            # Crossfade at the beginning and end
            vocals = vocals.fade_in(crossfade_ms).fade_out(crossfade_ms)
            music = music.fade_in(crossfade_ms).fade_out(crossfade_ms)

        # Mix vocals and music
        mixed = vocals.overlay(music)

        # Generate output path
        if output_path is None:
            output_path = self.output_path / "assembled_song.wav"

        # Export
        mixed.export(str(output_path), format="wav")

        logger.success(f"Song assembled: {output_path}")
        return output_path

    def create_song_with_structure(
        self,
        sections: list[dict],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Create song with multi-section structure.

        Args:
            sections: List of section dictionaries with keys:
                - type: Section type (intro, verse, chorus, bridge, outro)
                - vocals_path: Path to vocals audio (optional)
                - music_path: Path to music audio
                - duration: Section duration in seconds
            output_path: Optional output path

        Returns:
            Path to assembled song

        Example:
            ```python
            sections = [
                {
                    "type": "intro",
                    "music_path": Path("intro.wav"),
                    "duration": 8
                },
                {
                    "type": "verse",
                    "vocals_path": Path("verse1_vocals.wav"),
                    "music_path": Path("verse_music.wav"),
                    "duration": 16
                },
                {
                    "type": "chorus",
                    "vocals_path": Path("chorus_vocals.wav"),
                    "music_path": Path("chorus_music.wav"),
                    "duration": 16
                }
            ]
            song = service.create_song_with_structure(sections)
            ```
        """
        logger.info(f"Creating song with {len(sections)} sections")

        combined_sections = []

        for i, section in enumerate(sections):
            section_type = section.get("type", "section")
            logger.info(f"Processing section {i + 1}: {section_type}")

            music_path = section["music_path"]
            vocals_path = section.get("vocals_path")

            # Load music
            music = AudioSegment.from_file(str(music_path))

            # Mix with vocals if present
            if vocals_path:
                vocals = AudioSegment.from_file(str(vocals_path))

                # Adjust volumes (vocals slightly louder than music)
                vocals = vocals + 0  # Keep at 0 dB
                music = music - 5  # Reduce music by 5 dB

                # Ensure same length
                if len(music) > len(vocals):
                    music = music[: len(vocals)]
                elif len(music) < len(vocals):
                    # Loop music
                    repetitions = (len(vocals) // len(music)) + 1
                    music = music * repetitions
                    music = music[: len(vocals)]

                # Mix
                section_audio = vocals.overlay(music)
            else:
                # Instrumental only
                section_audio = music

            combined_sections.append(section_audio)

        # Combine all sections with crossfade
        if len(combined_sections) == 1:
            final_song = combined_sections[0]
        else:
            final_song = combined_sections[0]
            for section in combined_sections[1:]:
                # Add 500ms crossfade between sections
                final_song = final_song.append(section, crossfade=500)

        # Generate output path
        if output_path is None:
            output_path = self.output_path / "structured_song.wav"

        # Export
        final_song.export(str(output_path), format="wav")

        logger.success(f"Structured song created: {output_path}")
        return output_path

    def sync_lyrics_to_music(
        self,
        lyrics_sections: list[dict],
        music_path: Path,
        output_vocals_path: Path,
    ) -> Path:
        """
        Synchronize lyrics sections with music timing.

        Args:
            lyrics_sections: List of dicts with 'text' and 'start_time' (seconds)
            music_path: Path to music audio
            output_vocals_path: Path to save synchronized vocals

        Returns:
            Path to synchronized vocals

        Example:
            ```python
            lyrics_sections = [
                {"text": "Verse 1 lyrics...", "start_time": 0, "duration": 16},
                {"text": "Chorus lyrics...", "start_time": 16, "duration": 16}
            ]
            vocals = service.sync_lyrics_to_music(
                lyrics_sections=lyrics_sections,
                music_path=Path("music.wav"),
                output_vocals_path=Path("synced_vocals.wav")
            )
            ```
        """
        logger.info(f"Synchronizing {len(lyrics_sections)} lyrics sections")

        from app.core.voice_config import get_voice_profile
        from app.services.voice import get_voice_synthesis

        voice_service = get_voice_synthesis()
        voice_profile = get_voice_profile("female_singer_1")

        # Load music to get duration
        music = AudioSegment.from_file(str(music_path))
        music_duration_ms = len(music)

        # Create silent base track
        vocals_track = AudioSegment.silent(duration=music_duration_ms)

        # Generate and place each section
        temp_dir = output_vocals_path.parent / "temp_vocals"
        temp_dir.mkdir(exist_ok=True)

        for i, section in enumerate(lyrics_sections):
            text = section["text"]
            start_time_ms = int(section["start_time"] * 1000)

            # Generate vocals for this section
            temp_vocal_path = temp_dir / f"section_{i}.wav"
            voice_service.synthesize_text(
                text=text, voice_profile=voice_profile, output_path=temp_vocal_path
            )

            # Load generated vocals
            section_vocals = AudioSegment.from_file(str(temp_vocal_path))

            # Overlay at specified time
            vocals_track = vocals_track.overlay(section_vocals, position=start_time_ms)

            # Cleanup temp file
            temp_vocal_path.unlink()

        # Cleanup temp directory
        temp_dir.rmdir()

        # Export synchronized vocals
        vocals_track.export(str(output_vocals_path), format="wav")

        logger.success(f"Lyrics synchronized: {output_vocals_path}")
        return output_vocals_path

    def create_song_preview(
        self, song_path: Path, preview_duration: int = 30, output_path: Optional[Path] = None
    ) -> Path:
        """
        Create preview/sample of song (typically 30 seconds).

        Args:
            song_path: Path to full song
            preview_duration: Preview duration in seconds
            output_path: Optional output path

        Returns:
            Path to preview file

        Example:
            Extract first 30 seconds as preview:
            ```python
            preview = service.create_song_preview(
                song_path=Path("full_song.wav"),
                preview_duration=30
            )
            ```
        """
        logger.info(f"Creating {preview_duration}s preview")

        # Load song
        song = AudioSegment.from_file(str(song_path))

        # Extract preview (first N seconds)
        preview_ms = preview_duration * 1000
        preview = song[:preview_ms]

        # Add fade out at the end
        preview = preview.fade_out(2000)  # 2 second fade out

        # Generate output path
        if output_path is None:
            output_path = song_path.with_stem(f"{song_path.stem}_preview")

        # Export
        preview.export(str(output_path), format="wav")

        logger.success(f"Preview created: {output_path}")
        return output_path

    def export_multi_format(
        self, song_path: Path, formats: list[str], output_dir: Optional[Path] = None
    ) -> dict[str, Path]:
        """
        Export song in multiple formats.

        Args:
            song_path: Path to song audio file
            formats: List of formats (e.g., ["mp3", "wav", "ogg"])
            output_dir: Optional output directory

        Returns:
            Dictionary mapping format to output path

        Example:
            ```python
            exported = service.export_multi_format(
                song_path=Path("song.wav"),
                formats=["mp3", "wav", "ogg", "flac"]
            )
            # Returns: {
            #     "mp3": Path("song.mp3"),
            #     "wav": Path("song.wav"),
            #     ...
            # }
            ```
        """
        logger.info(f"Exporting song in {len(formats)} formats")

        # Load song
        song = AudioSegment.from_file(str(song_path))

        # Output directory
        if output_dir is None:
            output_dir = song_path.parent

        exported_files = {}

        # Export each format
        for fmt in formats:
            output_path = output_dir / f"{song_path.stem}.{fmt}"

            # Set quality parameters based on format
            if fmt == "mp3":
                song.export(str(output_path), format="mp3", bitrate="320k")
            elif fmt == "ogg":
                song.export(str(output_path), format="ogg", parameters=["-q:a", "10"])
            elif fmt == "flac":
                song.export(str(output_path), format="flac")
            elif fmt == "m4a":
                song.export(str(output_path), format="ipod", codec="aac")
            else:
                song.export(str(output_path), format=fmt)

            exported_files[fmt] = output_path
            logger.info(f"Exported {fmt}: {output_path}")

        logger.success(f"Multi-format export complete")
        return exported_files


# Singleton instance
_song_assembly_service: Optional[SongAssemblyService] = None


def get_song_assembly() -> SongAssemblyService:
    """Get or create song assembly service instance."""
    global _song_assembly_service
    if _song_assembly_service is None:
        _song_assembly_service = SongAssemblyService()
    return _song_assembly_service
