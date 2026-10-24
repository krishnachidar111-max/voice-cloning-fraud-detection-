"""
EchoGuard AI - Simulated UPI Interception Hook
Implements India-grounded Threat Scenario S1 (Customer-side UPI Collect Scam):
- Intercepts UPI collect requests and transfer attempts when risk is Orange/Red or call is in-flight
- Blocks payment, triggers scam-warning interstitial, and enforces 24h cooling-off period
- Prevents authorized push payment (APP) fraud when customer is pressured by a cloned relative or fake bank KYC call
"""

from typing import Dict, Any
from backend.app.schemas import UPIInterceptRequest, UPIInterceptResult
from backend.store.audit import audit_logger


class UPIInterceptionHook:
    """
    Simulated gateway hook into National Payments Corporation of India (NPCI) / UPI Switch.
    Monitors in-flight calls and active session risk before routing money.
    """

    def evaluate_transaction(
        self,
        request: UPIInterceptRequest,
        session_tier: str = "GREEN",
        out_of_band_approved: bool = True
    ) -> UPIInterceptResult:
        """
        Evaluates a UPI payment attempt against session risk and caller context.
        """
        # If the customer is on an active Orange/Red call or push was denied -> BLOCK
        if session_tier in ["ORANGE", "RED"] or not out_of_band_approved:
            audit_logger.append(
                actor_id="UPI_SWITCH_HOOK",
                action="UPI_TRANSACTION_BLOCKED",
                reason=f"Blocked UPI Collect of INR {request.amount:,.2f} from {request.upi_collect_vpa}. Session Tier: {session_tier}",
                session_id=request.session_id
            )
            return UPIInterceptResult(
                is_blocked=True,
                status="BLOCKED",
                tier=session_tier,
                warning_title="High-Risk UPI Collect Intercepted",
                warning_message=(
                    f"EchoGuard intercepted this UPI transfer of ₹{request.amount:,.2f} to '{request.upi_collect_vpa}'. "
                    "An active call on your device shows high probability of voice cloning or social engineering pressure. "
                    "Funds have been protected and a 24-hour payee cooling-off period has been activated."
                ),
                required_cooling_off_seconds=86400,
                out_of_band_token_required=True
            )

        # If Amber tier -> Require explicit confirmation with warning
        if session_tier == "AMBER" or request.urgency_flag:
            audit_logger.append(
                actor_id="UPI_SWITCH_HOOK",
                action="UPI_INTERSTITIAL_WARNING",
                reason=f"Displayed scam-warning interstitial for UPI transfer to {request.upi_collect_vpa}",
                session_id=request.session_id
            )
            return UPIInterceptResult(
                is_blocked=False,
                status="INTERCEPTED",
                tier="AMBER",
                warning_title="Urgent Payment Verification",
                warning_message=(
                    f"Warning: You are attempting to approve a ₹{request.amount:,.2f} UPI request while on a voice call. "
                    "Bank officials will NEVER ask you to approve a collect request or enter your UPI PIN to receive money."
                ),
                required_cooling_off_seconds=300,
                out_of_band_token_required=True
            )

        # Green tier -> Normal pass
        return UPIInterceptResult(
            is_blocked=False,
            status="PASSED",
            tier="GREEN",
            warning_title="Payment Approved",
            warning_message="UPI transfer verified and dispatched.",
            required_cooling_off_seconds=0,
            out_of_band_token_required=False
        )


upi_hook = UPIInterceptionHook()
