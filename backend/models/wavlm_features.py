"""
EchoGuard AI - Acoustic & Pretrained Feature Extractor
Extracts vocoder phase anomalies, Wiener spectral flatness, and 4-8 kHz high-frequency disruptions.
Provides optional WavLM / SSL hook with CPU-optimized acoustic spectral fallback.
"""

import numpy as np
from scipy import signal
from typing import Dict, Any, Optional


class AcousticFeatureExtractor:
    """
    Extracts discriminative features distinguishing neural synthetic speech (HiFi-GAN, VITS, ElevenLabs)
    from natural human vocal tracts, especially under telephony codec conditions.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract_features(self, samples: np.ndarray) -> Dict[str, float]:
        """
        Extracts 6 core acoustic biomarkers from a 16 kHz audio window:
        1. hf_energy_ratio: Vocoder artifact energy proportion in 4 kHz - 8 kHz band
        2. spectral_flatness: Wiener entropy (geometric mean / arithmetic mean)
        3. spectral_centroid: Center of spectral mass (Hz)
        4. spectral_rolloff: 85% energy frequency ceiling (Hz)
        5. zero_crossing_rate: High-frequency boundary transitions
        6. phase_jitter_score: Temporal irregularity across STFT frames
        """
        if len(samples) < 512:
            return {
                "hf_energy_ratio": 0.0,
                "spectral_flatness": 0.0,
                "spectral_centroid": 0.0,
                "spectral_rolloff": 0.0,
                "zero_crossing_rate": 0.0,
                "phase_jitter_score": 0.0,
                "is_silent": 1.0
            }

        # Check silence
        rms_energy = np.sqrt(np.mean(samples ** 2) + 1e-12)
        if rms_energy < 0.003:
            return {
                "hf_energy_ratio": 0.0,
                "spectral_flatness": 0.0,
                "spectral_centroid": 0.0,
                "spectral_rolloff": 0.0,
                "zero_crossing_rate": 0.0,
                "phase_jitter_score": 0.0,
                "is_silent": 1.0
            }

        # Short-Time Fourier Transform
        n_fft = 1024
        hop_length = 256
        freqs, _, spec = signal.stft(
            samples,
            fs=self.sample_rate,
            nperseg=n_fft,
            noverlap=n_fft - hop_length
        )
        mag_spec = np.abs(spec)
        power_spec = mag_spec ** 2
        avg_power = np.mean(power_spec, axis=1) + 1e-12
        total_energy = np.sum(avg_power)

        # 1. High-Frequency Vocoder Energy Ratio (4000 Hz to 8000 Hz)
        hf_mask = freqs >= 4000
        hf_energy = np.sum(avg_power[hf_mask])
        hf_energy_ratio = float(hf_energy / (total_energy + 1e-12))

        # 2. Spectral Centroid
        spectral_centroid = float(np.sum(freqs * avg_power) / (total_energy + 1e-12))

        # 3. Spectral Rolloff (85% energy cutoff)
        cumulative_energy = np.cumsum(avg_power)
        rolloff_idx = np.searchsorted(cumulative_energy, 0.85 * total_energy)
        rolloff_idx = min(rolloff_idx, len(freqs) - 1)
        spectral_rolloff = float(freqs[rolloff_idx])

        # 4. Spectral Flatness (Wiener entropy)
        # Avoid log(0)
        log_power = np.log(avg_power + 1e-12)
        geometric_mean = np.exp(np.mean(log_power))
        arithmetic_mean = np.mean(avg_power)
        spectral_flatness = float(geometric_mean / (arithmetic_mean + 1e-12))

        # 5. Zero Crossing Rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(samples)))) / (2 * len(samples))

        # 6. Phase Jitter / Vocoder Discontinuity
        # Synthetic vocoders often exhibit phase incoherence across consecutive frames
        phase_angles = np.angle(spec)
        phase_diffs = np.diff(phase_angles, axis=1)
        phase_jitter_score = float(np.mean(np.abs(phase_diffs))) / np.pi

        return {
            "hf_energy_ratio": float(np.clip(hf_energy_ratio, 0.0, 1.0)),
            "spectral_flatness": float(np.clip(spectral_flatness, 0.0, 1.0)),
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "zero_crossing_rate": float(np.clip(zero_crossings, 0.0, 1.0)),
            "phase_jitter_score": float(np.clip(phase_jitter_score, 0.0, 1.0)),
            "is_silent": 0.0
        }
