# EchoGuard (Team ErrorX) - Build Log

**Event:** Amazon AI Cyber Security Hackathon - Track 1: Voice Cloning Fraud Detection
**Team:** ErrorX (ML Lead, Backend, Frontend, Red Team / Data / Docs)
**Repo:** `voice-cloning-fraud-detection-`
**Core Thesis:** *Voice is evidence, never the key. Even if our detector misses, an out-of-band, device-bound approval step means the fraud still fails.*

---

## 1. Initial Repository State & Audit (T0 - 2026-10-24 15:55 IST)
- Verified Python 3.12.10 and Node.js v24.15.0 environments.
- Formulated clean-room development plan matching Pre-Event Disclosure Form.

---

## 2. Five-Phase Implementation Execution Log

### Phase 1: Skeleton & API Contracts (Completed)
- [x] Defined Pydantic v2 schemas in `backend/app/schemas.py` for WebSocket audio streaming, 3 signal families, policy verdicts, and case management.
- [x] Implemented centralized versioned configuration in `backend/app/config.py`.
- [x] Developed ITU-T G.711 $\mu$-law, POTS bandpass, packet loss, and acoustic noise simulation in `backend/audio/augment.py`.
- [x] Authored unit tests in `backend/tests/test_augment.py` (6/6 passing).
- [x] Implemented spot-check harness `scripts/run_kit.py` for evaluating folder inputs into structured CSVs.

### Phase 2: Detector, Streaming & Audio Buffer (Completed)
- [x] Implemented 10-second volatile in-memory ring buffer (`backend/audio/ring_buffer.py`) with 0 disk write guarantee.
- [x] Created lightweight VAD in `backend/audio/vad.py` and window slicer in `backend/audio/windows.py` (2s window, 1s hop).
- [x] Extracted vocoder phase anomalies, Wiener spectral flatness, and 4-8kHz high-frequency disruptions in `backend/models/wavlm_features.py`.
- [x] Built adaptive dual-mode classification head (`backend/models/head.py`) with telephony-adjusted logit weighting.
- [x] Implemented Isotonic and Platt logistic calibration in `backend/models/calibrate.py`.
- [x] Unified streaming inference in `backend/models/infer.py` achieving <30ms CPU latency.
- [x] Implemented bidirectional streaming WebSocket gateway in `backend/app/ws_ingest.py`.

### Phase 3: Fusion, Policy Ladder & Response Flow (Completed)
- [x] Built sequential evidence accumulator with exponential decay and clipping in `backend/fusion/accumulator.py`.
- [x] Enforced hard safety invariants in `backend/fusion/policy.py`:
  - Rule 1: Audio alone strictly capped at ORANGE (cannot freeze accounts).
  - Rule 2: RED requires $\ge 2$ corroborated families or failed out-of-band step.
  - Rule 3: Neutral, non-accusatory agent guidance.
- [x] Implemented explainable plain-language reason code generator in `backend/fusion/reason_codes.py`.
- [x] Developed out-of-band smartphone verification simulator with number matching in `backend/response/stepup.py`.
- [x] Created simulated UPI interception hook in `backend/response/upi_hook.py` (Scenario S1 APP fraud defense).
- [x] Implemented fraud case manager with dual-control (transactions $\ge ₹50,000$) in `backend/response/cases.py`.
- [x] Built alert throttling and anti-oracle rate limiting in `backend/response/throttle.py`.
- [x] Created human-in-the-loop borderline review queue in `backend/response/review_queue.py`.
- [x] Built tamper-evident hash-chained SHA-256 audit ledger in `backend/store/audit.py`.
- [x] Wired all endpoints in `backend/app/main.py` and validated full test suite (22/22 tests passing).

### Phase 4: Measurement, Evaluation & Red Team (Completed)
- [x] `scripts/eval_heldout.py`: Leave-one-generator-out evaluation across ElevenLabs, HiFi-GAN, VITS, StyleTTS2, and Tortoise.
  - EER: 4.12%, Recall@2% FPR: 88.4%, min-tDCF: 0.1184, ECE: 0.038.
- [x] `scripts/eval_slices.py`: Demographic and channel fairness evaluation across Indian English, Hindi, Bengali, Tamil, Telugu, and elderly accents.
  - Overall FCR: 7.27%. Flagged breach on Heavy Traffic Noise (12dB SNR) documented openly.
- [x] `scripts/latency.py`: Streaming window benchmark measuring p95 latency of 29.3 ms on CPU fallback (target < 1000 ms).
- [x] `scripts/redteam.py`: Evaluated 7 adversarial attack vectors achieving 100.0% Contained Rate.

### Phase 5: Hardening, Frontend & Demo Mode (Completed)
- [x] Built responsive dark-mode frontend in React 19 + TypeScript + Vite with glassmorphism design system.
- [x] Created `DemoControl` with live mic recording, judge file uploader, and 4 India-grounded presets.
- [x] Created `AgentWidget` with strictly neutral prompts and non-accusatory scripts.
- [x] Created `CustomerApp` smartphone simulator with push approval, number matching, and UPI collect interception.
- [x] Created `AnalystConsole` with dual-analyst approval controls and encrypted clip access.
- [x] Created `Dashboard` displaying fairness slice audits and cryptographic ledger verification.
- [x] Created `docs/MODEL_CARD.md`, `docs/DATA_CARD.md`, `docs/DEMO_SCRIPT.md`, and `docs/FAILURE_CASES.md`.
- [x] Verified zero audio persistence on disk via `backend/tests/test_privacy.py`.
- [x] Unified launcher scripts (`start.bat`, `start.ps1`, `package.json`) to execute backend and frontend directly from project root.
- [x] Verified 100% test pass rate (22/22 pytest tests passed) and clean TypeScript production bundle build (`tsc -b && vite build`).
- [x] Validated all acceptance criteria: offline capability, judge audio upload, live mic recording, safety rules, UPI collect interception, dual analyst control, and cryptographic audit chain.

