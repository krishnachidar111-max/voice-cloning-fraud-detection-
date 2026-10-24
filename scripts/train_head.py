"""
EchoGuard AI - Trainable Detection Head
Trains a LogisticRegression head + Isotonic Calibrator over 25 spectral features.
Saves the artifact to models/head.joblib for LearnedAudioEngine.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.learned_detector import _extract_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def train_head(
    manifest_path: str = None,
    output_path: str = "models/head.joblib",
    n_samples: int = 400
):
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.isotonic import IsotonicRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        import joblib
    except ImportError:
        logger.error("scikit-learn and joblib required to train detector head.")
        sys.exit(1)

    X_list = []
    y_list = []

    if manifest_path and os.path.exists(manifest_path):
        import csv
        import soundfile as sf
        logger.info("Loading manifest from %s", manifest_path)
        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or row[0].startswith("#") or row[0] == "path":
                    continue
                audio_path, label = row[0], int(row[1])
                if os.path.exists(audio_path):
                    data, sr = sf.read(audio_path)
                    if data.ndim > 1:
                        data = data.mean(axis=1)
                    feat = _extract_features(data.astype(np.float32), sr)
                    if feat is not None:
                        X_list.append(feat)
                        y_list.append(label)
    else:
        logger.info(
            "No manifest provided or file not found. Generating balanced synthetic training features (n=%d)...",
            n_samples
        )
        sr = 16000
        t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
        np.random.seed(42)

        # Generate realistic bona-fide speech harmonic mock samples (label 0)
        for i in range(n_samples // 2):
            f0 = np.random.uniform(90.0, 260.0)
            audio = (
                0.35 * np.sin(2 * np.pi * f0 * t) +
                0.20 * np.sin(2 * np.pi * 2 * f0 * t) +
                0.12 * np.sin(2 * np.pi * 3 * f0 * t) +
                0.05 * np.sin(2 * np.pi * 4 * f0 * t) +
                np.random.normal(0, 0.008, len(t))
            ).astype(np.float32)
            feat = _extract_features(audio, sr)
            if feat is not None:
                X_list.append(feat)
                y_list.append(0)

        # Generate synthetic vocoder mock samples with phase jitter & HF energy (label 1)
        for i in range(n_samples // 2):
            f0 = np.random.uniform(90.0, 260.0)
            jitter_phase = np.cumsum(np.random.uniform(-0.8, 0.8, len(t)))
            audio = (
                0.30 * np.sin(2 * np.pi * f0 * t + jitter_phase * 0.1) +
                0.15 * np.sin(2 * np.pi * 2 * f0 * t) +
                0.18 * np.sin(2 * np.pi * 5500 * t) +  # 5.5 kHz vocoder artifact
                0.10 * np.sin(2 * np.pi * 6800 * t) +  # 6.8 kHz artifact
                np.random.normal(0, 0.015, len(t))
            ).astype(np.float32)
            feat = _extract_features(audio, sr)
            if feat is not None:
                X_list.append(feat)
                y_list.append(1)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    logger.info("Extracted %d feature vectors across %d dimensions", len(X), X.shape[1])

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    logger.info("Fitting LogisticRegression(C=1.0, max_iter=500)...")
    clf = LogisticRegression(C=1.0, max_iter=500, random_state=42)
    clf.fit(X_train_scaled, y_train)

    train_acc = clf.score(X_train_scaled, y_train)
    val_acc = clf.score(X_val_scaled, y_val)
    logger.info("Train Accuracy: %.2f%% | Val Accuracy: %.2f%%", train_acc * 100, val_acc * 100)

    val_probs = clf.predict_proba(X_val_scaled)[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(val_probs, y_val)

    bundle = {
        "clf": clf,
        "calibrator": calibrator,
        "scaler": scaler,
        "feature_dim": 25,
        "feature_names": [
            "hf_energy_ratio", "lf_energy_ratio", "mid_energy_ratio",
            "spectral_centroid_norm", "spectral_rolloff_norm", "spectral_flatness",
            "zcr", "phase_jitter", "spectral_bandwidth_norm",
            "contrast_0", "contrast_1", "contrast_2", "contrast_3", "contrast_4", "contrast_5",
            "mel_0", "mel_1", "mel_2", "mel_3",
            "log_rms_norm", "temporal_flatness_norm", "is_telephony",
            "hf_flatness", "hf_ratio_wideband", "phase_hf_interaction"
        ]
    }

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, str(out_file))
    logger.info("Successfully trained and saved model to %s", out_file.resolve())
    return bundle


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EchoGuard Audio Detector Head")
    parser.add_argument("--manifest", type=str, default=None, help="Path to manifest CSV (path,label)")
    parser.add_argument("--output", type=str, default="models/head.joblib", help="Target output joblib")
    args = parser.parse_args()

    train_head(manifest_path=args.manifest, output_path=args.output)
