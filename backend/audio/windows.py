"""
EchoGuard AI - Audio Decoding & Window Slicing Pipeline
Decodes raw audio bytes to 16 kHz float32 mono PCM and yields 2-second windows (1-second hop).
"""

import io
import wave
import numpy as np
from scipy import signal
from typing import Tuple, List, Generator
from .vad import VoiceActivityDetector


class AudioDecoder:
    """
    Decodes audio bytes (WAV, PCM) and resamples to target sample rate (16000 Hz mono).
    """

    TARGET_SR = 16000

    @classmethod
    def decode(cls, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """
        Decodes arbitrary incoming audio payload to normalized float32 samples.
        """
        if not audio_bytes:
            return np.zeros(0, dtype=np.float32), cls.TARGET_SR

        # 1. Attempt standard WAV format decode
        try:
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                raw_frames = wav_file.readframes(n_frames)

                if sample_width == 1:
                    data = (np.frombuffer(raw_frames, dtype=np.uint8).astype(np.float32) - 128) / 128.0
                elif sample_width == 2:
                    data = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32) / 32768.0
                elif sample_width == 4:
                    data = np.frombuffer(raw_frames, dtype=np.int32).astype(np.float32) / 2147483648.0
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")

                if n_channels > 1:
                    data = data.reshape(-1, n_channels).mean(axis=1)

                if framerate != cls.TARGET_SR:
                    target_length = int(len(data) * cls.TARGET_SR / framerate)
                    data = signal.resample(data, target_length)

                return np.asarray(data, dtype=np.float32), cls.TARGET_SR
        except Exception:
            pass

        # 2. Raw headerless 16-bit PCM fallback (common in WebSockets)
        try:
            num_samples = len(audio_bytes) // 2
            if num_samples > 0:
                data = np.frombuffer(audio_bytes[:num_samples * 2], dtype=np.int16).astype(np.float32) / 32768.0
                return data, cls.TARGET_SR
        except Exception:
            pass

        raise ValueError("Could not decode audio payload. Ensure valid WAV or 16-bit PCM.")


class StreamingWindowProcessor:
    """
    Splits continuous streaming audio into 2-second windows with 1-second step (50% overlap).
    """

    def __init__(
        self,
        window_duration_s: float = 2.0,
        hop_duration_s: float = 1.0,
        sample_rate: int = 16000
    ):
        self.sample_rate = sample_rate
        self.window_size = int(window_duration_s * sample_rate)
        self.hop_size = int(hop_duration_s * sample_rate)
        self.vad = VoiceActivityDetector(sample_rate=sample_rate)

    def process_stream(self, samples: np.ndarray) -> Generator[Tuple[int, np.ndarray, bool], None, None]:
        """
        Yields (window_index, window_samples, is_voiced_speech) for all overlapping windows.
        """
        if len(samples) < self.window_size:
            # Pad short sample to window size if >= 0.5s
            if len(samples) >= self.sample_rate * 0.5:
                padded = np.pad(samples, (0, self.window_size - len(samples)))
                has_speech, _ = self.vad.is_speech(padded)
                yield 0, padded, has_speech
            return

        window_idx = 0
        current_start = 0
        while current_start + self.window_size <= len(samples):
            window = samples[current_start : current_start + self.window_size]
            has_speech, _ = self.vad.is_speech(window)
            yield window_idx, window, has_speech
            window_idx += 1
            current_start += self.hop_size
