"""
Intelligent frequency balancing service for music mixing.

This module provides frequency analysis, dynamic EQ, and sidechain compression
for intelligent mixing of vocals and music.
"""

import warnings
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
import soundfile as sf
from loguru import logger
from scipy import signal

from app.core.music_config import MusicGenre

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class FrequencyAnalysisService:
    """Service for analyzing frequency content of audio."""

    def __init__(self):
        """Initialize frequency analysis service."""
        logger.success("FrequencyAnalysisService initialized")

    def analyze_frequency_content(self, audio_path: Path, sr: Optional[int] = None) -> dict:
        """
        Analyze frequency content of an audio file.

        Args:
            audio_path: Path to audio file
            sr: Optional target sample rate (default: original)

        Returns:
            Dictionary containing frequency analysis:
            - spectral_centroid: Average frequency (Hz)
            - spectral_rolloff: Frequency below which 85% of energy is (Hz)
            - spectral_bandwidth: Bandwidth around spectral centroid (Hz)
            - zero_crossing_rate: Rate of sign changes
            - mfcc: Mel-frequency cepstral coefficients (13 features)
            - frequency_bands: Energy in frequency bands (sub-bass, bass, low-mid, mid, high-mid, treble)
            - peak_frequencies: Dominant frequencies (Hz)
            - energy_distribution: Energy distribution across frequency spectrum
        """
        logger.info(f"Analyzing frequency content: {audio_path}")

        y, original_sr = librosa.load(str(audio_path), sr=sr)

        if sr is None:
            sr = original_sr

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]

        # MFCC features (13 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Frequency band analysis
        frequency_bands = self._analyze_frequency_bands(y, sr)

        # Peak frequencies
        peak_frequencies = self._find_peak_frequencies(y, sr)

        # Energy distribution
        energy_distribution = self._calculate_energy_distribution(y, sr)

        analysis = {
            "spectral_centroid": float(np.mean(spectral_centroid)),
            "spectral_rolloff": float(np.mean(spectral_rolloff)),
            "spectral_bandwidth": float(np.mean(spectral_bandwidth)),
            "zero_crossing_rate": float(np.mean(zero_crossing_rate)),
            "mfcc": mfcc.mean(axis=1).tolist(),
            "frequency_bands": frequency_bands,
            "peak_frequencies": peak_frequencies,
            "energy_distribution": energy_distribution,
            "sample_rate": sr,
            "duration": len(y) / sr,
        }

        logger.success(f"Frequency analysis complete: {len(peak_frequencies)} peaks found")
        return analysis

    def _analyze_frequency_bands(self, y: np.ndarray, sr: int) -> dict:
        """
        Analyze energy in different frequency bands.

        Frequency bands:
        - Sub-bass: 20-60 Hz
        - Bass: 60-250 Hz
        - Low-mid: 250-500 Hz
        - Mid: 500-2000 Hz
        - High-mid: 2000-4000 Hz
        - Treble: 4000-20000 Hz
        """
        # Compute STFT
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        frequencies = librosa.fft_frequencies(sr=sr)

        # Define frequency bands
        bands = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mid": (250, 500),
            "mid": (500, 2000),
            "high_mid": (2000, 4000),
            "treble": (4000, sr // 2),
        }

        band_energies = {}
        for band_name, (fmin, fmax) in bands.items():
            # Find frequency indices
            freq_mask = (frequencies >= fmin) & (frequencies <= fmax)
            if np.any(freq_mask):
                band_energy = np.mean(magnitude[freq_mask, :])
                band_energies[band_name] = float(band_energy)
            else:
                band_energies[band_name] = 0.0

        # Normalize to percentage
        total_energy = sum(band_energies.values())
        if total_energy > 0:
            band_energies = {k: (v / total_energy) * 100 for k, v in band_energies.items()}

        return band_energies

    def _find_peak_frequencies(self, y: np.ndarray, sr: int, n_peaks: int = 10) -> list[float]:
        """Find dominant frequencies in the audio."""
        # Compute power spectrum
        fft = np.fft.fft(y)
        power_spectrum = np.abs(fft) ** 2
        frequencies = np.fft.fftfreq(len(y), 1 / sr)

        # Only consider positive frequencies
        positive_freq_mask = frequencies > 0
        frequencies = frequencies[positive_freq_mask]
        power_spectrum = power_spectrum[positive_freq_mask]

        # Find peaks
        peaks, properties = signal.find_peaks(
            power_spectrum, height=np.max(power_spectrum) * 0.1, distance=len(power_spectrum) // 100
        )

        # Get top N peaks
        if len(peaks) > 0:
            peak_powers = power_spectrum[peaks]
            top_indices = np.argsort(peak_powers)[-n_peaks:][::-1]
            peak_frequencies = frequencies[peaks[top_indices]].tolist()
        else:
            peak_frequencies = []

        return [float(f) for f in peak_frequencies if 20 <= f <= sr // 2]

    def _calculate_energy_distribution(self, y: np.ndarray, sr: int) -> dict:
        """Calculate energy distribution across frequency spectrum."""
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        frequencies = librosa.fft_frequencies(sr=sr)

        # Divide into octaves
        octaves = []
        for octave in range(1, 9):  # 8 octaves
            fmin = 20 * (2 ** (octave - 1))
            fmax = 20 * (2**octave)
            freq_mask = (frequencies >= fmin) & (frequencies <= fmax)
            if np.any(freq_mask):
                energy = np.mean(magnitude[freq_mask, :])
                octaves.append(float(energy))
            else:
                octaves.append(0.0)

        # Normalize
        total = sum(octaves)
        if total > 0:
            octaves = [e / total * 100 for e in octaves]

        return {"octaves": octaves}

    def compare_frequency_content(self, vocals_path: Path, music_path: Path) -> dict:
        """
        Compare frequency content between vocals and music.

        Args:
            vocals_path: Path to vocals audio file
            music_path: Path to music audio file

        Returns:
            Dictionary containing comparison analysis:
            - vocals_analysis: Frequency analysis of vocals
            - music_analysis: Frequency analysis of music
            - conflicts: Frequency ranges where both have high energy
            - recommendations: EQ recommendations
        """
        logger.info("Comparing frequency content: vocals vs music")

        vocals_analysis = self.analyze_frequency_content(vocals_path)
        music_analysis = self.analyze_frequency_content(music_path)

        # Find frequency conflicts
        conflicts = self._find_frequency_conflicts(vocals_analysis, music_analysis)

        # Generate EQ recommendations
        recommendations = self._generate_eq_recommendations(
            vocals_analysis, music_analysis, conflicts
        )

        comparison = {
            "vocals_analysis": vocals_analysis,
            "music_analysis": music_analysis,
            "conflicts": conflicts,
            "recommendations": recommendations,
        }

        logger.success("Frequency comparison complete")
        return comparison

    def _find_frequency_conflicts(self, vocals_analysis: dict, music_analysis: dict) -> list[dict]:
        """Find frequency ranges where vocals and music conflict."""
        conflicts = []

        # Compare frequency bands
        vocals_bands = vocals_analysis["frequency_bands"]
        music_bands = music_analysis["frequency_bands"]

        band_ranges = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mid": (250, 500),
            "mid": (500, 2000),
            "high_mid": (2000, 4000),
            "treble": (4000, 20000),
        }

        for band_name, (fmin, fmax) in band_ranges.items():
            vocals_energy = vocals_bands.get(band_name, 0)
            music_energy = music_bands.get(band_name, 0)

            # Conflict if both have significant energy (>15%)
            if vocals_energy > 15 and music_energy > 15:
                conflicts.append(
                    {
                        "band": band_name,
                        "frequency_range": (fmin, fmax),
                        "vocals_energy": vocals_energy,
                        "music_energy": music_energy,
                        "severity": (
                            "high" if (vocals_energy > 25 and music_energy > 25) else "medium"
                        ),
                    }
                )

        return conflicts

    def _generate_eq_recommendations(
        self, vocals_analysis: dict, music_analysis: dict, conflicts: list[dict]
    ) -> list[dict]:
        """Generate EQ recommendations based on frequency analysis."""
        recommendations = []

        # Vocal frequency range: typically 80-1100 Hz (fundamental), harmonics up to 8kHz
        vocals_centroid = vocals_analysis["spectral_centroid"]
        vocals_bands = vocals_analysis["frequency_bands"]

        # Music frequency range: full spectrum
        music_bands = music_analysis["frequency_bands"]

        # Recommendation 1: Boost vocals in mid range (500-2000 Hz)
        if vocals_bands.get("mid", 0) < 20:
            recommendations.append(
                {
                    "type": "boost",
                    "target": "vocals",
                    "frequency": 1000,
                    "gain_db": 3.0,
                    "q": 1.0,
                    "reason": "Vocals need more presence in mid range",
                }
            )

        # Recommendation 2: Cut music in vocal range to make room
        for conflict in conflicts:
            if conflict["band"] in ["mid", "high_mid"]:
                recommendations.append(
                    {
                        "type": "cut",
                        "target": "music",
                        "frequency": sum(conflict["frequency_range"]) / 2,
                        "gain_db": -2.0 - (conflict["severity"] == "high") * 2.0,
                        "q": 1.5,
                        "reason": f"Reduce music in {conflict['band']} to make room for vocals",
                    }
                )

        # Recommendation 3: Boost vocals in high-mid for clarity
        if vocals_bands.get("high_mid", 0) < 15:
            recommendations.append(
                {
                    "type": "boost",
                    "target": "vocals",
                    "frequency": 3000,
                    "gain_db": 2.0,
                    "q": 1.0,
                    "reason": "Enhance vocal clarity",
                }
            )

        # Recommendation 4: Cut excessive bass in vocals
        if vocals_bands.get("bass", 0) > 25:
            recommendations.append(
                {
                    "type": "cut",
                    "target": "vocals",
                    "frequency": 150,
                    "gain_db": -3.0,
                    "q": 2.0,
                    "reason": "Remove excessive bass from vocals",
                }
            )

        return recommendations


class DynamicEQService:
    """Service for applying dynamic EQ based on frequency analysis."""

    def __init__(self):
        """Initialize dynamic EQ service."""
        self.freq_analysis = FrequencyAnalysisService()
        logger.success("DynamicEQService initialized")

    def apply_dynamic_eq(
        self,
        audio_path: Path,
        reference_analysis: Optional[dict] = None,
        genre: Optional[MusicGenre] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply dynamic EQ to audio based on frequency analysis.

        Args:
            audio_path: Path to audio file
            reference_analysis: Optional reference frequency analysis (for vocals)
            genre: Optional genre for genre-specific EQ
            output_path: Optional output path

        Returns:
            Path to EQ'd audio file
        """
        logger.info(f"Applying dynamic EQ: {audio_path}")

        y, sr = librosa.load(str(audio_path), sr=None)

        # Analyze current frequency content
        analysis = self.freq_analysis.analyze_frequency_content(audio_path, sr=sr)

        # Get EQ settings based on analysis and genre
        eq_settings = self._get_eq_settings(analysis, reference_analysis, genre)

        # Apply EQ
        eq_audio = self._apply_eq_filters(y, sr, eq_settings)

        # Generate output path
        if output_path is None:
            output_path = audio_path.with_stem(f"{audio_path.stem}_eq")

        # Save
        sf.write(str(output_path), eq_audio, sr)
        logger.success(f"Dynamic EQ applied: {output_path}")
        return output_path

    def _get_eq_settings(
        self,
        analysis: dict,
        reference_analysis: Optional[dict],
        genre: Optional[MusicGenre],
    ) -> list[dict]:
        """Get EQ settings based on analysis."""
        settings = []

        bands = analysis["frequency_bands"]

        # Genre-specific EQ presets
        if genre:
            genre_eq = self._get_genre_eq_preset(genre)
            settings.extend(genre_eq)

        # Adaptive EQ based on frequency content
        # Boost weak frequency bands
        if bands.get("mid", 0) < 15:
            settings.append({"frequency": 1000, "gain_db": 2.0, "q": 1.0})
        if bands.get("high_mid", 0) < 10:
            settings.append({"frequency": 3000, "gain_db": 1.5, "q": 1.0})

        # Cut excessive frequencies
        if bands.get("bass", 0) > 30:
            settings.append({"frequency": 150, "gain_db": -2.0, "q": 2.0})
        if bands.get("treble", 0) > 40:
            settings.append({"frequency": 8000, "gain_db": -1.5, "q": 1.5})

        # Reference-based EQ (for vocals)
        if reference_analysis:
            ref_bands = reference_analysis["frequency_bands"]
            # Boost frequencies that are weak compared to reference
            for band_name in ["mid", "high_mid"]:
                current = bands.get(band_name, 0)
                target = ref_bands.get(band_name, 0)
                if target > current + 5:
                    freq = {"mid": 1000, "high_mid": 3000}[band_name]
                    settings.append(
                        {"frequency": freq, "gain_db": (target - current) / 10, "q": 1.0}
                    )

        return settings

    def _get_genre_eq_preset(self, genre: MusicGenre) -> list[dict]:
        """Get genre-specific EQ presets."""
        presets = {
            MusicGenre.POP: [
                {"frequency": 2000, "gain_db": 1.5, "q": 1.0},  # Boost presence
                {"frequency": 8000, "gain_db": 1.0, "q": 1.0},  # Boost air
            ],
            MusicGenre.ROCK: [
                {"frequency": 3000, "gain_db": 2.0, "q": 1.0},  # Boost aggression
                {"frequency": 100, "gain_db": 1.0, "q": 1.0},  # Boost low end
            ],
            MusicGenre.HIPHOP: [
                {"frequency": 80, "gain_db": 2.0, "q": 1.5},  # Boost sub-bass
                {"frequency": 2000, "gain_db": -1.0, "q": 1.0},  # Cut harsh mids
            ],
            MusicGenre.ELECTRONIC: [
                {"frequency": 60, "gain_db": 1.5, "q": 1.5},  # Boost sub-bass
                {"frequency": 5000, "gain_db": 1.0, "q": 1.0},  # Boost clarity
            ],
            MusicGenre.JAZZ: [
                {"frequency": 500, "gain_db": 1.0, "q": 1.0},  # Warmth
                {"frequency": 3000, "gain_db": -0.5, "q": 1.0},  # Reduce harshness
            ],
        }

        return presets.get(genre, [])

    def _apply_eq_filters(self, y: np.ndarray, sr: int, eq_settings: list[dict]) -> np.ndarray:
        """Apply EQ filters to audio."""
        eq_audio = y.copy()

        for setting in eq_settings:
            freq = setting["frequency"]
            gain_db = setting["gain_db"]
            q = setting.get("q", 1.0)

            # Convert gain from dB to linear
            gain_linear = 10 ** (gain_db / 20.0)

            # Design parametric EQ filter
            # Using a simple bell filter (peaking EQ)
            w0 = 2 * np.pi * freq / sr
            alpha = np.sin(w0) / (2 * q)
            cos_w0 = np.cos(w0)
            A = np.sqrt(gain_linear)

            # Coefficients for biquad filter
            b0 = 1 + alpha * A
            b1 = -2 * cos_w0
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_w0
            a2 = 1 - alpha / A

            # Normalize
            b = np.array([b0, b1, b2]) / a0
            a = np.array([a0, a1, a2]) / a0

            # Apply filter
            eq_audio = signal.filtfilt(b, a, eq_audio)

        return eq_audio


class SidechainCompressionService:
    """Service for sidechain compression (music ducks when vocals are present)."""

    def __init__(self):
        """Initialize sidechain compression service."""
        logger.success("SidechainCompressionService initialized")

    def apply_sidechain_compression(
        self,
        vocals_path: Path,
        music_path: Path,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 100.0,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply sidechain compression to music based on vocals.

        Music volume is reduced when vocals are present.

        Args:
            vocals_path: Path to vocals audio (sidechain source)
            music_path: Path to music audio (sidechain target)
            threshold_db: Compression threshold in dB
            ratio: Compression ratio (4:1 means 4dB input = 1dB output above threshold)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            output_path: Optional output path

        Returns:
            Path to sidechain-compressed audio
        """
        logger.info(f"Applying sidechain compression: music ducks for vocals")

        vocals, sr_vocals = librosa.load(str(vocals_path), sr=None)
        music, sr_music = librosa.load(str(music_path), sr=None)

        # Ensure same sample rate
        if sr_vocals != sr_music:
            music = librosa.resample(music, orig_sr=sr_music, target_sr=sr_vocals)
            sr = sr_vocals
        else:
            sr = sr_vocals

        # Ensure same length
        min_len = min(len(vocals), len(music))
        vocals = vocals[:min_len]
        music = music[:min_len]

        # Calculate sidechain gain reduction envelope
        gain_reduction = self._calculate_gain_reduction(
            vocals, sr, threshold_db, ratio, attack_ms, release_ms
        )

        # Apply gain reduction to music
        compressed_music = music * gain_reduction

        # Generate output path
        if output_path is None:
            output_path = music_path.with_stem(f"{music_path.stem}_sidechain")

        # Save
        sf.write(str(output_path), compressed_music, sr)
        logger.success(f"Sidechain compression applied: {output_path}")
        return output_path

    def _calculate_gain_reduction(
        self,
        sidechain_signal: np.ndarray,
        sr: int,
        threshold_db: float,
        ratio: float,
        attack_ms: float,
        release_ms: float,
    ) -> np.ndarray:
        """Calculate gain reduction envelope from sidechain signal."""
        # Convert threshold to linear
        threshold_linear = 10 ** (threshold_db / 20.0)

        # Calculate envelope (RMS energy)
        frame_length = int(sr * 0.01)  # 10ms frames
        hop_length = frame_length // 2
        rms = librosa.feature.rms(
            y=sidechain_signal, frame_length=frame_length, hop_length=hop_length
        )[0]

        # Interpolate RMS to match signal length
        rms_full = np.interp(
            np.arange(len(sidechain_signal)), np.arange(len(rms)) * hop_length, rms
        )

        # Calculate compression
        gain_reduction = np.ones_like(sidechain_signal)

        for i in range(len(sidechain_signal)):
            level = abs(sidechain_signal[i])
            rms_level = rms_full[i]

            if rms_level > threshold_linear:
                # Calculate compression
                excess = rms_level - threshold_linear
                compressed_excess = excess / ratio
                target_level = threshold_linear + compressed_excess
                reduction = target_level / rms_level if rms_level > 0 else 1.0
            else:
                reduction = 1.0

            gain_reduction[i] = reduction

        # Apply attack and release smoothing
        attack_samples = int(sr * attack_ms / 1000.0)
        release_samples = int(sr * release_ms / 1000.0)

        smoothed = np.zeros_like(gain_reduction)
        smoothed[0] = gain_reduction[0]

        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] < smoothed[i - 1]:
                # Attack (faster when reducing)
                alpha = 1.0 / (1.0 + attack_samples)
            else:
                # Release (slower when recovering)
                alpha = 1.0 / (1.0 + release_samples)

            smoothed[i] = alpha * gain_reduction[i] + (1 - alpha) * smoothed[i - 1]

        return smoothed


# Singleton instances
_freq_analysis_service: Optional[FrequencyAnalysisService] = None
_dynamic_eq_service: Optional[DynamicEQService] = None
_sidechain_service: Optional[SidechainCompressionService] = None


def get_frequency_analysis() -> FrequencyAnalysisService:
    """Get or create frequency analysis service instance."""
    global _freq_analysis_service
    if _freq_analysis_service is None:
        _freq_analysis_service = FrequencyAnalysisService()
    return _freq_analysis_service


def get_dynamic_eq() -> DynamicEQService:
    """Get or create dynamic EQ service instance."""
    global _dynamic_eq_service
    if _dynamic_eq_service is None:
        _dynamic_eq_service = DynamicEQService()
    return _dynamic_eq_service


def get_sidechain_compression() -> SidechainCompressionService:
    """Get or create sidechain compression service instance."""
    global _sidechain_service
    if _sidechain_service is None:
        _sidechain_service = SidechainCompressionService()
    return _sidechain_service
