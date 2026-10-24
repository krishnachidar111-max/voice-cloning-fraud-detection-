"""EchoGuard Audio Processing Package"""
from .augment import (
    mu_law_encode,
    mu_law_decode,
    apply_g711_telephony,
    apply_bandpass_telephony,
    apply_packet_loss,
    add_acoustic_noise,
    TelephonyAugmenter,
)

__all__ = [
    "mu_law_encode",
    "mu_law_decode",
    "apply_g711_telephony",
    "apply_bandpass_telephony",
    "apply_packet_loss",
    "add_acoustic_noise",
    "TelephonyAugmenter",
]
