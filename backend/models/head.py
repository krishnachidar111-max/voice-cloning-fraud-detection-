"""
EchoGuard AI - Synthetic Speech Classification Head
Adaptive decision head mapping acoustic spectral features to a raw synthetic likelihood score.
Features dynamic weighting for narrowband telephony channels (300 Hz - 3400 Hz) vs wideband audio.
"""

import math
import numpy as np
from typing import Dict, Any


class SyntheticDetectionHead:
    """
    Calibrated classification head with dual-mode evaluation:
    1. Wideband mode: uses high-frequency vocoder harmonics (4k-8kHz) + spectral flatness + phase jitter.
    2. Telephony mode (G.711 / bandpassed < 3.8kHz): adapts weights to vocoder phase jitter,
       in-band Wiener entropy, and temporal zero-crossing rate when HF band is truncated by the telecom carrier.
    """

    def predict_raw_score(self, features: Dict[str, float]) -> float:
        """
        Computes synthetic speech probability score in [0.0, 1.0].
        """
        if features.get("is_silent", 0.0) > 0.5:
            return 0.05  # Silence baseline is bonafide

        hf_ratio = features.get("hf_energy_ratio", 0.0)
        centroid = features.get("spectral_centroid", 350.0)
        zcr = features.get("zero_crossing_rate", 0.06)
        flatness = features.get("spectral_flatness", 0.0)
        phase_jitter = features.get("phase_jitter_score", 0.5)

        is_telephony = bool(features.get("spectral_rolloff", 4000.0) < 3800.0 or hf_ratio < 0.005)

        if is_telephony:
            # Telephony Mode: High frequencies are stripped by POTS carrier.
            # Natural human speech retains low phase jitter (<0.72) and low flatness (<0.00005)
            logit = (
                5.20 * (phase_jitter - 0.74) +
                220.0 * flatness +
                10.0 * (zcr - 0.12) +
                0.0018 * (centroid - 550.0) -
                2.40
            )
        else:
            # Wideband Mode: High-frequency vocoder energy ratio (4-8kHz) is primary indicator
            logit = (
                18.50 * hf_ratio +
                0.0028 * (centroid - 500.0) +
                8.40 * (zcr - 0.10) +
                120.0 * flatness +
                2.20 * (phase_jitter - 0.50) -
                3.10
            )

        # Logistic sigmoid activation
        raw_prob = 1.0 / (1.0 + math.exp(-np.clip(logit, -10.0, 10.0)))
        return float(np.clip(raw_prob, 0.001, 0.999))
