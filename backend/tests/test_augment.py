"""
Unit tests for telephony simulation & augmentation module.
Verifies G.711 mu-law, bandpass filtering, packet loss, and noise injection.
"""

import numpy as np
import pytest
from backend.audio.augment import (
    mu_law_encode,
    mu_law_decode,
    apply_g711_telephony,
    apply_bandpass_telephony,
    apply_packet_loss,
    add_acoustic_noise,
    TelephonyAugmenter,
)


@pytest.fixture
def synthetic_speech_signal():
    """Generates a 1-second 16kHz test sine tone with harmonics."""
    sample_rate = 16000
    t = np.linspace(0, 1.0, sample_rate, endpoint=False)
    # Fundamental 300Hz + 1kHz + 2.5kHz + 5kHz harmonics
    signal_data = (
        0.5 * np.sin(2 * np.pi * 300 * t) +
        0.3 * np.sin(2 * np.pi * 1000 * t) +
        0.15 * np.sin(2 * np.pi * 2500 * t) +
        0.05 * np.sin(2 * np.pi * 5000 * t)
    )
    return signal_data.astype(np.float32)


def test_mu_law_reconstruction(synthetic_speech_signal):
    """Verifies that mu-law encoding and decoding reconstructs signal within quantization bounds."""
    encoded = mu_law_encode(synthetic_speech_signal, mu=255)
    decoded = mu_law_decode(encoded, mu=255)

    # Values must remain bounded in [-1.0, 1.0]
    assert np.all(encoded >= -1.0) and np.all(encoded <= 1.0)
    assert np.all(decoded >= -1.0) and np.all(decoded <= 1.0)

    # Quantization error without bit truncation is very small
    error = np.mean((synthetic_speech_signal - decoded) ** 2)
    assert error < 1e-4


def test_g711_codec_pipeline(synthetic_speech_signal):
    """Verifies full G.711 downsample -> compand -> 8bit quantize -> expand -> upsample pipeline."""
    degraded = apply_g711_telephony(synthetic_speech_signal, sample_rate=16000)

    assert len(degraded) == len(synthetic_speech_signal)
    assert not np.isnan(degraded).any()
    assert not np.isinf(degraded).any()

    # Telephony 8-bit quantization creates noticeable but bounded distortion
    snr = 10 * np.log10(np.mean(synthetic_speech_signal ** 2) / np.mean((synthetic_speech_signal - degraded) ** 2))
    assert snr > 15.0  # G.711 SNR typically 25-35 dB


def test_bandpass_telephony_attenuation(synthetic_speech_signal):
    """Verifies bandpass filter removes high frequencies (>3400Hz)."""
    filtered = apply_bandpass_telephony(synthetic_speech_signal, sample_rate=16000, low_freq=300, high_freq=3400)

    assert len(filtered) == len(synthetic_speech_signal)
    assert np.max(np.abs(filtered)) <= 1.0

    # The 5000 Hz component should be heavily attenuated
    fft_orig = np.abs(np.fft.rfft(synthetic_speech_signal))
    fft_filt = np.abs(np.fft.rfft(filtered))
    freqs = np.fft.rfftfreq(len(synthetic_speech_signal), 1.0 / 16000)

    high_freq_idx = np.where(freqs >= 4500)[0]
    orig_hf_power = np.sum(fft_orig[high_freq_idx] ** 2)
    filt_hf_power = np.sum(fft_filt[high_freq_idx] ** 2)

    assert filt_hf_power < orig_hf_power * 0.05  # At least 95% attenuation at 5kHz


def test_packet_loss_injection(synthetic_speech_signal):
    """Verifies packet loss drops frames and fills with comfort noise."""
    corrupted = apply_packet_loss(synthetic_speech_signal, sample_rate=16000, loss_rate=0.20, frame_ms=30.0)

    assert len(corrupted) == len(synthetic_speech_signal)
    # Some parts should be different from original
    differences = np.abs(corrupted - synthetic_speech_signal)
    assert np.sum(differences > 0.01) > 0


def test_acoustic_noise_snr(synthetic_speech_signal):
    """Verifies additive noise adheres to target SNR."""
    target_snr = 20.0
    noisy = add_acoustic_noise(synthetic_speech_signal, snr_db=target_snr)

    noise = noisy - synthetic_speech_signal
    measured_snr = 10 * np.log10(np.mean(synthetic_speech_signal ** 2) / (np.mean(noise ** 2) + 1e-12))

    assert pytest.approx(target_snr, abs=3.0) == measured_snr


def test_telephony_augmenter_class(synthetic_speech_signal):
    """Verifies the complete TelephonyAugmenter pipeline executes without errors."""
    augmenter = TelephonyAugmenter(
        enable_g711=True,
        enable_bandpass=True,
        enable_noise=True,
        enable_packet_loss=True,
        snr_db=18.0,
        packet_loss_rate=0.04
    )
    augmented = augmenter.augment(synthetic_speech_signal, sample_rate=16000)

    assert isinstance(augmented, np.ndarray)
    assert len(augmented) == len(synthetic_speech_signal)
    assert np.all(np.isfinite(augmented))
