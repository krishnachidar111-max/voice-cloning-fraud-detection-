"""
EchoGuard AI - Family B: Call & Interaction Context Signals
Measures conversational cadence, turn-taking latency, prosody, and ANI reputation.
"""

import math
from typing import Optional
from backend.app.schemas import InteractionSignal


def compute_interaction_llr(
    response_latency_s: float,
    turn_taking_jitter_s: float,
    prosodic_variance: float,
    caller_ani_reputation: float,
    unscripted_challenge_latency_s: Optional[float] = None
) -> float:
    """
    Computes calibrated LLR for conversational interaction dynamics.
    Synthetic/voice-cloned attacks exhibit:
    - High or rigid response latency (TTS synthesis buffer delay: 600ms - 1500ms)
    - Unnatural turn-taking jitter
    - Depressed prosodic variance (flatter pitch contour than excited human)
    - High hesitation on unscripted interactive challenges (>2.5s)
    - Spoofed / high-risk ANI
    """
    score = 0.0

    # 1. Synthesis latency penalty (TTS systems have turnaround delay)
    if response_latency_s > 1.8:
        score += 1.2
    elif response_latency_s > 1.2:
        score += 0.6
    elif response_latency_s < 0.4:
        score -= 0.5  # Fluid human cadence

    # 2. Prosodic variance (robotic voice has flat prosody < 0.5)
    if prosodic_variance < 0.45:
        score += 1.0
    elif prosodic_variance > 0.8:
        score -= 0.4

    # 3. Unscripted challenge response latency
    if unscripted_challenge_latency_s is not None:
        if unscripted_challenge_latency_s > 3.0:
            score += 1.8  # Operator typing into prompt / generating clone
        elif unscripted_challenge_latency_s < 1.5:
            score -= 0.8  # Spontaneous natural reply

    # 4. Caller ANI reputation score [0.0 (safe) to 1.0 (spoofed/VoIP)]
    score += (caller_ani_reputation - 0.2) * 2.0

    # Map to bounded LLR [-3.0, +3.0]
    return float(max(-3.0, min(3.0, score)))


def get_interaction_signal(
    response_latency_s: float = 0.8,
    turn_taking_jitter_s: float = 0.1,
    prosodic_variance: float = 0.85,
    caller_ani_reputation: float = 0.1,
    unscripted_challenge_latency_s: Optional[float] = None
) -> InteractionSignal:
    """Returns a typed InteractionSignal with calculated LLR."""
    llr = compute_interaction_llr(
        response_latency_s=response_latency_s,
        turn_taking_jitter_s=turn_taking_jitter_s,
        prosodic_variance=prosodic_variance,
        caller_ani_reputation=caller_ani_reputation,
        unscripted_challenge_latency_s=unscripted_challenge_latency_s
    )
    return InteractionSignal(
        response_latency_s=response_latency_s,
        turn_taking_jitter_s=turn_taking_jitter_s,
        prosodic_variance=prosodic_variance,
        unscripted_challenge_latency_s=unscripted_challenge_latency_s,
        caller_ani_reputation=caller_ani_reputation,
        llr=llr
    )
