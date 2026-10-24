"""
EchoGuard AI - 10-Second Volatile In-Memory Audio Ring Buffer
Fulfills FR-3 and Hard Rule 2 (Zero-Disk Audio Retention Policy).

Features:
- Fixed-capacity circular memory buffer storing 16 kHz float32 samples.
- Strictly lives in RAM; never serialized or written to persistent storage.
- Automatically purges audio upon call termination.
- Exposes real-time persisted byte count (guaranteed 0 bytes to disk).
"""

import threading
import numpy as np
from typing import Tuple, Optional


class MemoryRingBuffer:
    """
    Thread-safe circular audio buffer stored exclusively in RAM.
    Capacity: 10 seconds of 16 kHz mono float32 audio (160,000 samples = ~640 KB RAM).
    """

    def __init__(self, capacity_seconds: float = 10.0, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.capacity_samples = int(capacity_seconds * sample_rate)
        self.buffer = np.zeros(self.capacity_samples, dtype=np.float32)
        self.write_pos = 0
        self.total_samples_written = 0
        self.lock = threading.Lock()
        self.persisted_disk_bytes = 0  # Invariant: Must strictly remain 0

    def append(self, samples: np.ndarray) -> None:
        """
        Appends new float32 audio samples into the circular buffer.
        Overwrites oldest samples once 10 seconds capacity is reached.
        """
        if len(samples) == 0:
            return

        with self.lock:
            samples_flat = samples.flatten().astype(np.float32)
            n_samples = len(samples_flat)

            if n_samples >= self.capacity_samples:
                # If incoming chunk exceeds capacity, keep only the latest slice
                self.buffer[:] = samples_flat[-self.capacity_samples:]
                self.write_pos = 0
            else:
                end_pos = self.write_pos + n_samples
                if end_pos <= self.capacity_samples:
                    self.buffer[self.write_pos:end_pos] = samples_flat
                    self.write_pos = end_pos % self.capacity_samples
                else:
                    first_part = self.capacity_samples - self.write_pos
                    self.buffer[self.write_pos:] = samples_flat[:first_part]
                    second_part = n_samples - first_part
                    self.buffer[:second_part] = samples_flat[first_part:]
                    self.write_pos = second_part

            self.total_samples_written += n_samples

    def get_latest(self, duration_seconds: float = 2.0) -> np.ndarray:
        """
        Retrieves the most recent N seconds of audio in chronological order.
        """
        with self.lock:
            n_requested = int(duration_seconds * self.sample_rate)
            n_available = min(self.total_samples_written, self.capacity_samples)
            n_return = min(n_requested, n_available)

            if n_return <= 0:
                return np.zeros(0, dtype=np.float32)

            # Circular extraction of the last n_return samples
            indices = (self.write_pos - n_return + np.arange(n_return)) % self.capacity_samples
            return self.buffer[indices].copy()

    def purge(self) -> None:
        """
        Immediate zeroization of volatile buffer memory upon call hangup or termination.
        Ensures customer voice data does not linger in memory.
        """
        with self.lock:
            self.buffer.fill(0.0)
            self.write_pos = 0
            self.total_samples_written = 0

    @property
    def disk_persisted_bytes(self) -> int:
        """Guaranteed 0 bytes. Used for UI badge & compliance auditing."""
        return 0

    @property
    def memory_footprint_bytes(self) -> int:
        """Volatile RAM consumption in bytes."""
        return self.buffer.nbytes
