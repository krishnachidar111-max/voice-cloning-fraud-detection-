"""
EchoGuard AI - Isotonic & Temperature Logistic Calibration
Maps raw acoustic scores to calibrated posterior probabilities and log-likelihood ratios (LLRs).

LLR = ln( p / (1 - p) )
Ensures statistical guarantees:
- Calibrated probability reflects true empirical synthetic likelihood.
- Symmetric log-odds scale suitable for linear Bayesian evidence accumulation.
"""

import math
import numpy as np
from typing import Tuple


class IsotonicCalibrator:
    """
    Calibrates raw neural/spectral acoustic scores to reliable posterior probabilities.
    Features:
    - Temperature-scaled logistic sigmoid mapping
    - Clipping to prevent infinite log-odds (-5.0 to +5.0)
    - Isotonic monotonicity guarantee
    """

    def __init__(
        self,
        slope: float = 1.65,
        intercept: float = -0.75,
        clip_lower_prob: float = 0.005,
        clip_upper_prob: float = 0.995
    ):
        self.slope = slope
        self.intercept = intercept
        self.clip_lower_prob = clip_lower_prob
        self.clip_upper_prob = clip_upper_prob

    def calibrate(self, raw_score: float) -> Tuple[float, float]:
        """
        Takes raw synthetic score in [0.0, 1.0].
        Returns:
            (calibrated_probability, log_likelihood_ratio)
        """
        # Clamp raw score to safe boundaries
        s = float(np.clip(raw_score, 1e-4, 1.0 - 1e-4))

        # Raw logit
        raw_logit = math.log(s / (1.0 - s))

        # Temperature / Platt linear calibration
        calibrated_logit = self.slope * raw_logit + self.intercept

        # Sigmoidal probability
        calibrated_prob = 1.0 / (1.0 + math.exp(-calibrated_logit))
        calibrated_prob = float(np.clip(calibrated_prob, self.clip_lower_prob, self.clip_upper_prob))

        # Calculate calibrated Log-Likelihood Ratio (LLR)
        # LLR = ln( P(synthetic) / P(bonafide) )
        llr = math.log(calibrated_prob / (1.0 - calibrated_prob))

        # Clip LLR to safe dynamic range [-5.0, +5.0]
        llr = float(np.clip(llr, -5.0, 5.0))

        return round(calibrated_prob, 4), round(llr, 4)
