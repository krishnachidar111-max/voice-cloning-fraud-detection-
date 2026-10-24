"""
EchoGuard AI - Evaluation Kit Runner (Spot-Check Harness)
Loads a directory of audio WAV files (e.g. Hackathon organizer's spot-check kit),
runs end-to-end detection & policy evaluation, and outputs a detailed results CSV.

Usage:
    python scripts/run_kit.py --input_dir data/spot_check_kit --output_csv reports/spot_check_results.csv
"""

import os
import sys
import argparse
import time
import csv
import glob
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from backend.audio.windows import AudioDecoder
from backend.models.infer import AudioInferenceEngine
from backend.fusion.policy import PolicyEngine
from backend.fusion.accumulator import EvidenceAccumulator
from backend.signals.transaction import get_transaction_signal
from backend.signals.interaction import get_interaction_signal


def parse_ground_truth(filename: str) -> str:
    """
    Infers expected ground truth from standard dataset naming conventions:
    - contains 'bonafide', 'real', 'human', 'genuine' -> bonafide
    - contains 'spoof', 'fake', 'synth', 'clone', 'deepfake' -> synthetic
    - otherwise -> unknown
    """
    fn = filename.lower()
    if any(k in fn for k in ["bonafide", "real", "human", "genuine", "legit"]):
        return "bonafide"
    elif any(k in fn for k in ["spoof", "fake", "synth", "clone", "deepfake", "elevenlabs", "vits"]):
        return "synthetic"
    return "unknown"


def run_spot_check(input_dir: str, output_csv: str) -> None:
    print("=" * 70)
    print("       EchoGuard AI - Spot-Check Kit Evaluation Harness")
    print("=" * 70)
    print(f"Target Directory: {input_dir}")
    print(f"Output Report:    {output_csv}\n")

    in_path = Path(input_dir)
    if not in_path.exists():
        print(f"[ERROR] Input directory '{input_dir}' not found.")
        print("[INFO] Creating demo mock samples for verification...")
        in_path.mkdir(parents=True, exist_ok=True)
        # Create at least 2 synthetic test files if empty
        _create_mock_spot_samples(in_path)

    wav_files = sorted(list(in_path.glob("*.wav")) + list(in_path.glob("*.mp3")) + list(in_path.glob("*.flac")))
    if not wav_files:
        print(f"[WARN] No audio files found in {input_dir}. Generating sample test audio...")
        _create_mock_spot_samples(in_path)
        wav_files = sorted(list(in_path.glob("*.wav")))

    print(f"Found {len(wav_files)} audio samples for spot-check evaluation.\n")

    decoder = AudioDecoder()
    inference_engine = AudioInferenceEngine()
    policy_engine = PolicyEngine()

    results = []
    total_processed = 0
    correct_count = 0
    evaluable_count = 0
    tier_counts = {"GREEN": 0, "AMBER": 0, "ORANGE": 0, "RED": 0}

    for idx, file_path in enumerate(wav_files, 1):
        filename = file_path.name
        expected = parse_ground_truth(filename)

        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        start_time = time.time()
        try:
            samples, sr = decoder.decode(audio_bytes)
            duration_s = round(len(samples) / float(sr), 2)
            audio_signal = inference_engine.analyze(samples, sr)
        except Exception as e:
            print(f"  [{idx:03d}] Error decoding {filename}: {str(e)}")
            continue

        latency_ms = round((time.time() - start_time) * 1000.0, 2)

        # Baseline interaction and low-risk transaction context
        interaction_signal = get_interaction_signal()
        txn_signal = get_transaction_signal("balance_inquiry", 0.0)

        # Policy tier evaluation
        accumulator = EvidenceAccumulator()
        accumulator.add_window(audio_signal.llr, interaction_signal.llr, txn_signal.llr)
        verdict = policy_engine.evaluate(
            session_id=f"SPOT-{idx:04d}",
            window_index=1,
            accumulator=accumulator,
            audio_signal=audio_signal,
            interaction_signal=interaction_signal,
            txn_signal=txn_signal
        )

        predicted = "synthetic" if audio_signal.synthetic_prob >= 0.50 else "bonafide"
        is_correct = "N/A"
        if expected != "unknown":
            evaluable_count += 1
            if predicted == expected:
                correct_count += 1
                is_correct = "TRUE"
            else:
                is_correct = "FALSE"

        tier = verdict.tier
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        total_processed += 1

        reason_codes_str = "; ".join([r.code for r in verdict.reason_codes])

        results.append({
            "sample_index": idx,
            "filename": filename,
            "duration_s": duration_s,
            "expected_label": expected,
            "predicted_label": predicted,
            "synthetic_score": round(audio_signal.synthetic_prob, 4),
            "calibrated_llr": round(audio_signal.llr, 4),
            "tier": tier,
            "risk_score": round(verdict.risk_score, 2),
            "is_correct": is_correct,
            "reason_codes": reason_codes_str,
            "latency_ms": latency_ms
        })

        status_marker = "OK" if is_correct == "TRUE" else ("FAIL" if is_correct == "FALSE" else "--")
        print(f"[{idx:03d}/{len(wav_files):03d}] {filename[:30]:30s} | Exp: {expected:9s} | Pred: {predicted:9s} | Tier: {tier:6s} | Latency: {latency_ms:5.1f}ms [{status_marker}]")

    # Save to CSV
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    fieldnames = [
        "sample_index", "filename", "duration_s", "expected_label", "predicted_label",
        "synthetic_score", "calibrated_llr", "tier", "risk_score", "is_correct",
        "reason_codes", "latency_ms"
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 70)
    print("                     EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Audio Samples Evaluated: {total_processed}")
    if evaluable_count > 0:
        accuracy = (correct_count / evaluable_count) * 100.0
        print(f"Samples with Ground Truth:    {evaluable_count}")
        print(f"Correctly Classified:         {correct_count}")
        print(f"Spot-Check Accuracy:          {accuracy:.2f}%")
    print("\nTier Distribution:")
    for t in ["GREEN", "AMBER", "ORANGE", "RED"]:
        cnt = tier_counts.get(t, 0)
        pct = (cnt / total_processed * 100.0) if total_processed > 0 else 0.0
        print(f"  - {t:6s}: {cnt:3d} ({pct:5.1f}%)")
    print(f"\nReport generated and saved to: {output_csv}")
    print("=" * 70)


def _create_mock_spot_samples(target_dir: Path):
    """Generates synthetic wav files for spot-check testing if directory is empty."""
    import wave
    sr = 16000
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)

    # 1. Bona fide clean speech harmonic
    bonafide = (0.4 * np.sin(2 * np.pi * 220 * t) + 0.2 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    # 2. Synthetic speech with high-frequency vocoder phase artifact (5.5kHz - 7.5kHz buzz)
    synth = bonafide + 0.15 * np.sin(2 * np.pi * 6200 * t) + 0.08 * np.sin(2 * np.pi * 7100 * t)

    def write_wav(path: Path, data: np.ndarray):
        int_data = (data * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(int_data.tobytes())

    write_wav(target_dir / "sample_01_bonafide_hindi_customer.wav", bonafide)
    write_wav(target_dir / "sample_02_spoof_elevenlabs_clone.wav", synth)
    write_wav(target_dir / "sample_03_bonafide_accented_elderly.wav", bonafide)
    write_wav(target_dir / "sample_04_spoof_vits_neural_vocoder.wav", synth)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EchoGuard AI Spot-Check Evaluation Harness")
    parser.add_argument("--input_dir", type=str, default="data/spot_check_kit", help="Directory containing audio files")
    parser.add_argument("--output_csv", type=str, default="reports/spot_check_results.csv", help="Path to save output CSV")
    args = parser.parse_args()

    run_spot_check(args.input_dir, args.output_csv)
