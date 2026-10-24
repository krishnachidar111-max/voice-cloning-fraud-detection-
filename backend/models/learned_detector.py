"""
EchoGuard AI - Learned Audio Engine
Replaces the hand-tuned spectral head with a trained sklearn LogisticRegression
head loaded from models/head.joblib.

Interface matches AudioInferenceEngine.analyze() exactly.

When models/head.joblib is absent, falls back to the spectral head and sets
is_fallback_mode = True so the UI can display the FALLBACK banner.
"""

import os
import time
import math
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import signal

from backend.app.schemas import AudioSignal

logger = logging.getLogger(__name__)

# Default path – override with DETECTOR_MODEL_PATH env var
_DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "head.joblib"


def _get_model_path() -> Path:
    env_path = os.environ.get("DETECTOR_MODEL_PATH", "")
    if env_path:
        return Path(env_path)
    return _DEFAULT_MODEL_PATH


# ─────────────────────────────────────────────────────────────────────────────
# Feature Extraction (25 spectral features)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_features(samples: np.ndarray, sample_rate: int = 16000) -> Optional[np.ndarray]:
    """
    Extracts 25 acoustic features from a float32 PCM window.
    Returns None for silent / too-short frames.
    """
    if len(samples) < 512:
        return None

    rms = float(np.sqrt(np.mean(samples ** 2) + 1e-12))
    if rms < 0.003:
        return None

    n_fft = 1024
    hop_length = 256
    freqs, _, spec = signal.stft(
        samples,
        fs=sample_rate,
        nperseg=n_fft,
        noverlap=n_fft - hop_length
    )
    mag_spec = np.abs(spec)
    power_spec = mag_spec ** 2
    avg_power = np.mean(power_spec, axis=1) + 1e-12
    total_energy = float(np.sum(avg_power))

    # 1. HF energy ratio (4–8 kHz)
    hf_mask = freqs >= 4000
    hf_energy = float(np.sum(avg_power[hf_mask]))
    hf_energy_ratio = hf_energy / (total_energy + 1e-12)

    # 2. LF energy ratio (0–1 kHz)
    lf_mask = freqs < 1000
    lf_energy = float(np.sum(avg_power[lf_mask]))
    lf_energy_ratio = lf_energy / (total_energy + 1e-12)

    # 3. Mid energy ratio (1–4 kHz)
    mid_mask = (freqs >= 1000) & (freqs < 4000)
    mid_energy = float(np.sum(avg_power[mid_mask]))
    mid_energy_ratio = mid_energy / (total_energy + 1e-12)

    # 4. Spectral centroid
    spectral_centroid = float(np.sum(freqs * avg_power) / (total_energy + 1e-12))

    # 5. Spectral rolloff (85%)
    cumulative = np.cumsum(avg_power)
    rolloff_idx = min(np.searchsorted(cumulative, 0.85 * total_energy), len(freqs) - 1)
    spectral_rolloff = float(freqs[rolloff_idx])

    # 6. Spectral flatness (Wiener entropy)
    log_power = np.log(avg_power + 1e-12)
    geom_mean = float(np.exp(np.mean(log_power)))
    arith_mean = float(np.mean(avg_power))
    spectral_flatness = geom_mean / (arith_mean + 1e-12)

    # 7. Zero crossing rate
    zcr = float(np.sum(np.abs(np.diff(np.sign(samples)))) / (2 * len(samples)))

    # 8. Phase jitter (vocoder discontinuity)
    phase_angles = np.angle(spec)
    phase_diffs = np.diff(phase_angles, axis=1)
    phase_jitter = float(np.mean(np.abs(phase_diffs))) / np.pi

    # 9. Spectral bandwidth (std around centroid)
    variance = float(np.sum((freqs - spectral_centroid) ** 2 * avg_power) / (total_energy + 1e-12))
    spectral_bandwidth = float(np.sqrt(variance))

    # 10. Spectral contrast (diff between peak and valley per sub-band)
    n_bands = 6
    band_edges = np.linspace(0, sample_rate // 2, n_bands + 1)
    contrasts = []
    for bi in range(n_bands):
        mask = (freqs >= band_edges[bi]) & (freqs < band_edges[bi + 1])
        if mask.sum() > 0:
            band_power = avg_power[mask]
            contrasts.append(float(np.max(band_power) / (np.min(band_power) + 1e-12)))
        else:
            contrasts.append(1.0)
    # 6 contrast values = features 10–15

    # 11. Mel filterbank statistics (4 mel bands — mean energy)
    mel_edges = np.array([0, 300, 800, 2000, 4000, 8000])
    mel_feats = []
    for mi in range(4):
        mask = (freqs >= mel_edges[mi]) & (freqs < mel_edges[mi + 1])
        mel_feats.append(float(np.mean(avg_power[mask])) if mask.sum() > 0 else 0.0)
    # 4 mel features = 16–19

    # 12. RMS energy (log scale)
    log_rms = float(np.log(rms + 1e-12))

    # 13. Temporal flatness (variance of frame energies)
    frame_energies = np.sum(power_spec, axis=0)
    temporal_flatness = float(np.std(frame_energies) / (np.mean(frame_energies) + 1e-12))

    # 14. Telephony flag (bandwidth check)
    is_telephony = float(spectral_rolloff < 3800.0 or hf_energy_ratio < 0.005)

    # 15. HF band flatness (4–8 kHz)
    if hf_mask.sum() > 0:
        hf_flat_power = avg_power[hf_mask]
        hf_geom = float(np.exp(np.mean(np.log(hf_flat_power + 1e-12))))
        hf_arith = float(np.mean(hf_flat_power))
        hf_flatness = hf_geom / (hf_arith + 1e-12)
    else:
        hf_flatness = 0.0

    feat = np.array([
        hf_energy_ratio,    # 0
        lf_energy_ratio,    # 1
        mid_energy_ratio,   # 2
        spectral_centroid / 8000.0,  # 3 (normalised)
        spectral_rolloff / 8000.0,   # 4
        float(np.clip(spectral_flatness, 0.0, 1.0)),  # 5
        float(np.clip(zcr, 0.0, 1.0)),                # 6
        float(np.clip(phase_jitter, 0.0, 1.0)),        # 7
        spectral_bandwidth / 8000.0,                   # 8
        contrasts[0], contrasts[1], contrasts[2],       # 9-11
        contrasts[3], contrasts[4], contrasts[5],       # 12-14
        mel_feats[0], mel_feats[1], mel_feats[2], mel_feats[3],  # 15-18
        float(np.clip((log_rms + 10) / 10, 0.0, 1.0)),  # 19
        float(np.clip(temporal_flatness, 0.0, 5.0)) / 5.0,  # 20
        is_telephony,                                    # 21
        float(np.clip(hf_flatness, 0.0, 1.0)),          # 22
        hf_energy_ratio * (1.0 - is_telephony),         # 23 (HF ratio when wideband)
        float(np.clip(phase_jitter * hf_energy_ratio * 10, 0.0, 1.0)),  # 24 interaction
    ], dtype=np.float32)

    return feat


def _llr_from_p(p: float, prior: float = 0.5) -> float:
    """Converts calibrated probability to log-likelihood ratio."""
    p = float(np.clip(p, 0.001, 0.999))
    prior = float(np.clip(prior, 0.001, 0.999))
    return float(np.clip(math.log((p / (1 - p)) / (prior / (1 - prior))), -5.0, 5.0))


# ─────────────────────────────────────────────────────────────────────────────
# Learned Audio Engine
# ─────────────────────────────────────────────────────────────────────────────

class LearnedAudioEngine:
    """
    Learned synthetic speech detector.

    Uses a 25-feature spectral frontend + sklearn LogisticRegression head
    (saved as models/head.joblib with an optional IsotonicRegression calibrator).

    When the model file is missing, falls back to the hand-tuned spectral head
    and sets `is_fallback_mode = True`.
    """

    def __init__(self, sample_rate: int = 16000, model_path: Optional[Path] = None):
        self.sample_rate = sample_rate
        self.is_fallback_mode = False
        self._clf = None
        self._calibrator = None

        path = model_path or _get_model_path()
        self._load_model(path)

    def _load_model(self, path: Path) -> None:
        if not path.exists():
            logger.warning(
                "FALLBACK MODE: models/head.joblib not found at %s. "
                "Using spectral heuristic. Results are NOT suitable for accuracy claims.",
                path
            )
            self.is_fallback_mode = True
            from backend.models.head import SyntheticDetectionHead
            from backend.models.wavlm_features import AcousticFeatureExtractor
            from backend.models.calibrate import IsotonicCalibrator
            self._spectral_head = SyntheticDetectionHead()
            self._spectral_features = AcousticFeatureExtractor(sample_rate=self.sample_rate)
            self._spectral_calibrator = IsotonicCalibrator()
            return

        try:
            import joblib
            bundle = joblib.load(path)
            if isinstance(bundle, dict):
                self._clf = bundle.get("clf")
                self._calibrator = bundle.get("calibrator")
                self._scaler = bundle.get("scaler")
            else:
                # Bare classifier
                self._clf = bundle
                self._calibrator = None
                self._scaler = None
            logger.info("Loaded learned model from %s", path)
        except Exception as e:
            logger.error("Failed to load model from %s: %s — falling back to spectral head", path, e)
            self.is_fallback_mode = True
            from backend.models.head import SyntheticDetectionHead
            from backend.models.wavlm_features import AcousticFeatureExtractor
            from backend.models.calibrate import IsotonicCalibrator
            self._spectral_head = SyntheticDetectionHead()
            self._spectral_features = AcousticFeatureExtractor(sample_rate=self.sample_rate)
            self._spectral_calibrator = IsotonicCalibrator()

    def analyze(self, samples: np.ndarray, sample_rate: int = 16000) -> AudioSignal:
        """
        Analyzes a float32 PCM segment.
        Returns an AudioSignal with calibrated synthetic_prob and llr.
        Interface is identical to AudioInferenceEngine.analyze().
        """
        start_time = time.perf_counter()

        # Resample if needed
        if sample_rate != self.sample_rate:
            target_len = int(len(samples) * self.sample_rate / sample_rate)
            samples = signal.resample(samples, target_len)

        # Silence check
        rms = float(np.sqrt(np.mean(samples ** 2) + 1e-12))
        is_silent = rms < 0.003 or len(samples) < 512

        if is_silent:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AudioSignal(
                synthetic_prob=0.05,
                llr=-2.94,
                spectral_anomaly_score=0.0,
                hf_energy_ratio=0.0,
                spectral_flatness=0.0,
                channel_replay_score=0.0,
                is_silent=True,
                is_telephony_degraded=False,
                latency_ms=latency_ms
            )

        # Telephony check (bandwidth)
        n_fft = 512
        freqs, _, spec = signal.stft(samples, fs=self.sample_rate, nperseg=n_fft)
        power = np.mean(np.abs(spec) ** 2, axis=1) + 1e-12
        total = np.sum(power)
        hf_ratio = float(np.sum(power[freqs >= 4000]) / total)
        cum = np.cumsum(power)
        rolloff_idx = min(np.searchsorted(cum, 0.85 * total), len(freqs) - 1)
        rolloff = float(freqs[rolloff_idx])
        is_telephony = bool(rolloff < 3800.0 or hf_ratio < 0.005)

        # ── Fallback path ──
        if self.is_fallback_mode:
            feats = self._spectral_features.extract_features(samples)
            raw = self._spectral_head.predict_raw_score(feats)
            calib_prob, llr = self._spectral_calibrator.calibrate(raw)
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AudioSignal(
                synthetic_prob=calib_prob,
                llr=llr,
                spectral_anomaly_score=round(float(feats.get("phase_jitter_score", 0.0)), 4),
                hf_energy_ratio=round(float(feats.get("hf_energy_ratio", 0.0)), 4),
                spectral_flatness=round(float(feats.get("spectral_flatness", 0.0)), 4),
                channel_replay_score=round(float(feats.get("zero_crossing_rate", 0.0)), 4),
                is_silent=False,
                is_telephony_degraded=is_telephony,
                latency_ms=latency_ms
            )

        # ── Learned path ──
        feat = _extract_features(samples, self.sample_rate)
        if feat is None:
            # Treat as silent
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AudioSignal(
                synthetic_prob=0.05,
                llr=-2.94,
                spectral_anomaly_score=0.0,
                hf_energy_ratio=round(hf_ratio, 4),
                spectral_flatness=0.0,
                channel_replay_score=0.0,
                is_silent=True,
                is_telephony_degraded=is_telephony,
                latency_ms=latency_ms
            )

        feat_2d = feat.reshape(1, -1)
        if self._scaler is not None:
            feat_2d = self._scaler.transform(feat_2d)

        if self._calibrator is not None:
            raw_prob = float(self._clf.predict_proba(feat_2d)[0, 1])
            calib_prob = float(np.clip(self._calibrator.predict([raw_prob])[0], 0.001, 0.999))
        else:
            calib_prob = float(np.clip(self._clf.predict_proba(feat_2d)[0, 1], 0.001, 0.999))

        llr = _llr_from_p(calib_prob)
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return AudioSignal(
            synthetic_prob=round(calib_prob, 4),
            llr=round(llr, 4),
            spectral_anomaly_score=round(float(np.clip(feat[7], 0.0, 1.0)), 4),  # phase jitter
            hf_energy_ratio=round(float(np.clip(hf_ratio, 0.0, 1.0)), 4),
            spectral_flatness=round(float(np.clip(feat[5], 0.0, 1.0)), 4),
            channel_replay_score=round(float(np.clip(feat[6], 0.0, 1.0)), 4),  # ZCR
            is_silent=False,
            is_telephony_degraded=is_telephony,
            latency_ms=latency_ms
        )

    def analyze_bytes(self, audio_bytes: bytes) -> AudioSignal:
        """Helper to analyze raw audio payload (WAV/PCM)."""
        from backend.audio.windows import AudioDecoder
        samples, sr = AudioDecoder.decode(audio_bytes)
        return self.analyze(samples, sr)
