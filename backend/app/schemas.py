"""
EchoGuard AI - Core Pydantic Schemas and API Contracts
Provides strict typed contracts for:
- WebSocket audio streaming & real-time verdicts
- Multi-family signals (Audio, Interaction, Transaction)
- Four-tier policy ladder & reason codes
- Out-of-band customer verification & UPI hook
- Analyst case management & immutable audit logs
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ---------------------------------------------------------
# Signal Family Schemas
# ---------------------------------------------------------

class AudioSignal(BaseModel):
    synthetic_prob: float = Field(..., ge=0.0, le=1.0, description="Calibrated synthetic speech probability")
    llr: float = Field(..., description="Calibrated log-likelihood ratio for audio evidence")
    spectral_anomaly_score: float = Field(..., ge=0.0, le=1.0)
    hf_energy_ratio: float = Field(..., ge=0.0, le=1.0, description="High-frequency vocoder band energy ratio")
    spectral_flatness: float = Field(..., ge=0.0, le=1.0)
    channel_replay_score: float = Field(0.0, ge=0.0, le=1.0)
    is_silent: bool = False
    is_telephony_degraded: bool = False
    latency_ms: float = 0.0


class InteractionSignal(BaseModel):
    response_latency_s: float = Field(0.0, ge=0.0, description="Speaker response latency in seconds")
    turn_taking_jitter_s: float = Field(0.0, ge=0.0)
    prosodic_variance: float = Field(1.0, ge=0.0, description="Pitch & cadence variance (robotic speech has low variance)")
    unscripted_challenge_latency_s: Optional[float] = Field(None, description="Latency on unscripted challenge question")
    caller_ani_reputation: float = Field(0.0, ge=0.0, le=1.0, description="ANI/Caller ID spoofing risk score")
    llr: float = Field(0.0, description="Log-likelihood ratio for interaction cues")


class TransactionSignal(BaseModel):
    action_type: Literal[
        "balance_inquiry",
        "mini_statement",
        "bill_payment",
        "add_payee",
        "raise_limit",
        "credentials_reset",
        "sim_swap_signal",
        "upi_collect_request",
        "upi_transfer",
        "wire_transfer"
    ] = "balance_inquiry"
    amount: float = Field(0.0, ge=0.0)
    is_novel_payee: bool = False
    velocity_1h_count: int = Field(0, ge=0)
    recent_credential_change_24h: bool = False
    mule_account_risk_score: float = Field(0.0, ge=0.0, le=1.0)
    llr: float = Field(0.0, description="Log-likelihood ratio for financial risk")


# ---------------------------------------------------------
# Policy & Verdict Schemas
# ---------------------------------------------------------

class ReasonCode(BaseModel):
    code: str
    family: Literal["AUDIO", "INTERACTION", "TRANSACTION", "SYSTEM"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str
    plain_language_explanation: str


class StreamingVerdict(BaseModel):
    session_id: str
    timestamp: str
    window_index: int
    tier: Literal["GREEN", "AMBER", "ORANGE", "RED"]
    risk_score: float
    accumulated_evidence: float
    llr_audio: float
    llr_interaction: float
    llr_transaction: float
    reason_codes: List[ReasonCode]
    safety_rule_applied: Optional[str] = None
    audio_persisted_bytes: int = 0
    processing_latency_ms: float
    agent_guidance: str
    recommended_action: str


# ---------------------------------------------------------
# Out-of-Band & UPI Verification Schemas
# ---------------------------------------------------------

class VerificationRequest(BaseModel):
    session_id: str
    action_type: str
    amount: float
    payee_name: Optional[str] = None
    account_number_masked: Optional[str] = None
    upi_id_masked: Optional[str] = None


class VerificationChallenge(BaseModel):
    challenge_id: str
    session_id: str
    token: str
    action_type: str
    amount: float
    payee: str
    number_matching_code: int = Field(..., ge=10, le=99)
    status: Literal["PENDING", "APPROVED", "DENIED", "EXPIRED"] = "PENDING"
    expires_at: str
    created_at: str


class VerificationResponse(BaseModel):
    challenge_id: str
    decision: Literal["APPROVE", "DENY"]
    entered_matching_code: Optional[int] = None
    device_biometric_passed: bool = True


class UPIInterceptRequest(BaseModel):
    session_id: str
    upi_collect_vpa: str
    amount: float
    payer_vpa: str
    urgency_flag: bool = False


class UPIInterceptResult(BaseModel):
    is_blocked: bool
    status: Literal["PASSED", "INTERCEPTED", "BLOCKED"]
    tier: str
    warning_title: str
    warning_message: str
    required_cooling_off_seconds: int = 0
    out_of_band_token_required: bool = False


# ---------------------------------------------------------
# Analyst & Case Management Schemas
# ---------------------------------------------------------

class CaseSummary(BaseModel):
    case_id: str
    session_id: str
    customer_id_masked: str
    tier: Literal["AMBER", "ORANGE", "RED"]
    risk_score: float
    action_attempted: str
    amount: float
    status: Literal["ACTIVE_HOLD", "RELEASED", "CONFIRMED_FRAUD", "AUTO_CLEARED", "APPEALED"]
    created_at: str
    updated_at: str
    reason_codes: List[ReasonCode]
    has_dual_control_requirement: bool
    first_analyst_id: Optional[str] = None
    second_analyst_id: Optional[str] = None
    audio_clip_available: bool = False


class CaseActionRequest(BaseModel):
    analyst_id: str
    action: Literal["HOLD", "RELEASE", "CONFIRM_FRAUD"]
    notes: str


class CustomerAppealRequest(BaseModel):
    case_id: str
    session_id: str
    customer_id: str
    contact_number: str
    appeal_reason: str


class CustomerAppealResult(BaseModel):
    case_id: str
    status: Literal["OVERTURNED", "UPHELD", "PENDING_REVIEW"]
    why_it_fired: str
    resolution_time_seconds: float
    fairness_reassurance: str


# ---------------------------------------------------------
# Audit Trail Schema
# ---------------------------------------------------------

class AuditLogEntry(BaseModel):
    log_id: int
    timestamp: str
    actor_id: str
    action: str
    case_id: Optional[str] = None
    session_id: Optional[str] = None
    reason: str
    ip_address: str
    previous_hash: str
    current_hash: str
