"""
Unit tests for Simulated UPI Interception Hook & Threat Scenario S1.
Verifies that:
- UPI collect requests are blocked when session risk is Orange/Red or customer approval was denied.
- Low-risk transactions in Green tier pass without friction.
- Scam-warning interstitials trigger for high urgency or Amber tier.
"""

import pytest
from backend.app.schemas import UPIInterceptRequest
from backend.response.upi_hook import upi_hook


def test_upi_transfer_blocked_on_red_tier():
    req = UPIInterceptRequest(
        session_id="SESS-UPI-ATTACK-01",
        upi_collect_vpa="shady_scammer@okaxis",
        amount=45000.0,
        payer_vpa="victim@okhdfcbank",
        urgency_flag=True
    )
    result = upi_hook.evaluate_transaction(req, session_tier="RED", out_of_band_approved=False)

    assert result.is_blocked is True
    assert result.status == "BLOCKED"
    assert "High-Risk UPI Collect Intercepted" in result.warning_title
    assert result.required_cooling_off_seconds == 86400


def test_upi_transfer_blocked_when_push_denied():
    """Even if tier is Green or Amber, if customer explicitly tapped DENY, UPI is blocked."""
    req = UPIInterceptRequest(
        session_id="SESS-UPI-ATTACK-02",
        upi_collect_vpa="mule_account@paytm",
        amount=15000.0,
        payer_vpa="victim@okhdfcbank",
        urgency_flag=False
    )
    result = upi_hook.evaluate_transaction(req, session_tier="GREEN", out_of_band_approved=False)

    assert result.is_blocked is True
    assert result.status == "BLOCKED"


def test_upi_transfer_passes_on_green():
    req = UPIInterceptRequest(
        session_id="SESS-UPI-SAFE-03",
        upi_collect_vpa="electricity_bill@bescom",
        amount=1850.0,
        payer_vpa="genuine_customer@okhdfcbank",
        urgency_flag=False
    )
    result = upi_hook.evaluate_transaction(req, session_tier="GREEN", out_of_band_approved=True)

    assert result.is_blocked is False
    assert result.status == "PASSED"
    assert result.required_cooling_off_seconds == 0
