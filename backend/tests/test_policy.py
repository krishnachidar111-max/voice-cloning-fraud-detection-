"""
Unit tests for EchoGuard Four-Tier Policy Engine & Safety Invariants.
Verifies Hard Rule 3 and FR-13:
- Audio evidence alone is strictly capped at ORANGE (never RED).
- RED requires corroboration from at least 2 families or an out-of-band failure.
- Neutral agent prompts without accusatory language or scores.
"""

import pytest
from backend.app.schemas import AudioSignal, InteractionSignal, TransactionSignal
from backend.fusion.accumulator import EvidenceAccumulator
from backend.fusion.policy import PolicyEngine


@pytest.fixture
def policy_engine():
    return PolicyEngine(tau1=1.25, tau2=2.80, tau3=4.50)


@pytest.fixture
def accumulator():
    return EvidenceAccumulator()


def test_green_tier_for_benign_customer(policy_engine, accumulator):
    """Verifies low-risk, natural customer interaction passes smoothly as GREEN."""
    audio = AudioSignal(
        synthetic_prob=0.08,
        llr=-2.4,
        spectral_anomaly_score=0.05,
        hf_energy_ratio=0.10,
        spectral_flatness=0.15,
        channel_replay_score=0.0,
        is_silent=False,
        is_telephony_degraded=False,
        latency_ms=15.0
    )
    interaction = InteractionSignal(response_latency_s=0.7, turn_taking_jitter_s=0.1, prosodic_variance=0.9, caller_ani_reputation=0.05, llr=-1.2)
    txn = TransactionSignal(action_type="balance_inquiry", amount=0.0, is_novel_payee=False, velocity_1h_count=1, recent_credential_change_24h=False, mule_account_risk_score=0.0, llr=-2.5)

    accumulator.add_window(audio.llr, interaction.llr, txn.llr)
    verdict = policy_engine.evaluate("SESS-001", 1, accumulator, audio, interaction, txn)

    assert verdict.tier == "GREEN"
    assert verdict.risk_score < 1.25
    assert "Standard customer servicing" in verdict.agent_guidance
    assert verdict.audio_persisted_bytes == 0


def test_safety_rule_1_audio_alone_cannot_trigger_red(policy_engine, accumulator):
    """
    CRITICAL INVARIANT TEST:
    Even if the synthetic speech detector emits MAXIMUM confidence (LLR = +5.0),
    if other families are benign/neutral, policy engine MUST CAP the tier at ORANGE.
    Audio alone can NEVER freeze an account (trigger RED).
    """
    # Overwhelming synthetic speech score
    audio = AudioSignal(
        synthetic_prob=0.99,
        llr=5.0,
        spectral_anomaly_score=0.95,
        hf_energy_ratio=0.75,
        spectral_flatness=0.80,
        channel_replay_score=0.2,
        is_silent=False,
        is_telephony_degraded=False,
        latency_ms=18.0
    )
    # Natural interaction and low-risk transaction
    interaction = InteractionSignal(response_latency_s=0.8, turn_taking_jitter_s=0.1, prosodic_variance=0.85, caller_ani_reputation=0.1, llr=0.0)
    txn = TransactionSignal(action_type="balance_inquiry", amount=0.0, is_novel_payee=False, velocity_1h_count=0, recent_credential_change_24h=False, mule_account_risk_score=0.0, llr=-2.0)

    # Force accumulator risk score above TAU_3 (4.50)
    accumulator.current_evidence = 4.80

    verdict = policy_engine.evaluate("SESS-002", 2, accumulator, audio, interaction, txn)

    # MUST be capped at ORANGE
    assert verdict.tier == "ORANGE"
    assert verdict.safety_rule_applied == "SAFETY_RULE_1_AUDIO_ALONE_CAPPED_AT_ORANGE"
    assert "Secondary authentication required" in verdict.agent_guidance
    assert "Mandatory mobile app approval in progress" in verdict.recommended_action


def test_corroborated_red_tier_with_two_families(policy_engine, accumulator):
    """
    Verifies RED tier triggers when synthetic audio is corroborated by high transaction risk (2 families).
    """
    audio = AudioSignal(
        synthetic_prob=0.94,
        llr=4.2,
        spectral_anomaly_score=0.85,
        hf_energy_ratio=0.65,
        spectral_flatness=0.70,
        channel_replay_score=0.1,
        is_silent=False,
        is_telephony_degraded=False,
        latency_ms=18.0
    )
    interaction = InteractionSignal(response_latency_s=1.6, turn_taking_jitter_s=0.4, prosodic_variance=0.3, caller_ani_reputation=0.4, llr=1.2)
    txn = TransactionSignal(action_type="add_payee", amount=85000.0, is_novel_payee=True, velocity_1h_count=2, recent_credential_change_24h=True, mule_account_risk_score=0.8, llr=4.5)

    accumulator.current_evidence = 5.20

    verdict = policy_engine.evaluate("SESS-003", 3, accumulator, audio, interaction, txn)

    assert verdict.tier == "RED"
    assert verdict.safety_rule_applied is None
    assert "Security policy hold triggered" in verdict.agent_guidance


def test_out_of_band_failure_escalates_to_red(policy_engine, accumulator):
    """
    Verifies that if customer denies out-of-band push verification,
    the session immediately escalates to RED regardless of scores.
    """
    audio = AudioSignal(
        synthetic_prob=0.45,
        llr=0.2,
        spectral_anomaly_score=0.2,
        hf_energy_ratio=0.2,
        spectral_flatness=0.2,
        channel_replay_score=0.0,
        is_silent=False,
        is_telephony_degraded=False,
        latency_ms=12.0
    )
    interaction = InteractionSignal(llr=0.1)
    txn = TransactionSignal(action_type="raise_limit", amount=50000.0, llr=1.0)

    accumulator.current_evidence = 1.80  # Normally AMBER

    # Out-of-band push was DENIED by real customer
    verdict = policy_engine.evaluate("SESS-004", 4, accumulator, audio, interaction, txn, out_of_band_failed=True)

    assert verdict.tier == "RED"
    assert "Security policy hold triggered" in verdict.agent_guidance


def test_neutral_agent_guidance_invariants(policy_engine, accumulator):
    """Verifies frontline agent guidance never contains accusations or technical scores."""
    audio = AudioSignal(synthetic_prob=0.98, llr=4.5, spectral_anomaly_score=0.9, hf_energy_ratio=0.8, spectral_flatness=0.8, channel_replay_score=0.0, is_silent=False, is_telephony_degraded=False, latency_ms=15.0)
    interaction = InteractionSignal(llr=1.5)
    txn = TransactionSignal(action_type="add_payee", amount=50000.0, llr=3.0)
    accumulator.current_evidence = 4.90

    verdict = policy_engine.evaluate("SESS-005", 5, accumulator, audio, interaction, txn)

    # Check guidance text
    forbidden_terms = ["fake", "clone", "deepfake", "fraudster", "criminal", "score:"]
    guidance_lower = verdict.agent_guidance.lower()
    for term in forbidden_terms:
        assert term not in guidance_lower, f"Forbidden term '{term}' found in agent guidance!"
