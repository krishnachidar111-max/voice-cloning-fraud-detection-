"""
EchoGuard AI - Unified Audio Inference Engine
Provides the primary inference entrypoint: analyze(samples, sr) -> AudioSignal.
Integrates feature extraction, classification head, and isotonic calibration.
Dispatches between LearnedAudioEngine and the legacy spectral head based on config.
"""

import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from backend.app.config import settings
from backend.audio.windows import AudioDecoder
from backend.models.wavlm_features import AcousticFeatureExtractor
from backend.models.head import SyntheticDetectionHead
from backend.models.calibrate import IsotonicCalibrator
from backend.models.learned_detector import LearnedAudioEngine
from backend.app.schemas import AudioSignal


class LegacySpectralEngine:
    """Fallback legacy spectral inference engine."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.feature_extractor = AcousticFeatureExtractor(sample_rate=sample_rate)
        self.head = SyntheticDetectionHead()
        self.calibrator = IsotonicCalibrator()
        self.is_fallback_mode = True

    def analyze(self, samples: np.ndarray, sample_rate: int = 16000) -> AudioSignal:
        start_time = time.perf_counter()

        if sample_rate != self.sample_rate:
            from scipy import signal
            target_len = int(len(samples) * self.sample_rate / sample_rate)
            samples = signal.resample(samples, target_len)

        features = self.feature_extractor.extract_features(samples)
        is_silent = bool(features.get("is_silent", 0.0) > 0.5)
        raw_score = self.head.predict_raw_score(features)
        calibrated_prob, llr = self.calibrator.calibrate(raw_score)
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
        samples, sr = AudioDecoder.decode(audio_bytes)
        return self.analyze(samples, sr)


class AudioInferenceEngine:
    """
    Sub-second real-time audio synthetic speech inference engine.
    Dispatches to LearnedAudioEngine by default or when configured.
    Ensures p95 latency < 100 ms on CPU.
    """

    def __init__(self, sample_rate: int = 16000, backend: Optional[str] = None):
        self.sample_rate = sample_rate
        backend_choice = backend or getattr(settings, "DETECTOR_BACKEND", "learned")

        if backend_choice == "learned":
            model_path_str = getattr(settings, "DETECTOR_MODEL_PATH", "")
            model_path = Path(model_path_str) if model_path_str else None
            self._engine = LearnedAudioEngine(sample_rate=sample_rate, model_path=model_path)
            self.backend_name = "learned"
        else:
            self._engine = LegacySpectralEngine(sample_rate=sample_rate)
            self.backend_name = "spectral"

    @property
    def is_fallback_mode(self) -> bool:
        return getattr(self._engine, "is_fallback_mode", False)

    def analyze(self, samples: np.ndarray, sample_rate: int = 16000) -> AudioSignal:
        return self._engine.analyze(samples, sample_rate)

    def analyze_bytes(self, audio_bytes: bytes) -> AudioSignal:
        return self._engine.analyze_bytes(audio_bytes)
