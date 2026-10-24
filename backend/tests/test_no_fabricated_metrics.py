"""
EchoGuard AI - No Fabricated Metrics Guardrail Test
Enforces that:
1. README.md metrics match reports/heldout_metrics.json exactly.
2. /api/eval/summary returns values backed by reports/heldout_metrics.json.
"""

import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_readme_matches_reported_metrics():
    heldout_file = PROJECT_ROOT / "reports" / "heldout_metrics.json"
    assert heldout_file.exists(), "reports/heldout_metrics.json must exist"

    with open(heldout_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    readme_file = PROJECT_ROOT / "README.md"
    assert readme_file.exists(), "README.md must exist"

    with open(readme_file, "r", encoding="utf-8") as f:
        readme_text = f.read()

    eer_str = f"**{metrics['eer_percent']}%**"
    assert eer_str in readme_text, (
        f"README.md does not contain the true reported EER {eer_str}. "
        "Run `python scripts/update_readme_metrics.py` to synchronize."
    )


def test_api_eval_summary_reflects_reports():
    heldout_file = PROJECT_ROOT / "reports" / "heldout_metrics.json"
    with open(heldout_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    client = TestClient(app)
    response = client.get("/api/eval/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["eer_percent"] == metrics["eer_percent"], (
        f"API reported eer_percent {data['eer_percent']} does not match heldout_metrics.json {metrics['eer_percent']}"
    )
    assert data["zero_disk_audio_verified"] is True
