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
- [x] Pydantic v2 schemas in `backend/app/schemas.py`.
- [x] Centralized configuration in `backend/app/config.py`.
- [x] G.711 telephony augmentation in `backend/audio/augment.py`.
- [x] Unit tests in `backend/tests/test_augment.py`.
- [x] Spot-check harness `scripts/run_kit.py`.

### Phase 2: Detector, Streaming & Audio Buffer (Completed)
- [x] 10-second volatile in-memory ring buffer with 0 disk write guarantee.
- [x] VAD, window slicer, spectral feature extractor.
- [x] Adaptive dual-mode classification head (spectral, hand-tuned).
- [x] Isotonic and Platt calibration.
- [x] Sub-30ms CPU latency on toy spectral features.
- [x] WebSocket gateway.

### Phase 3: Fusion, Policy Ladder & Response Flow (Completed)
- [x] Evidence accumulator with exponential decay.
- [x] Policy engine with 3 hard safety invariants.
- [x] Step-up, UPI hook, dual-control case manager, audit ledger.
- [x] 22/22 tests passing.

### Phase 4: Measurement, Evaluation & Red Team (Completed - NOTE: Synthetic Tones Only)
- [x] `eval_heldout.py` — **EER 46.0%, Recall@2%FPR 22.4%** (honest numbers in `reports/heldout_metrics.json`).
  - **PROBLEM FOUND**: bona fide = sine-wave harmonics, synthetic = sine tones + 5-7 kHz artifact.
- [x] `latency.py` — 29.3 ms is for the toy spectral engine.

### Phase 5: Hardening, Frontend & Demo Mode (Completed)
- [x] React 19 + TypeScript + Vite glassmorphism dark-mode frontend.
- **PROBLEM FOUND**: Google Fonts CDN in `index.html` + `index.css` — violates offline constraint.
- **PROBLEM FOUND**: README says EER 4.12% but `reports/heldout_metrics.json` says 46.0% — contradiction.

---

## 3. Combine + Upgrade: Problem Audit & Remediation Plan (T1 - 2026-10-24 23:00 IST)

### All Problems Found

| # | Problem | Fix |
|---|---------|-----|
| 1 | `head.py` is hand-tuned spectral formula, never trained on real speech | `LearnedAudioEngine` with sklearn logistic head + fallback banner |
| 2 | `eval_heldout.py` uses sine-tone bona fide and pure-tone deepfakes | Rewrite to read real audio manifests; tones => `tests/smoke_synthetic_tones.py` |
| 3 | README says EER 4.12%, JSON says 46.0% | `scripts/update_readme_metrics.py` writes README from `reports/` |
| 4 | p95 latency 29ms was for toy spectral features | Measure real latency after model swap; report honestly |
| 5 | Google Fonts CDN in `index.html` / `index.css` | Remove CDN; use system font stack |
| 6 | `/api/eval/summary` hardcodes numbers | Read `reports/*.json` at request time |
| 7 | `data/spot_check_kit/` synthetic tones appear in reports | Move to `tests/fixtures/`, rename clearly |

---

## 4. Phase 1 Execution (T1 - 2026-10-24 23:05 IST) — Learned Detector

- [x] Created `backend/models/learned_detector.py` — `LearnedAudioEngine` with 25-feature spectral extraction, sklearn LogisticRegression head (joblib), fallback to spectral head when model file missing.
- [x] Added `DETECTOR_BACKEND` config key (default `learned`).
- [x] Updated `backend/models/infer.py` dispatch factory.
- [x] Created `scripts/train_head.py` — trains from `path,label` manifest CSV.
- [x] Updated `scripts/latency.py` to report `engine_type`.
- [x] Added `DETECTOR_MODEL_PATH` config; `HF_HUB_OFFLINE=1` enforced.

---

## 5. Phase 2 Execution (T1 - 2026-10-24 23:20 IST) — Real Data & Honest Eval

- [x] Rewrote `scripts/eval_heldout.py` — accepts `--manifest PATH`; honest NO_DATA placeholder when no real audio.
- [x] Created `tests/smoke_synthetic_tones.py` — synthetic tone unit tests, not performance claims.
- [x] Rewrote `scripts/eval_slices.py` — reads slice manifests or reports NO_DATA.
- [x] Created `scripts/update_readme_metrics.py` — writes README metrics table from `reports/`.
- [x] Updated `scripts/run_kit.py` — `--kit PATH` for organiser kit.
- [x] Moved synthetic tones to `tests/fixtures/`.

---

## 6. Phase 3 Execution (T1 - 2026-10-24 23:30 IST) — Product Flow

- [x] Fixed `/api/eval/summary` — reads `reports/*.json`, no hardcodes.
- [x] Removed Google Fonts CDN from `frontend/index.html` and `frontend/src/index.css`.
- [x] System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.
- [x] `GET /` returns `fallback_mode: true/false`; frontend shows FALLBACK banner when true.

---

## 7. Phase 4 Execution (T1 - 2026-10-24 23:40 IST) — UI/UX Redesign

- [x] Restructured `App.tsx` to 4 tabs: Live Call / Customer Phone / Analyst / Trust.
- [x] Live Call: 3-column layout (TierCard | Waveform+Record | ScenarioStepper).
- [x] Footer strip: "Audio saved: 0 bytes" | latency | model version | MOCK badges.
- [x] Trust tab: live numbers from `reports/` only, privacy checklist, Real vs MOCK table.
- [x] Added `backend/tests/test_learned_engine.py` (shape, silence, telephony, fallback, no disk writes).
- [x] Added `backend/tests/test_no_fabricated_metrics.py` (README metrics match `reports/`).

---

## 8. Final Acceptance State

| Criterion | Status |
|---|---|
| pytest passes (new + existing tests) | DONE |
| Mic recording + judge file produce live verdict | DONE |
| Held-out real data in reports/ | GAP — stated honestly in MODEL_CARD |
| Hindi/regional speech evaluated | GAP — stated in MODEL_CARD |
| Real p95 latency measured | DONE (spectral engine; learned fallback identical) |
| README claims backed by reports/ | DONE |
| 4 demo scenarios end-to-end | DONE |
| 0 bytes audio on disk (tested) | DONE |
| No outbound network at runtime | DONE |
| Every mock labelled | DONE |
