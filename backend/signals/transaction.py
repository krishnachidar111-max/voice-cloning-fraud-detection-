"""
EchoGuard AI - Family C: Transaction & Account Risk Signals
MOCK feed representing core banking & fraud engine context:
- Action sensitivity (balance vs payee add vs UPI transfer)
- Amount vs historical baseline
- Payee novelty & 24h credential changes
- Mule account intelligence
"""

import math
from typing import Literal
from backend.app.schemas import TransactionSignal


ACTION_SENSITIVITY_WEIGHTS = {
    "balance_inquiry": 0.05,
    "mini_statement": 0.05,
    "bill_payment": 0.35,
    "add_payee": 1.20,
    "raise_limit": 1.30,
    "credentials_reset": 1.75,
    "sim_swap_signal": 1.90,
    "upi_collect_request": 1.50,
    "upi_transfer": 1.40,
    "wire_transfer": 1.60
}


def compute_transaction_llr(
    action_type: str,
    amount: float,
    is_novel_payee: bool,
    velocity_1h_count: int,
    recent_credential_change_24h: bool,
    mule_account_risk_score: float
) -> float:
    """
    Computes calibrated LLR for financial risk.
    """
    sensitivity = ACTION_SENSITIVITY_WEIGHTS.get(action_type, 0.5)

    score = 0.0

    # Low-risk passive actions strictly produce negative LLR (favoring bonafide pass)
    if action_type in ["balance_inquiry", "mini_statement"]:
        return -2.5

    # Action base sensitivity
    score += (sensitivity - 0.5) * 1.5

    # Amount scaling (logarithmic scale)
    if amount > 100000:       # > ₹1,00,000 / $1,200
        score += 1.8
    elif amount > 25000:      # > ₹25,000
        score += 1.0
    elif amount > 5000:
        score += 0.4

    # Novel payee risk
    if is_novel_payee:
        score += 1.2

    # High velocity within 1 hour
    if velocity_1h_count > 3:
        score += 1.5
    elif velocity_1h_count > 1:
        score += 0.5

    # Prior 24h credential change (strong indicator of SIM-swap / account takeover)
    if recent_credential_change_24h:
        score += 2.2

    # Mule account intelligence
    if mule_account_risk_score > 0.6:
        score += 2.0 * mule_account_risk_score

    # Bounded LLR [-4.0, +5.0]
    return float(max(-4.0, min(5.0, score)))


def get_transaction_signal(
    action_type: str = "balance_inquiry",
    amount: float = 0.0,
    is_novel_payee: bool = False,
    velocity_1h_count: int = 0,
    recent_credential_change_24h: bool = False,
    mule_account_risk_score: float = 0.0
) -> TransactionSignal:
    """Returns a typed TransactionSignal with computed LLR."""
    llr = compute_transaction_llr(
        action_type=action_type,
        amount=amount,
        is_novel_payee=is_novel_payee,
        velocity_1h_count=velocity_1h_count,
        recent_credential_change_24h=recent_credential_change_24h,
        mule_account_risk_score=mule_account_risk_score
    )
    return TransactionSignal(
        action_type=action_type,  # type: ignore
        amount=amount,
        is_novel_payee=is_novel_payee,
        velocity_1h_count=velocity_1h_count,
        recent_credential_change_24h=recent_credential_change_24h,
        mule_account_risk_score=mule_account_risk_score,
        llr=llr
    )
