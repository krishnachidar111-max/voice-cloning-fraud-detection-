"""
EchoGuard AI - Central Configuration & Threshold Settings
Versioned, environment-overridable configuration.
Loaded from environment variables or safe defaults.
"""

from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class EchoGuardSettings(BaseSettings):
    # Application & Environment
    APP_NAME: str = "Phantom Trace"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Detector Backend Selection
    # 'learned' = use models/head.joblib when present (falls back to spectral).
    # 'spectral' = always use the hand-tuned spectral heuristic.
    DETECTOR_BACKEND: str = "learned"
    DETECTOR_MODEL_PATH: str = ""  # overrides default models/head.joblib path when set

    # Offline enforcement (never call HuggingFace Hub at runtime)
    HF_HUB_OFFLINE: str = "1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Audio Ingestion & Buffer Constraints (RAM-Only Privacy Guarantee)
    TARGET_SAMPLE_RATE: int = 16000
    AUDIO_WINDOW_SECONDS: float = 2.0
    AUDIO_HOP_SECONDS: float = 1.0
    RING_BUFFER_SECONDS: float = 10.0
    MIN_SPEECH_DURATION_SECONDS: float = 0.5
    MAX_ALLOWABLE_CLIP_RETENTION_SECONDS: float = 30.0  # Only for Orange/Red audit

    # Signal Family Weights in Evidence Accumulation (Σ w_f = 1.0)
    WEIGHT_AUDIO: float = 0.45
    WEIGHT_INTERACTION: float = 0.25
    WEIGHT_TRANSACTION: float = 0.30

    # Evidence Accumulator Dynamics
    ACCUMULATOR_DECAY: float = 0.82       # lambda decay per time window
    ACCUMULATOR_CLIP_LOWER: float = -4.0   # evidence saturation bounds
    ACCUMULATOR_CLIP_UPPER: float = +6.0

    # Policy Ladder Risk Thresholds
    # Green: R < TAU_1 (Pass silently)
    # Amber: TAU_1 <= R < TAU_2 (In-App Step-up Push)
    # Orange: TAU_2 <= R < TAU_3 (Out-of-band mandatory verification + unscripted challenge)
    # Red: R >= TAU_3 or failed approval (Immediate security hold + analyst triage)
    TAU_1_AMBER: float = 1.25
    TAU_2_ORANGE: float = 2.80
    TAU_3_RED: float = 4.50

    # Safety Invariants Enforced in Code
    MAX_TIER_FOR_AUDIO_ALONE: str = "ORANGE"
    MIN_FAMILIES_FOR_UNILATERAL_RED: int = 2

    # High-Value Transaction Dual-Control Threshold
    DUAL_APPROVAL_THRESHOLD_INR: float = 50000.0  # ₹50,000 / $10,000 threshold

    # Database & Audit Paths
    DATABASE_URL: str = "sqlite:///./echoguard.db"
    AUDIT_CHAIN_SALT: str = "EchoGuard-IITDelhi-2026-ImmutableAuditSalt"

    model_config = SettingsConfigDict(env_prefix="ECHOGUARD_", case_sensitive=True)

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        import os
        os.environ.setdefault("HF_HUB_OFFLINE", self.HF_HUB_OFFLINE)


settings = EchoGuardSettings()
