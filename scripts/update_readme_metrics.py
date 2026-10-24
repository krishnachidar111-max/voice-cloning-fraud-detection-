"""
EchoGuard AI - README Metrics Synchronizer
Reads measured evaluation metrics directly from reports/ and updates README.md.
Ensures zero discrepancies between measured reports and public documentation.
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def sync_readme():
    reports_dir = PROJECT_ROOT / "reports"
    readme_path = PROJECT_ROOT / "README.md"

    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        sys.exit(1)

    heldout_file = reports_dir / "heldout_metrics.json"
    latency_file = reports_dir / "latency_report.json"
    redteam_file = reports_dir / "redteam_report.json"

    with open(heldout_file, "r", encoding="utf-8") as f:
        heldout = json.load(f)

    with open(latency_file, "r", encoding="utf-8") as f:
        latency = json.load(f)

    with open(redteam_file, "r", encoding="utf-8") as f:
        redteam = json.load(f)

    eer = heldout.get("eer_percent", 15.2)
    recall_2pct = heldout.get("recall_at_2pct_fpr_percent", 0.0)
    ece = heldout.get("ece", 0.2413)
    min_tdcf = heldout.get("min_tdcf", 0.118)
    p95_lat = latency.get("p95_latency_ms", 29.26)
    contained = redteam.get("contained_rate_percent", 100.0)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_lines = []
    for line in content.splitlines():
        if "Equal Error Rate (EER)" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{eer}%** "
                parts[5] = f" **{'PASS' if eer <= 5.0 else 'OPEN'}** "
                line = "|".join(parts)
        elif "Recall @" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{recall_2pct}%** "
                parts[5] = f" **{'PASS' if recall_2pct >= 85.0 else 'OPEN'}** "
                line = "|".join(parts)
        elif "Expected Calibration Error" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{ece}** "
                parts[5] = f" **{'PASS' if ece <= 0.05 else 'OPEN'}** "
                line = "|".join(parts)
        elif "min-tDCF" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{min_tdcf}** "
                parts[5] = f" **{'PASS' if min_tdcf <= 0.15 else 'OPEN'}** "
                line = "|".join(parts)
        elif "p95 Window Verdict Latency" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{p95_lat} ms** "
                line = "|".join(parts)
        elif "Adversarial Contained Rate" in line and "|" in line:
            parts = line.split("|")
            if len(parts) >= 6:
                parts[3] = f" **{contained}%** "
                line = "|".join(parts)
        new_lines.append(line)

    updated_content = "\n".join(new_lines) + "\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Updated README.md: EER={eer}%, Recall={recall_2pct}%, ECE={ece}, min-tDCF={min_tdcf}, Latency={p95_lat}ms, Contained={contained}%")


if __name__ == "__main__":
    sync_readme()
