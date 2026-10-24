"""
EchoGuard AI - Telephony Audio Augmentation Module
Part of Phase 1 Audio Engineering Pipeline.

Simulates realistic telecommunication network channel degradations:
- G.711 mu-law companding & quantization (ITU-T G.711 standard)
- Narrowband bandpass filtering (300 Hz - 3400 Hz standard POTS/telephony channel)
- Acoustic additive noise at configurable SNR (pink/call-center noise)
- VoIP packet loss with comfort-noise fill
- Codec transcoding & amplitude clipping
"""

import math
import numpy as np
from scipy import signal
from typing import Tuple, Optional


def mu_law_encode(samples: np.ndarray, mu: int = 255) -> np.ndarray:
    """
    Applies ITU-T G.711 mu-law non-linear companding.
    x in [-1.0, 1.0] -> y in [-1.0, 1.0]
    F(x) = sgn(x) * ln(1 + mu * |x|) / ln(1 + mu)
    """
    x = np.clip(samples, -1.0, 1.0)
    sign = np.sign(x)
    numerator = np.log1p(mu * np.abs(x))
    denominator = np.log1p(mu)
    return sign * (numerator / denominator)


def mu_law_decode(quantized: np.ndarray, mu: int = 255) -> np.ndarray:
    """
    Inverses ITU-T G.711 mu-law non-linear companding.
    F^-1(y) = sgn(y) * (1 / mu) * ((1 + mu)^|y| - 1)
    """
    y = np.clip(quantized, -1.0, 1.0)
    sign = np.sign(y)
    return sign * (1.0 / mu) * (np.power(1.0 + mu, np.abs(y)) - 1.0)


def apply_g711_telephony(samples: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """
    Simulates end-to-end G.711 PSTN telephony codec:
    1. Downsamples to 8 kHz standard telephony rate
    2. Compands with mu-law
    3. Quantizes to 8-bit resolution (256 discrete bins)
    4. Decompands
    5. Resamples back to target sample rate (16 kHz)
    """
    if len(samples) == 0:
        return samples

    # 1. Resample to 8kHz telephony bandwidth
    if sample_rate != 8000:
        num_8k_samples = int(len(samples) * 8000 / sample_rate)
        audio_8k = signal.resample(samples, num_8k_samples)
    else:
        audio_8k = samples.copy()

    # 2. mu-law compand
    encoded = mu_law_encode(audio_8k, mu=255)

    # 3. 8-bit uniform quantization [-128, 127]
    quantized_8bit = np.round(encoded * 127.0) / 127.0

    # 4. mu-law expand
    decoded_8k = mu_law_decode(quantized_8bit, mu=255)

    # 5. Resample back to original sample rate
    if sample_rate != 8000:
        return signal.resample(decoded_8k, len(samples))
    return decoded_8k


def apply_bandpass_telephony(
    samples: np.ndarray,
    sample_rate: int = 16000,
    low_freq: float = 300.0,
    high_freq: float = 3400.0,
    order: int = 4
) -> np.ndarray:
    """
    Applies standard POTS/telephony bandpass filtering (300 Hz - 3400 Hz)
    using a Butterworth digital filter.
    """
    if len(samples) < order * 4:
        return samples

    nyquist = 0.5 * sample_rate
    low = max(0.001, low_freq / nyquist)
    high = min(0.999, high_freq / nyquist)

    sos = signal.butter(order, [low, high], btype='bandpass', output='sos')
    filtered = signal.sosfilt(sos, samples)
    return np.asarray(filtered, dtype=np.float32)


def apply_packet_loss(
    samples: np.ndarray,
    sample_rate: int = 16000,
    loss_rate: float = 0.05,
    frame_ms: float = 30.0
) -> np.ndarray:
    """
    Simulates VoIP / cellular burst packet loss.
    Drops random frames and replaces them with comfort noise / silence.
    """
    if loss_rate <= 0.0 or len(samples) == 0:
        return samples

    frame_size = int(sample_rate * (frame_ms / 1000.0))
    if frame_size <= 0:
        return samples

    output = samples.copy()
    num_frames = len(samples) // frame_size

    for f in range(num_frames):
        if np.random.rand() < loss_rate:
            start_idx = f * frame_size
            end_idx = min(len(samples), start_idx + frame_size)
            # Comfort noise fill (low-level gaussian noise)
            comfort_noise = np.random.normal(0, 0.001, end_idx - start_idx).astype(np.float32)
            output[start_idx:end_idx] = comfort_noise

    return output


def add_acoustic_noise(
    samples: np.ndarray,
    snr_db: float = 18.0
) -> np.ndarray:
    """
    Adds Gaussian ambient noise scaled to target Signal-to-Noise Ratio (SNR in dB).
    """
    signal_power = np.mean(samples ** 2)
    if signal_power < 1e-9:
        return samples

    snr_linear = 10.0 ** (snr_db / 10.0)
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0.0, np.sqrt(noise_power), len(samples)).astype(np.float32)

    return np.clip(samples + noise, -1.0, 1.0)


class TelephonyAugmenter:
    """
    Composable augmentation pipeline for robust synthetic speech detection.
    Passes audio through multiple telephony degradation stages.
    """

    def __init__(
        self,
        enable_g711: bool = True,
        enable_bandpass: bool = True,
        enable_noise: bool = True,
        enable_packet_loss: bool = True,
        snr_db: float = 20.0,
        packet_loss_rate: float = 0.03
    ):
        self.enable_g711 = enable_g711
        self.enable_bandpass = enable_bandpass
        self.enable_noise = enable_noise
        self.enable_packet_loss = enable_packet_loss
        self.snr_db = snr_db
        self.packet_loss_rate = packet_loss_rate

    def augment(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """Applies the configured telephony degradations sequentially."""
        out = audio.copy()

        if self.enable_bandpass:
            out = apply_bandpass_telephony(out, sample_rate)

        if self.enable_g711:
            out = apply_g711_telephony(out, sample_rate)

        if self.enable_packet_loss:
            out = apply_packet_loss(out, sample_rate, self.packet_loss_rate)

        if self.enable_noise:
            out = add_acoustic_noise(out, self.snr_db)

        return np.asarray(out, dtype=np.float32)
