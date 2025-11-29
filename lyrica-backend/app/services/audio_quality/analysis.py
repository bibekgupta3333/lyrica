"""
Audio Analysis Service.

Provides comprehensive audio analysis:
- Loudness analysis (LUFS, RMS, peak)
- Clarity and quality metrics
- Spectral analysis
- Performance metrics
"""

from pathlib import Path
from typing import Dict, List, Optional

import librosa
import numpy as np
from loguru import logger
from pydub import AudioSegment


class AudioAnalysisService:
    """Service for analyzing audio quality and characteristics."""

    def __init__(self):
        """Initialize audio analysis service."""
        logger.info("Audio analysis service initialized")

    def analyze_loudness(self, audio_path: Path) -> Dict:
        """
        Analyze audio loudness metrics.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with loudness metrics
        """
        logger.info(f"Analyzing loudness: {audio_path}")

        try:
            y, sr = librosa.load(str(audio_path), sr=None)

            # Calculate RMS (Root Mean Square)
            rms = np.sqrt(np.mean(y**2))
            rms_db = 20 * np.log10(rms) if rms > 0 else -100.0

            # Calculate peak
            peak = np.max(np.abs(y))
            peak_db = 20 * np.log10(peak) if peak > 0 else -100.0

            # Calculate crest factor
            crest_factor = peak / rms if rms > 0 else 0.0
            crest_factor_db = 20 * np.log10(crest_factor) if crest_factor > 0 else 0.0

            # Estimate LUFS (simplified - real LUFS requires K-weighting filter)
            estimated_lufs = rms_db - 3.0

            # Calculate loudness range
            frame_length = 2048
            hop_length = 512
            rms_frames = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[
                0
            ]
            rms_frames_db = librosa.amplitude_to_db(rms_frames, ref=np.max)

            loudness_range = float(
                np.percentile(rms_frames_db, 95) - np.percentile(rms_frames_db, 5)
            )

            # True peak (check for inter-sample peaks via upsampling)
            y_upsampled = librosa.resample(y, orig_sr=sr, target_sr=sr * 4)
            true_peak = np.max(np.abs(y_upsampled))
            true_peak_db = 20 * np.log10(true_peak) if true_peak > 0 else -100.0

            return {
                "rms_db": float(rms_db),
                "peak_db": float(peak_db),
                "true_peak_db": float(true_peak_db),
                "estimated_lufs": float(estimated_lufs),
                "crest_factor_db": float(crest_factor_db),
                "loudness_range_db": loudness_range,
                "is_clipping": true_peak >= 0.99,
                "headroom_db": float(0.0 - true_peak_db),
            }

        except Exception as e:
            logger.error(f"Error analyzing loudness: {e}")
            raise

    def analyze_clarity(self, audio_path: Path) -> Dict:
        """
        Analyze audio clarity and quality metrics.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with clarity metrics
        """
        logger.info(f"Analyzing clarity: {audio_path}")

        try:
            y, sr = librosa.load(str(audio_path), sr=None)

            # Spectral centroid (brightness)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            avg_brightness = float(np.mean(spectral_centroid))

            # Spectral rolloff (frequency content)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
            avg_rolloff = float(np.mean(spectral_rolloff))

            # Spectral bandwidth (timbre)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            avg_bandwidth = float(np.mean(spectral_bandwidth))

            # Zero crossing rate (noisiness)
            zero_crossings = librosa.zero_crossings(y, pad=False)
            zcr = float(np.sum(zero_crossings) / len(y))

            # Signal-to-noise ratio (estimate)
            # Use quietest 10% as noise estimate
            frame_rms = librosa.feature.rms(y=y)[0]
            noise_floor = np.percentile(frame_rms, 10)
            signal_level = np.mean(frame_rms)
            snr_db = 20 * np.log10(signal_level / noise_floor) if noise_floor > 0 else 100.0

            # Spectral contrast (dynamic range across frequency bands)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            avg_contrast = float(np.mean(spectral_contrast))

            # Clarity score (0-100)
            clarity_score = self._calculate_clarity_score(
                snr_db=snr_db,
                bandwidth=avg_bandwidth,
                zcr=zcr,
            )

            return {
                "spectral_centroid_hz": avg_brightness,
                "spectral_rolloff_hz": avg_rolloff,
                "spectral_bandwidth_hz": avg_bandwidth,
                "zero_crossing_rate": zcr,
                "estimated_snr_db": float(snr_db),
                "spectral_contrast_db": avg_contrast,
                "clarity_score": clarity_score,
                "quality_grade": self._get_clarity_grade(clarity_score),
            }

        except Exception as e:
            logger.error(f"Error analyzing clarity: {e}")
            raise

    def _calculate_clarity_score(
        self,
        snr_db: float,
        bandwidth: float,
        zcr: float,
    ) -> float:
        """Calculate overall clarity score."""
        score = 50.0

        # SNR contribution (0-40 points)
        if snr_db > 40:
            score += 40
        elif snr_db > 20:
            score += 20 + (snr_db - 20)
        elif snr_db > 10:
            score += snr_db
        else:
            score += max(0, snr_db / 2)

        # Bandwidth contribution (0-10 points)
        if bandwidth > 8000:
            score += 10
        elif bandwidth > 4000:
            score += 5

        # Low ZCR is better (less noise) (0-10 points penalty)
        if zcr > 0.2:
            score -= 10
        elif zcr > 0.1:
            score -= 5

        return max(0.0, min(100.0, score))

    def _get_clarity_grade(self, score: float) -> str:
        """Convert clarity score to grade."""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Poor"
        else:
            return "Very Poor"

    def analyze_spectral(self, audio_path: Path) -> Dict:
        """
        Perform spectral analysis.

        Args:
            audio_path: Path to audio file

        Returns:
            Spectral analysis results
        """
        logger.info(f"Analyzing spectrum: {audio_path}")

        try:
            y, sr = librosa.load(str(audio_path), sr=None)

            # Compute mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

            # Frequency band energy distribution
            freq_bands = {
                "sub_bass": (20, 60),
                "bass": (60, 250),
                "low_mid": (250, 500),
                "mid": (500, 2000),
                "high_mid": (2000, 4000),
                "presence": (4000, 6000),
                "brilliance": (6000, 20000),
            }

            band_energy = {}
            for band_name, (low_freq, high_freq) in freq_bands.items():
                # Convert frequencies to mel scale
                mel_low = librosa.hz_to_mel(low_freq)
                mel_high = librosa.hz_to_mel(high_freq)

                # Find corresponding mel bins
                mel_freqs = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=sr / 2)
                mask = (mel_freqs >= mel_low) & (mel_freqs <= mel_high)

                # Calculate average energy in band
                if np.any(mask):
                    band_energy[band_name] = float(np.mean(mel_spec_db[mask]))
                else:
                    band_energy[band_name] = -100.0

            # Overall spectral characteristics
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            avg_flatness = float(np.mean(spectral_flatness))

            return {
                "frequency_band_energy_db": band_energy,
                "spectral_flatness": avg_flatness,
                "is_tonal": avg_flatness < 0.1,  # Low flatness = tonal
                "is_noisy": avg_flatness > 0.5,  # High flatness = noisy
            }

        except Exception as e:
            logger.error(f"Error analyzing spectrum: {e}")
            raise

    def analyze_performance(self, audio_path: Path) -> Dict:
        """
        Analyze audio performance metrics.

        Args:
            audio_path: Path to audio file

        Returns:
            Performance metrics
        """
        logger.info(f"Analyzing performance: {audio_path}")

        try:
            # Get file info
            audio = AudioSegment.from_file(str(audio_path))
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)

            # Calculate bitrate
            duration_seconds = len(audio) / 1000.0
            bitrate_kbps = (
                (file_size_mb * 8 * 1024) / duration_seconds if duration_seconds > 0 else 0
            )

            # Load for detailed analysis
            y, sr = librosa.load(str(audio_path), sr=None)

            # Check encoding quality indicators
            # High frequency content (indicates better encoding)
            stft = librosa.stft(y)
            magnitude = np.abs(stft)

            # Check if high frequencies are preserved (> 12kHz)
            freq_bins = librosa.fft_frequencies(sr=sr)
            high_freq_mask = freq_bins > 12000
            high_freq_energy = float(np.mean(magnitude[high_freq_mask]))
            total_energy = float(np.mean(magnitude))
            high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0.0

            # Estimate encoding quality
            if high_freq_ratio > 0.01 and bitrate_kbps > 256:
                quality_estimate = "Excellent"
            elif high_freq_ratio > 0.005 and bitrate_kbps > 192:
                quality_estimate = "Good"
            elif bitrate_kbps > 128:
                quality_estimate = "Acceptable"
            else:
                quality_estimate = "Poor"

            return {
                "file_size_mb": file_size_mb,
                "duration_seconds": duration_seconds,
                "sample_rate_hz": sr,
                "channels": audio.channels,
                "bit_depth": audio.sample_width * 8,
                "estimated_bitrate_kbps": bitrate_kbps,
                "high_frequency_preservation": high_freq_ratio,
                "encoding_quality": quality_estimate,
            }

        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            raise

    def comprehensive_analysis(self, audio_path: Path) -> Dict:
        """
        Perform comprehensive audio analysis.

        Args:
            audio_path: Path to audio file

        Returns:
            Complete analysis results
        """
        logger.info(f"Performing comprehensive analysis: {audio_path}")

        try:
            analysis = {
                "file_path": str(audio_path),
                "loudness": self.analyze_loudness(audio_path),
                "clarity": self.analyze_clarity(audio_path),
                "spectral": self.analyze_spectral(audio_path),
                "performance": self.analyze_performance(audio_path),
            }

            # Calculate overall quality score
            loudness_score = self._score_loudness(analysis["loudness"])
            clarity_score = analysis["clarity"]["clarity_score"]
            spectral_score = self._score_spectral(analysis["spectral"])

            overall_score = (loudness_score + clarity_score + spectral_score) / 3.0

            analysis["overall"] = {
                "quality_score": overall_score,
                "grade": self._get_overall_grade(overall_score),
                "loudness_score": loudness_score,
                "clarity_score": clarity_score,
                "spectral_score": spectral_score,
            }

            logger.success(
                f"Comprehensive analysis complete. Overall score: {overall_score:.1f}/100"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise

    def _score_loudness(self, loudness_metrics: Dict) -> float:
        """Score loudness metrics."""
        score = 50.0

        # Check LUFS target (-14.0 is broadcast standard)
        lufs = loudness_metrics.get("estimated_lufs", -100)
        lufs_deviation = abs(lufs - (-14.0))
        if lufs_deviation < 1.0:
            score += 25
        elif lufs_deviation < 3.0:
            score += 15
        elif lufs_deviation < 6.0:
            score += 5

        # Check headroom
        headroom = loudness_metrics.get("headroom_db", 0)
        if headroom > 3.0:
            score += 15
        elif headroom > 1.0:
            score += 10
        elif headroom > 0.1:
            score += 5

        # Check for clipping
        if not loudness_metrics.get("is_clipping", False):
            score += 10

        return max(0.0, min(100.0, score))

    def _score_spectral(self, spectral_metrics: Dict) -> float:
        """Score spectral metrics."""
        score = 50.0

        # Balanced frequency distribution
        band_energy = spectral_metrics.get("frequency_band_energy_db", {})
        if band_energy:
            # Check if energy is reasonably distributed
            energies = list(band_energy.values())
            energy_range = max(energies) - min(energies)

            if energy_range < 20:
                score += 30  # Well balanced
            elif energy_range < 30:
                score += 20
            elif energy_range < 40:
                score += 10

        # Not too noisy
        if not spectral_metrics.get("is_noisy", True):
            score += 20

        return max(0.0, min(100.0, score))

    def _get_overall_grade(self, score: float) -> str:
        """Get overall quality grade."""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"


# Singleton instance
_audio_analysis_service: Optional[AudioAnalysisService] = None


def get_audio_analysis() -> AudioAnalysisService:
    """Get singleton audio analysis service."""
    global _audio_analysis_service
    if _audio_analysis_service is None:
        _audio_analysis_service = AudioAnalysisService()
    return _audio_analysis_service
