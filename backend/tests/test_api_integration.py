"""
Integration tests for EchoGuard FastAPI REST & WebSocket endpoints.
Verifies health status, one-shot audio upload, verification push challenges,
analyst case management with dual-control, and tamper-evident audit logs.
"""

import io
import wave
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["audio_persisted_bytes"] == 0
    assert "safety_invariants" in data


def test_one_shot_audio_analysis_file_upload(client):
    # Create valid in-memory WAV file
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    int_data = (audio * 32767).astype(np.int16)

    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int_data.tobytes())
    wav_io.seek(0)

    response = client.post(
        "/api/audio/analyze",
        files={"file": ("test.wav", wav_io, "audio/wav")},
        data={"session_id": "SESS-INTEG-01", "action_type": "balance_inquiry"}
    )
    assert response.status_code == 200
    verdict = response.json()
    assert "tier" in verdict
    assert "risk_score" in verdict
    assert verdict["audio_persisted_bytes"] == 0


def test_out_of_band_verification_lifecycle(client):
    # 1. Request verification push
    req = {
        "session_id": "SESS-PUSH-TEST",
        "action_type": "add_payee",
        "amount": 45000.0,
        "payee_name": "Rohan Sharma"
    }
    resp1 = client.post("/api/verification/request", json=req)
    assert resp1.status_code == 200
    challenge = resp1.json()
    assert challenge["status"] == "PENDING"
    challenge_id = challenge["challenge_id"]
    code = challenge["number_matching_code"]

    # 2. Customer responds with matching code
    resp2 = client.post("/api/verification/respond", json={
        "challenge_id": challenge_id,
        "decision": "APPROVE",
        "entered_matching_code": code
    })
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "APPROVED"


def test_analyst_dual_control_enforcement(client):
    # Case with amount >= ₹50,000 requires 2 analysts to release
    cases_resp = client.get("/api/cases")
    assert cases_resp.status_code == 200
    cases = cases_resp.json()
    assert len(cases) > 0
    case_id = cases[0]["case_id"]

    # Analyst 1 approves release
    action1 = {
        "analyst_id": "ANALYST_01",
        "action": "RELEASE",
        "notes": "Verified voice and callback with customer."
    }
    res1 = client.post(f"/api/cases/{case_id}/action", json=action1)
    assert res1.status_code == 200
    assert res1.json()["status"] == "PENDING_SECOND_APPROVAL"

    # Same Analyst 1 cannot approve second time
    res_repeat = client.post(f"/api/cases/{case_id}/action", json=action1)
    assert res_repeat.status_code == 400

    # Analyst 2 (supervisor) provides final signoff
    action2 = {
        "analyst_id": "SUPERVISOR_02",
        "action": "RELEASE",
        "notes": "Secondary signoff approved."
    }
    res2 = client.post(f"/api/cases/{case_id}/action", json=action2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "RELEASED"


def test_audit_chain_integrity(client):
    resp = client.get("/api/audit/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["status"] == "CHAIN_VERIFIED_TAMPER_EVIDENT"
