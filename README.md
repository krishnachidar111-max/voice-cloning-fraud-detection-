# EchoGuard AI
## Real-Time Voice Cloning Fraud Detection & Banking Security System
**Team ErrorX | Amazon AI Cyber Security Hackathon (Track 1: Voice Cloning Fraud Detection)**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![Tests: 22 Passed](https://img.shields.io/badge/Tests-22%20Passed-brightgreen.svg)]()
[![Contained Rate: 100%](https://img.shields.io/badge/Contained%20Rate-100%25-success.svg)]()
[![Privacy: 0 Bytes Disk](https://img.shields.io/badge/Audio%20Persisted-0%20Bytes-success.svg)]()

---

> **Core Thesis:** *"Voice is evidence, never the key."* Even if our synthetic voice detector misses, an out-of-band, device-bound approval step means the financial fraud still fails.

---

## 🌟 Key Capabilities & Safety Invariants

1. **Sub-Second Streaming Inference (Family A):**
   - 2-second overlapping windows (1.0s hop) with **p95 latency of 29.3 ms on CPU**.
   - Extracts vocoder phase anomalies, Wiener spectral flatness, and $4-8\,\text{kHz}$ high-frequency disruptions characteristic of neural synthesizers (HiFi-GAN, VITS, ElevenLabs).
   - Dual-mode adaptive weighting for POTS/G.711 telephony channels ($300\,\text{Hz} - 3400\,\text{Hz}$).

2. **Three-Family Risk Accumulation:**
   - **Family A (Audio Evidence):** Calibrated LLR of acoustic synthesis cues and channel anomalies.
   - **Family B (Interaction & Cadence):** Response latency (TTS buffer turnaround delay), turn-taking jitter, prosodic variance, and ANI spoofing risk.
   - **Family C (Transaction Context):** Action sensitivity (balance inquiry vs payee add vs limit raise vs UPI collect), amount vs history, novel payee, and SIM-swap signals.
   - Accumulator with exponential decay: $S_t = \text{clip}(\lambda S_{t-1} + \sum_f w_f \cdot \text{LLR}_f, -L, +U)$.

3. **Four-Tier Response Policy with Hard Safety Invariants (Enforced in Code):**
   - **GREEN:** Normal workflow pass. Low-risk operations (e.g. balance check) are never blocked.
   - **AMBER:** Passive step-up: in-app push notification to customer app.
   - **ORANGE:** Unscripted interactive challenge + mandatory out-of-band mobile verification.
   - **RED:** Immediate security freeze and analyst triage.
   - **Safety Invariant 1:** Audio score alone is **STRICTLY CAPPED AT ORANGE** (can never freeze an account).
   - **Safety Invariant 2:** RED requires corroborating evidence from $\ge 2$ independent signal families, OR an explicitly denied/timed-out out-of-band step.
   - **Safety Invariant 3:** Frontline agents see only neutral, non-accusatory operational guidance. Never scores or fraud accusations.

4. **Zero-Disk Privacy by Design (DPDP Act 2023 Conformance):**
   - Audio processed strictly in a **10-second volatile in-memory ring buffer**.
   - **0 bytes of raw voice saved to persistent disk**. Buffers are wiped within 100ms of call termination.
   - No voiceprints, no biometric speaker identification, no emotion profiling.

5. **India-Grounded Threat Scenarios:**
   - **Scenario S1 (Customer-Side UPI Collect Scam):** Cloned relative calls victim urging collect approval $\to$ Intercepted at simulated UPI Switch hook with scam-warning interstitial and 24h cooling-off.
   - **Scenario S2 (Contact Center Account Takeover):** Cloned voice requests payee add + limit raise $\to$ Victim taps DENY on mobile banking app $\to$ Session freezes into RED with dual-analyst signoff.

---

## ⚖️ Real vs MOCK Architecture (Disclosure Table)

Per Hard Rule 4 and PRD Section 7, all simulated interfaces are explicitly labelled:

| Component | Status | Operational Details |
|---|---|---|
| **Streaming Acoustic Deepfake Detector** | **REAL** | Custom hybrid feature extractor + adaptive dual-mode head with Isotonic calibration. |
| **Telephony Channel Augmentation** | **REAL** | G.711 $\mu$-law companding, Butterworth bandpass (300-3400Hz), packet loss, and acoustic noise. |
| **10-Second Volatile RAM Buffer** | **REAL** | In-memory circular buffer with zero disk writes, verified by automated privacy tests. |
| **Multi-Family Bayesian Accumulator** | **REAL** | Exponential decay ($\lambda = 0.82$), saturation bounds $[-4.0, +6.0]$, calibrated LLRs. |
| **Policy Engine & Safety Invariants** | **REAL** | Threshold ladders, audio cap at Orange, 2-family Red requirement enforced in code. |
| **Tamper-Evident Audit Ledger** | **REAL** | Hash-chained SHA-256 append-only ledger with cryptographic verification endpoint. |
| **Out-of-Band Smartphone Simulator** | **REAL** | Web-based smartphone simulator with cryptographic single-use tokens & number matching. |
| **Analyst Console & Dual-Control** | **REAL** | Interactive case queue, dual-analyst signoff for amounts $\ge ₹50,000$, and appeal workflow. |
| **Telephony Media Fork (SIPREC / SBC)** | **MOCK** | Browser Web Audio API microphone stream or audio file uploader. |
| **Core Banking System (Finacle / BaNCS)** | **MOCK** | Simulated transaction feed with action sensitivity weights and baseline limits. |
| **NPCI UPI Switch Gateway** | **MOCK** | Simulated UPI hook intercepting collect requests during active high-risk calls. |
| **Telecom Carrier SIM-Swap Feed** | **MOCK** | Simulated carrier intelligence flag indicating SIM replacement within 24 hours. |

---

## 📊 Empirical Evaluation Benchmarks (Measured in `reports/`)

All figures below are generated by executable scripts in `scripts/` and recorded in `reports/`:

| Evaluation Metric | Target | Measured Value | Script & Source of Truth | Result |
|---|---|---|---|---|
| **Equal Error Rate (EER)** | $\le 5.0\%$ | **15.2%** | `scripts/eval_heldout.py` | **OPEN** |
| **Recall @ $\le 2\%$ FPR** | $\ge 85.0\%$ | **0.0%** | `scripts/eval_heldout.py` (Held-out generators) | **OPEN** |
| **Expected Calibration Error (ECE)** | $\le 0.05$ | **0.2413** | `scripts/eval_heldout.py` | **OPEN** |
| **min-tDCF** | $\le 0.15$ | **0.118** | `scripts/eval_heldout.py` | **PASS** |
| **Adversarial Contained Rate** | $\ge 95.0\%$ | **100.0%** | `scripts/redteam.py` (7 attack vectors) | **PASS** |
| **p95 Window Verdict Latency** | $< 1,000\,\text{ms}$ | **29.26 ms** | `scripts/latency.py` (150 iterations on CPU) | **PASS** |
| **Spot-Check Kit Accuracy** | High | **100.0%** | `scripts/run_kit.py` (`reports/spot_check_results.csv`) | **PASS** |
| **Overall False Challenge Rate** | $\le 3.0\%$ | **7.27%** | `scripts/eval_slices.py` (*Flagged breach on 12dB noise*) | **OPEN** |

> **Honesty Disclosure (Per-Slice Breach):** In `scripts/eval_slices.py`, genuine speech under **Heavy Traffic Noise (12dB SNR)** exhibited a 100% false challenge rate. While all languages (Hindi, English, Bengali, Tamil, Telugu) passed cleanly at 0.0% FCR, extreme noise triggers spectral flatness elevation. This failure case is called out openly and analyzed in [`docs/FAILURE_CASES.md`](docs/FAILURE_CASES.md).

---

## 🚀 Quickstart & One-Command Startup

### Prerequisites
- **Python 3.11+** (FastAPI, NumPy, SciPy, scikit-learn, pytest)
- **Node.js v20+** and **npm**

### Step 1: Run One-Command Launcher

**On Windows (PowerShell):**
```powershell
.\start.ps1
```

**Or on Command Prompt:**
```cmd
start.bat
```

**Or via Root NPM:**
```bash
npm run dev
```

### Step 2: Access Endpoints
- **Frontend Dashboard & Controller:** `http://127.0.0.1:5173`
- **Backend API & Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Real-Time WebSocket Gateway:** `ws://127.0.0.1:8000/ws/audio/{session_id}`

---

## 🧪 Running Automated Test Suite & Evaluation

Run all 22 passing unit and integration tests:
```bash
python -m pytest backend/tests -v
```

Execute evaluation and red-team benchmark scripts:
```bash
# 1. Spot-check kit evaluation on any folder of WAV files
python scripts/run_kit.py --input_dir data/spot_check_kit --output_csv reports/spot_check_results.csv

# 2. Leave-one-generator-out held-out evaluation (EER, min-tDCF, Recall@2% FPR)
python scripts/eval_heldout.py

# 3. Demographic & channel per-slice fairness audit
python scripts/eval_slices.py

# 4. Sub-second CPU latency benchmark (p50, p95, p99)
python scripts/latency.py

# 5. Adversarial red-team attack simulation (Contained rate)
python scripts/redteam.py
```

---

## 📁 Repository Directory Structure

```
backend/
  app/
    main.py          # FastAPI application & REST endpoints
    ws_ingest.py     # Real-time WebSocket audio streaming gateway
    config.py        # Centralized settings & threshold ladders
    schemas.py       # Pydantic v2 data contracts
  audio/
    ring_buffer.py   # 10-second in-memory volatile ring buffer (0-byte disk guarantee)
    vad.py           # Energy-based voice activity detection
    windows.py       # Audio decoding & 2s windowing (1s hop)
    augment.py       # Telephony simulation (G.711 mu-law, bandpass, packet loss, noise)
  models/
    wavlm_features.py# Spectral vocoder anomaly & acoustic feature extraction
    head.py          # Adaptive dual-mode classification head
    calibrate.py     # Isotonic & Platt temperature calibration
    infer.py         # Sub-30ms unified audio inference engine
  signals/
    interaction.py   # Family B: response latency, turn-taking, prosody, ANI risk
    transaction.py   # Family C: action sensitivity, payee novelty, amount, SIM-swap
    channel_cues.py  # Replay & acoustic double-convolution detection
  fusion/
    accumulator.py   # Sequential Bayesian evidence accumulator with decay
    policy.py        # Four-tier policy engine & core safety invariants
    reason_codes.py  # Plain-language explainable reason codes generator
  response/
    stepup.py        # Out-of-band mobile verification orchestrator
    upi_hook.py      # Simulated UPI interception hook (NPCI gateway simulation)
    cases.py         # Fraud case manager with dual-analyst control (>= ₹50,000)
    throttle.py      # Alert throttling & anti-oracle rate limiter
    review_queue.py  # Human-in-the-loop borderline score review queue
  store/
    db.py            # SQLite metadata & score-only repository (zero audio)
    audit.py         # Cryptographic SHA-256 hash-chained append-only audit ledger
  tests/             # 22 passing unit & integration tests

frontend/
  src/
    pages/
      DemoControl.tsx# Live mic recording, judge file upload, 4 India presets
      AgentWidget.tsx# Neutral frontline call center agent interface
      CustomerApp.tsx# Mobile banking smartphone simulator (Approve/Deny, UPI collect)
      AnalystConsole.tsx # Tier-2 fraud specialist case triage & dual approval
      Dashboard.tsx  # Fairness per-slice charts & tamper-evident audit ledger
    services/api.ts  # Typed API client
    App.tsx          # Main navigation & state synchronization
    index.css        # Glassmorphism dark-mode cybersecurity design system

scripts/
  run_kit.py         # Spot-check evaluation on folder of WAV files
  eval_heldout.py    # Held-out generator benchmark (EER, min-tDCF, ECE)
  eval_slices.py     # Demographic & channel per-slice fairness audit
  latency.py         # p95 streaming window latency benchmark
  redteam.py         # Adversarial red-team attack suite

reports/             # Generated CSV and JSON benchmark results
docs/
  ASSETS.md          # Inventory of dependencies, models, and datasets
  DECISIONS.md       # Architecture & technical decisions log
  BUILD_LOG.md       # Step-by-step milestone log
  MODEL_CARD.md      # Model architecture, training, and ethical scope
  DATA_CARD.md       # Dataset heritage, transforms, and DPDP Act compliance
  DEMO_SCRIPT.md     # 3-minute stage 2 presentation script for jury
  FAILURE_CASES.md   # Named failure cases and adversarial limitations
```
