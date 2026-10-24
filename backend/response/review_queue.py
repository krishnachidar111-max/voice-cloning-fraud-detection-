"""
EchoGuard AI - Human-in-the-Loop Borderline Review Queue
Triages borderline confidence scores (0.35 - 0.65) to specialized fraud analysts.
Provides full multi-family feature breakdowns for manual audit.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.schemas import StreamingVerdict


class ReviewQueueManager:
    """Manages queue of borderline scores requiring secondary human scrutiny."""

    def __init__(self, lower_bound: float = 0.35, upper_bound: float = 0.65):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.queue: List[Dict[str, Any]] = []

    def check_and_enqueue(self, verdict: StreamingVerdict, synthetic_prob: float) -> Optional[Dict[str, Any]]:
        """If confidence is ambiguous/borderline, adds session to human review queue."""
        if self.lower_bound <= synthetic_prob <= self.upper_bound or verdict.tier == "ORANGE":
            item = {
                "queue_id": f"REV-{len(self.queue) + 1:04d}",
                "session_id": verdict.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "synthetic_prob": synthetic_prob,
                "risk_score": verdict.risk_score,
                "tier": verdict.tier,
                "llr_breakdown": {
                    "audio": verdict.llr_audio,
                    "interaction": verdict.llr_interaction,
                    "transaction": verdict.llr_transaction
                },
                "reason_codes": [r.code for r in verdict.reason_codes],
                "status": "AWAITING_REVIEW",
                "assigned_to": None
            }
            self.queue.append(item)
            return item
        return None

    def list_queue(self) -> List[Dict[str, Any]]:
        return list(reversed(self.queue[-50:]))


review_queue = ReviewQueueManager()
