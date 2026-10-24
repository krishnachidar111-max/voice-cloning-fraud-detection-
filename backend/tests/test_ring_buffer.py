"""
Unit tests for 10-Second Volatile In-Memory Ring Buffer.
Verifies circular overwriting, retrieval chronological ordering, and memory zeroization.
"""

import numpy as np
import pytest
from backend.audio.ring_buffer import MemoryRingBuffer


def test_ring_buffer_capacity_and_retrieval():
    buffer = MemoryRingBuffer(capacity_seconds=2.0, sample_rate=1000)
    assert buffer.capacity_samples == 2000

    # Write 1000 samples of 1.0s
    chunk1 = np.ones(1000, dtype=np.float32)
    buffer.append(chunk1)
    retrieved = buffer.get_latest(duration_seconds=1.0)
    assert len(retrieved) == 1000
    assert np.all(retrieved == 1.0)

    # Write 1500 samples of 2.0s (triggers circular wrap)
    chunk2 = np.full(1500, 2.0, dtype=np.float32)
    buffer.append(chunk2)

    # Retrieval of last 1.0s (1000 samples) should contain exclusively chunk2
    retrieved_latest = buffer.get_latest(duration_seconds=1.0)
    assert len(retrieved_latest) == 1000
    assert np.all(retrieved_latest == 2.0)


def test_ring_buffer_purge():
    buffer = MemoryRingBuffer(capacity_seconds=5.0, sample_rate=16000)
    samples = np.random.normal(0, 1, 32000).astype(np.float32)
    buffer.append(samples)

    assert buffer.total_samples_written == 32000

    # Purge memory
    buffer.purge()

    assert buffer.total_samples_written == 0
    assert buffer.write_pos == 0
    assert np.all(buffer.buffer == 0.0)
    assert buffer.disk_persisted_bytes == 0
