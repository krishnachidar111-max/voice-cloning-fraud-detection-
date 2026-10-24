"""
EchoGuard AI - Alert Throttling & Rate-Limiting Engine
Prevents alert fatigue by deduplicating alerts per session and rate-limiting per ANI / account.
Anti-oracle defense: limits rapid consecutive probing by an adaptive attacker (FR-25).
"""

import time
from typing import Dict, Tuple


class AlertThrottler:
    """
    Tracks alert timestamps per session and caller ANI.
    Enforces cooldown intervals and rate limits to defeat automated probing.
    """

    def __init__(self, session_cooldown_s: float = 3.0, max_probes_per_ani_10m: int = 5):
        self.session_cooldown_s = session_cooldown_s
        self.max_probes_per_ani = max_probes_per_ani_10m
        self.last_alert_time: Dict[str, float] = {}
        self.ani_probe_counts: Dict[str, list[float]] = {}

    def should_emit_alert(self, session_id: str, tier: str) -> bool:
        """Determines if a push or analyst alert should be emitted or throttled."""
        if tier in ["GREEN"]:
            return False

        now = time.time()
        last_time = self.last_alert_time.get(session_id, 0.0)

        # Suppress alerts if emitted too recently in the same session
        if now - last_time < self.session_cooldown_s and tier != "RED":
            return False

        self.last_alert_time[session_id] = now
        return True

    def check_ani_rate_limit(self, ani_phone: str) -> Tuple[bool, str]:
        """
        Anti-oracle defense: checks if an ANI has triggered too many verification calls in 10 minutes.
        """
        now = time.time()
        window_start = now - 600.0  # 10 minutes

        calls = self.ani_probe_counts.get(ani_phone, [])
        recent_calls = [t for t in calls if t >= window_start]
        recent_calls.append(now)
        self.ani_probe_counts[ani_phone] = recent_calls

        if len(recent_calls) > self.max_probes_per_ani:
            return False, f"Anti-oracle rate limit exceeded for caller ID {ani_phone}. Probing detected."

        return True, "Rate limit within normal threshold."


alert_throttler = AlertThrottler()
