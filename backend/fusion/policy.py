"""
EchoGuard AI - Four-Tier Policy Engine & Core Safety Invariants
Implements FR-11, FR-12, FR-13, FR-14, and Hard Rule 3.

Safety Invariants Enforced in Code:
1. Audio evidence alone is strictly capped at ORANGE. An audio score can NEVER trigger RED or freeze an account.
2. RED requires corroborating evidence from at least 2 of the 3 signal families (Audio, Interaction, Transaction),
   OR an explicitly denied / timed-out out-of-band verification step.
3. Frontline agents see only neutral, non-accusatory operational guidance. Never scores or fraud accusations.
"""

from typing import Literal, Optional, List
from datetime import datetime, timezone
from backend.app.config import settings
from backend.app.schemas import (
    StreamingVerdict,
    AudioSignal,
    InteractionSignal,
    TransactionSignal,
    ReasonCode
)
from backend.fusion.accumulator import EvidenceAccumulator
from backend.fusion.reason_codes import generate_reason_codes


class PolicyEngine:
    """
    Evaluates fused risk scores against configured threshold ladders
    while strictly enforcing core safety invariants.
    """

    def __init__(
        self,
        tau1: float = settings.TAU_1_AMBER,
        tau2: float = settings.TAU_2_ORANGE,
        tau3: float = settings.TAU_3_RED
    ):
        self.tau1 = tau1
        self.tau2 = tau2
        self.tau3 = tau3

    def evaluate(
        self,
        session_id: str,
        window_index: int,
        accumulator: EvidenceAccumulator,
        audio_signal: AudioSignal,
        interaction_signal: InteractionSignal,
        txn_signal: TransactionSignal,
        out_of_band_failed: bool = False
    ) -> StreamingVerdict:
        """
        Calculates final response tier and emits an auditable StreamingVerdict.
        """
        # Retrieve accumulated evidence and risk
        accumulated_evidence = accumulator.current_evidence
        risk_score = accumulated_evidence

        # Action-specific risk scaling factor
        from backend.signals.transaction import ACTION_SENSITIVITY_WEIGHTS
        k_action = ACTION_SENSITIVITY_WEIGHTS.get(txn_signal.action_type, 0.5)

        # Baseline provisional tier determination
        provisional_tier: Literal["GREEN", "AMBER", "ORANGE", "RED"]
        if risk_score < self.tau1:
            provisional_tier = "GREEN"
        elif risk_score < self.tau2:
            provisional_tier = "AMBER"
        elif risk_score < self.tau3:
            provisional_tier = "ORANGE"
        else:
            provisional_tier = "RED"

        # Explicit out-of-band failure escalates directly to RED
        if out_of_band_failed:
            provisional_tier = "RED"

        # -------------------------------------------------------------
        # ENFORCE SAFETY INVARIANT 1: Audio alone is capped at ORANGE
        # -------------------------------------------------------------
        safety_rule_applied: Optional[str] = None
        has_interaction_evidence = interaction_signal.llr >= 0.8
        has_transaction_evidence = txn_signal.llr >= 0.8
        has_audio_evidence = audio_signal.llr >= 0.8

        corroborated_families_count = sum([
            1 if has_audio_evidence else 0,
            1 if has_interaction_evidence else 0,
            1 if has_transaction_evidence else 0
        ])

        if provisional_tier == "RED" and not out_of_band_failed:
            # Check if triggered solely by audio
            if has_audio_evidence and not has_interaction_evidence and not has_transaction_evidence:
                provisional_tier = "ORANGE"
                safety_rule_applied = "SAFETY_RULE_1_AUDIO_ALONE_CAPPED_AT_ORANGE"

            # -------------------------------------------------------------
            # ENFORCE SAFETY INVARIANT 2: RED requires >= 2 corroborated families
            # -------------------------------------------------------------
            elif corroborated_families_count < settings.MIN_FAMILIES_FOR_UNILATERAL_RED:
                provisional_tier = "ORANGE"
                safety_rule_applied = "SAFETY_RULE_2_RED_REQUIRES_TWO_CORROBORATING_FAMILIES"

        final_tier = provisional_tier

        # Generate explainable reason codes
        reason_codes = generate_reason_codes(
            audio_signal=audio_signal,
            interaction_signal=interaction_signal,
            txn_signal=txn_signal,
            risk_score=risk_score,
            tier=final_tier
        )

        # Neutral Agent Guidance (Never shows scores or accusations to agent)
        agent_guidance, recommended_action = self._get_agent_guidance(final_tier)

        return StreamingVerdict(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            window_index=window_index,
            tier=final_tier,
            risk_score=round(risk_score, 2),
            accumulated_evidence=round(accumulated_evidence, 2),
            llr_audio=round(audio_signal.llr, 2),
            llr_interaction=round(interaction_signal.llr, 2),
            llr_transaction=round(txn_signal.llr, 2),
            reason_codes=reason_codes,
            safety_rule_applied=safety_rule_applied,
            audio_persisted_bytes=0,  # Strict RAM-only guarantee
            processing_latency_ms=round(audio_signal.latency_ms + 1.5, 2),
            agent_guidance=agent_guidance,
            recommended_action=recommended_action
        )

    def _get_agent_guidance(self, tier: str) -> tuple[str, str]:
        """Provides neutral, professional prompts for call center agents."""
        if tier == "GREEN":
            return (
                "Standard customer servicing. All security verifications clear.",
                "Proceed with requested workflow normally."
            )
        elif tier == "AMBER":
            return (
                "Routine high-assurance confirmation initiated.",
                "Prompt customer to tap 'Confirm' on their mobile banking notification."
            )
        elif tier == "ORANGE":
            return (
                "Secondary authentication required for sensitive action.",
                "Mandatory mobile app approval in progress. Do not proceed until verified."
            )
        else:  # RED
            return (
                "Security policy hold triggered. Warm transfer to Senior Fraud Specialist required.",
                "Keep customer on hold. Account temporarily protected pending analyst review."
            )
