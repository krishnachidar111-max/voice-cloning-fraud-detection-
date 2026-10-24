"""
EchoGuard AI - Voice Activity Detection (VAD) & Segmentation
Determines active voiced frames vs silence/pause in real-time streaming audio.
"""

import numpy as np
from typing import Tuple


class VoiceActivityDetector:
    """
    Lightweight energy and spectral entropy VAD.
    Optimized for streaming 16 kHz telephony audio without requiring external C libraries.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: float = 30.0,
        energy_threshold_ratio: float = 0.12,
        min_speech_duration_ms: float = 200.0
    ):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        self.energy_threshold_ratio = energy_threshold_ratio
        self.min_speech_frames = int(min_speech_duration_ms / frame_duration_ms)

    def is_speech(self, samples: np.ndarray) -> Tuple[bool, float]:
        """
        Analyzes audio segment and returns:
        (has_sufficient_speech, speech_ratio)
        """
        if len(samples) < self.frame_size:
            return False, 0.0

        num_frames = len(samples) // self.frame_size
        frame_energies = np.zeros(num_frames, dtype=np.float32)

        for i in range(num_frames):
            frame = samples[i * self.frame_size : (i + 1) * self.frame_size]
            frame_energies[i] = np.sqrt(np.mean(frame ** 2) + 1e-12)

        max_energy = np.max(frame_energies) if len(frame_energies) > 0 else 0.0

        # Absolute noise floor gate: if max frame energy is very small, it's silence
        if max_energy < 0.003:
            return False, 0.0

        # Voiced threshold relative to peak energy
        voiced_threshold = max(0.003, max_energy * self.energy_threshold_ratio)
        voiced_mask = frame_energies >= voiced_threshold
        speech_ratio = float(np.mean(voiced_mask))
        num_voiced_frames = int(np.sum(voiced_mask))

        has_speech = (num_voiced_frames >= self.min_speech_frames) and (speech_ratio >= 0.15)
        return has_speech, speech_ratio
