"""
EchoGuard AI - Dynamic Evidence Accumulator
Implements FR-10:
    S_t = clip( decay * S_{t-1} + sum(w_f * LLR_f), -L, +U )
    R_t = S_t + prior(ANI, device) + k[action] * txn_risk

Prevents single noisy window from causing false alarms.
"""

from typing import List, Dict, Tuple
from backend.app.config import settings


class EvidenceAccumulator:
    """
    Sequential Bayesian evidence accumulator with exponential decay and dynamic saturation bounds.
    """

    def __init__(
        self,
        decay: float = settings.ACCUMULATOR_DECAY,
        clip_lower: float = settings.ACCUMULATOR_CLIP_LOWER,
        clip_upper: float = settings.ACCUMULATOR_CLIP_UPPER,
        w_audio: float = settings.WEIGHT_AUDIO,
        w_interaction: float = settings.WEIGHT_INTERACTION,
        w_transaction: float = settings.WEIGHT_TRANSACTION
    ):
        self.decay = decay
        self.clip_lower = clip_lower
        self.clip_upper = clip_upper
        self.w_audio = w_audio
        self.w_interaction = w_interaction
        self.w_transaction = w_transaction

        self.current_evidence: float = 0.0
        self.window_history: List[Dict[str, float]] = []

    def add_window(
        self,
        llr_audio: float,
        llr_interaction: float,
        llr_transaction: float,
        ani_device_prior: float = 0.0
    ) -> Tuple[float, float]:
        """
        Ingests evidence from the latest 2-second time window.
        Returns:
            (accumulated_evidence S_t, total_risk_score R_t)
        """
        # Weighted instantaneous log-likelihood ratio
        instant_llr = (
            self.w_audio * llr_audio +
            self.w_interaction * llr_interaction +
            self.w_transaction * llr_transaction
        )

        # Update evidence with exponential decay and saturation clipping
        self.current_evidence = self.decay * self.current_evidence + instant_llr
        self.current_evidence = max(self.clip_lower, min(self.clip_upper, self.current_evidence))

        # Total fused risk score R_t
        risk_score = self.current_evidence + ani_device_prior

        # Record window history
        self.window_history.append({
            "window_index": len(self.window_history),
            "llr_audio": llr_audio,
            "llr_interaction": llr_interaction,
            "llr_transaction": llr_transaction,
            "instant_llr": instant_llr,
            "accumulated_evidence": self.current_evidence,
            "risk_score": risk_score
        })

        return round(self.current_evidence, 3), round(risk_score, 3)

    def reset(self) -> None:
        """Resets accumulator at session termination."""
        self.current_evidence = 0.0
        self.window_history.clear()
