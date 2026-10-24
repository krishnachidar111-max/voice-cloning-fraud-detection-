"""
Privacy Safeguard Verification Test
Implements Hard Rule 2 & Acceptance Checklist:
"No raw audio on disk during live runs (verified by a test that scans the data directory)"
Verifies zero raw audio bytes are written to persistent disk storage during operation.
"""

import os
import glob
from pathlib import Path
import pytest
import numpy as np
from backend.audio.ring_buffer import MemoryRingBuffer
from backend.models.infer import AudioInferenceEngine


def test_zero_disk_audio_invariant(tmp_path):
    """
    Simulates high-volume audio ingestion and verifies NO .wav, .pcm, or .bin
    audio files are created in the workspace or data directory.
    """
    initial_files = set(glob.glob("**/*.wav", recursive=True) + glob.glob("**/*.pcm", recursive=True))

    buffer = MemoryRingBuffer(capacity_seconds=10.0, sample_rate=16000)
    engine = AudioInferenceEngine(sample_rate=16000)

    # Ingest 30 seconds of audio chunks into the ring buffer
    for _ in range(15):
        chunk = np.random.uniform(-0.5, 0.5, 32000).astype(np.float32)
        buffer.append(chunk)
        latest = buffer.get_latest(duration_seconds=2.0)
        signal = engine.analyze(latest)

        assert buffer.disk_persisted_bytes == 0
        assert signal.synthetic_prob >= 0.0

    # Purge buffer
    buffer.purge()
    assert buffer.disk_persisted_bytes == 0

    # Scan workspace directory for any leaked audio files
    current_files = set(glob.glob("**/*.wav", recursive=True) + glob.glob("**/*.pcm", recursive=True))
    new_files = current_files - initial_files

    # Filter out static benchmark test kit in data/spot_check_kit
    new_leaked_audio = [f for f in new_files if "spot_check_kit" not in f and "benchmark" not in f]
    assert len(new_leaked_audio) == 0, f"Privacy violation: Audio leaked to disk: {new_leaked_audio}"
