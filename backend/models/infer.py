"""
EchoGuard AI - Unified Audio Inference Engine
Provides the primary inference entrypoint: analyze(samples, sr) -> AudioSignal.
Integrates feature extraction, classification head, and isotonic calibration.
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from backend.audio.windows import AudioDecoder
from backend.models.wavlm_features import AcousticFeatureExtractor
from backend.models.head import SyntheticDetectionHead
from backend.models.calibrate import IsotonicCalibrator
from backend.app.schemas import AudioSignal


class AudioInferenceEngine:
    """
    Sub-second real-time audio synthetic speech inference engine.
    Ensures p95 latency < 100 ms on CPU.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.feature_extractor = AcousticFeatureExtractor(sample_rate=sample_rate)
        self.head = SyntheticDetectionHead()
        self.calibrator = IsotonicCalibrator()

    def analyze(self, samples: np.ndarray, sample_rate: int = 16000) -> AudioSignal:
        """
        Analyzes a float32 PCM segment (typically 2 seconds at 16 kHz).
        Returns a calibrated AudioSignal ready for fusion and accumulation.
        """
        start_time = time.perf_counter()

        # Handle sample rate if mismatched
        if sample_rate != self.sample_rate:
            from scipy import signal
            target_len = int(len(samples) * self.sample_rate / sample_rate)
            samples = signal.resample(samples, target_len)

        # 1. Feature extraction
        features = self.feature_extractor.extract_features(samples)
        is_silent = bool(features.get("is_silent", 0.0) > 0.5)

        # 2. Classification score
        raw_score = self.head.predict_raw_score(features)

        # 3. Isotonic calibration to probability & LLR
        calibrated_prob, llr = self.calibrator.calibrate(raw_score)

        # Telephony check (if band limited below 3.4kHz)
        is_telephony = bool(features.get("spectral_rolloff", 4000.0) < 3800.0)

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return AudioSignal(
            synthetic_prob=calibrated_prob,
            llr=llr,
            spectral_anomaly_score=round(float(features.get("phase_jitter_score", 0.0)), 4),
            hf_energy_ratio=round(float(features.get("hf_energy_ratio", 0.0)), 4),
            spectral_flatness=round(float(features.get("spectral_flatness", 0.0)), 4),
            channel_replay_score=round(float(features.get("zero_crossing_rate", 0.0)), 4),
            is_silent=is_silent,
            is_telephony_degraded=is_telephony,
            latency_ms=latency_ms
        )

    def analyze_bytes(self, audio_bytes: bytes) -> AudioSignal:
        """Helper to analyze raw audio payload (WAV/PCM)."""
        samples, sr = AudioDecoder.decode(audio_bytes)
        return self.analyze(samples, sr)
