"""
EchoGuard AI - Channel & Codec Cues (Family A Secondary Signals)
Detects replay, acoustic room impulse response artifacts, and synthetic codec laundering.
"""

import numpy as np
from typing import Dict


def detect_channel_replay_artifacts(samples: np.ndarray, sample_rate: int = 16000) -> float:
    """
    Detects acoustic double-convolution characteristic of physical loudspeaker replay:
    - Low-frequency room resonant peaks
    - Repetitive autocorrelation peaks in the 10ms - 50ms reflection lag range
    Returns score in [0.0, 1.0].
    """
    if len(samples) < sample_rate:
        return 0.0

    # Normalized autocorrelation
    centered = samples - np.mean(samples)
    autocorr = np.correlate(centered[:2000], centered[:2000], mode='full')
    autocorr = autocorr[len(autocorr)//2 :]
    max_peak = autocorr[0] + 1e-12
    norm_corr = autocorr / max_peak

    # Replay delay search between 10ms (160 samples) and 40ms (640 samples)
    replay_lag_window = norm_corr[160:640]
    replay_score = float(np.max(replay_lag_window)) if len(replay_lag_window) > 0 else 0.0

    return float(np.clip(max(0.0, replay_score * 1.5), 0.0, 1.0))
