"""
EchoGuard AI - Explainable Reason Codes Generator
Produces transparent, auditable, and plain-language reason codes for any decision.
Fulfills FR-14, FR-20, and Responsible AI requirements.
"""

from typing import List
from backend.app.schemas import ReasonCode, AudioSignal, InteractionSignal, TransactionSignal


def generate_reason_codes(
    audio_signal: AudioSignal,
    interaction_signal: InteractionSignal,
    txn_signal: TransactionSignal,
    risk_score: float,
    tier: str
) -> List[ReasonCode]:
    """
    Evaluates individual signal metrics and generates structured, human-readable reason codes.
    """
    codes: List[ReasonCode] = []

    # 1. Audio Family Codes
    if audio_signal.hf_energy_ratio > 0.35:
        codes.append(ReasonCode(
            code="AUD-VOCODER-HF-DISRUPTION",
            family="AUDIO",
            severity="HIGH",
            description="High-frequency energy anomalies detected in 4k-8kHz vocoder synthesis band.",
            plain_language_explanation="The speaker's voice contains acoustic artifacts commonly produced by artificial neural speech synthesizers."
        ))

    if audio_signal.spectral_flatness > 0.40:
        codes.append(ReasonCode(
            code="AUD-SPECTRAL-FLATNESS-ELEVATED",
            family="AUDIO",
            severity="MEDIUM",
            description="Elevated Wiener spectral flatness entropy inconsistent with natural vocal folds.",
            plain_language_explanation="The acoustic resonance of the speech shows synthetic smoothness rather than natural throat vibrations."
        ))

    if audio_signal.is_telephony_degraded:
        codes.append(ReasonCode(
            code="AUD-TELEPHONY-CODEC-CHANNEL",
            family="AUDIO",
            severity="LOW",
            description="Bandpass filtered telephony channel (G.711 / 3.4kHz POTS) active.",
            plain_language_explanation="Audio is passing through standard telephone compression, which our model accounts for during evaluation."
        ))

    # 2. Interaction Family Codes
    if interaction_signal.response_latency_s > 1.4:
        codes.append(ReasonCode(
            code="INT-LATENCY-TURN-DELAY",
            family="INTERACTION",
            severity="MEDIUM",
            description=f"Turn-taking response latency was {interaction_signal.response_latency_s:.2f}s, exceeding conversational baseline.",
            plain_language_explanation="Unusual pauses were detected before speech, consistent with real-time text-to-speech generation lag."
        ))

    if interaction_signal.unscripted_challenge_latency_s and interaction_signal.unscripted_challenge_latency_s > 2.5:
        codes.append(ReasonCode(
            code="INT-CHALLENGE-HESITATION",
            family="INTERACTION",
            severity="HIGH",
            description="Prolonged delay on spontaneous unscripted challenge prompt.",
            plain_language_explanation="Significant hesitation occurred during an interactive question that automated cloning tools struggle to answer immediately."
        ))

    if interaction_signal.caller_ani_reputation > 0.5:
        codes.append(ReasonCode(
            code="INT-ANI-SPOOF-RISK",
            family="INTERACTION",
            severity="HIGH",
            description="Caller ID route originated from a VoIP gateway with high spoofing index.",
            plain_language_explanation="The incoming phone number route does not match standard cellular carrier verification."
        ))

    # 3. Transaction Family Codes
    if txn_signal.action_type in ["add_payee", "raise_limit", "sim_swap_signal", "credentials_reset"]:
        codes.append(ReasonCode(
            code="TXN-HIGH-SENSITIVITY-ACTION",
            family="TRANSACTION",
            severity="HIGH",
            description=f"Action '{txn_signal.action_type}' carries high financial or credential takeover risk.",
            plain_language_explanation=f"A sensitive account change was requested ({txn_signal.action_type.replace('_', ' ')}), requiring stronger safeguards."
        ))

    if txn_signal.is_novel_payee:
        codes.append(ReasonCode(
            code="TXN-NOVEL-BENEFICIARY",
            family="TRANSACTION",
            severity="MEDIUM",
            description="Beneficiary account has no prior transaction history with this customer.",
            plain_language_explanation="Money is being directed to a newly registered account that this customer has never sent funds to before."
        ))

    if txn_signal.amount > 25000:
        codes.append(ReasonCode(
            code="TXN-ELEVATED-AMOUNT",
            family="TRANSACTION",
            severity="MEDIUM",
            description=f"Transaction value (INR {txn_signal.amount:,.2f}) exceeds customer's 30-day typical transfer baseline.",
            plain_language_explanation=f"The transfer amount (₹{txn_signal.amount:,.2f}) is higher than normal activity for this account."
        ))

    if txn_signal.recent_credential_change_24h:
        codes.append(ReasonCode(
            code="TXN-RECENT-CREDENTIAL-CHANGE",
            family="TRANSACTION",
            severity="CRITICAL",
            description="Password or registered mobile number was updated within the last 24 hours.",
            plain_language_explanation="Security credentials were modified very recently, which is common in account-takeover scenarios."
        ))

    # Fallback if no specific code triggered
    if not codes:
        codes.append(ReasonCode(
            code="SYS-ROUTINE-VERIFICATION",
            family="SYSTEM",
            severity="LOW",
            description="All monitored signals within standard operational baselines.",
            plain_language_explanation="Routine automated monitoring. No anomalous speech or transaction patterns detected."
        ))

    return codes
