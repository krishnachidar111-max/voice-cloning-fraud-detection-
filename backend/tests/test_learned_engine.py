"""
EchoGuard AI - Unit Tests for LearnedAudioEngine
Verifies:
1. Feature vector dimensionality (25 features)
2. Silence detection & safe response
3. Telephony band-limited degradation handling
4. Fallback banner activation when model artifact missing
5. Zero disk audio persistence guarantee
"""

import os
import tempfile
import numpy as np
from pathlib import Path

from backend.models.learned_detector import LearnedAudioEngine, _extract_features
from backend.models.infer import AudioInferenceEngine


def test_feature_vector_dimensionality():
    sr = 16000
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    # Synthetic speech wave
    samples = (0.4 * np.sin(2 * np.pi * 200 * t) + 0.1 * np.sin(2 * np.pi * 5000 * t)).astype(np.float32)

    feat = _extract_features(samples, sr)
    assert feat is not None
    assert feat.shape == (25,), f"Expected 25 features, got {feat.shape}"
    assert np.all(np.isfinite(feat)), "Features must be finite numbers"


def test_silence_detection():
    sr = 16000
    silent_samples = np.zeros(int(2.0 * sr), dtype=np.float32)
    engine = LearnedAudioEngine(sample_rate=sr)

    signal = engine.analyze(silent_samples, sr)
    assert signal.is_silent is True
    assert signal.synthetic_prob < 0.15
    assert signal.llr < 0.0


def test_telephony_detection():
    sr = 16000
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    # Low-pass limited band audio (e.g. 300 - 3000 Hz, strictly below 3.4 kHz)
    telephony_samples = (0.5 * np.sin(2 * np.pi * 400 * t) + 0.3 * np.sin(2 * np.pi * 1200 * t)).astype(np.float32)
    engine = LearnedAudioEngine(sample_rate=sr)

    signal = engine.analyze(telephony_samples, sr)
    assert signal.is_telephony_degraded is True


def test_fallback_mode_when_model_missing():
    non_existent = Path(tempfile.gettempdir()) / "non_existent_model_head.joblib"
    if non_existent.exists():
        non_existent.unlink()

    engine = LearnedAudioEngine(model_path=non_existent)
    assert engine.is_fallback_mode is True

    sr = 16000
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    samples = (0.4 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)

    signal = engine.analyze(samples, sr)
    assert hasattr(signal, "synthetic_prob")
    assert 0.0 <= signal.synthetic_prob <= 1.0


def test_zero_disk_writes_on_inference():
    sr = 16000
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    samples = (0.3 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)

    # Record all file mtimes in root before inference
    project_root = Path(__file__).resolve().parent.parent.parent
    audio_extensions = {".wav", ".mp3", ".raw", ".pcm", ".aac", ".flac"}
    pre_audio_files = {p for p in project_root.rglob("*") if p.suffix.lower() in audio_extensions}

    engine = AudioInferenceEngine(sample_rate=sr)
    for _ in range(5):
        engine.analyze(samples, sr)

    post_audio_files = {p for p in project_root.rglob("*") if p.suffix.lower() in audio_extensions}
    new_audio_files = post_audio_files - pre_audio_files
    assert len(new_audio_files) == 0, f"Inference persisted audio files to disk: {new_audio_files}"
