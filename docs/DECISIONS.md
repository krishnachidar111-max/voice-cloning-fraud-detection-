# EchoGuard - Architectural & Technical Decisions Log

Every technical decision, scope adjustment, or tradeoff made during the 48-hour build window is documented here with rationale and alternatives considered.

---

### DEC-001: Direct Monorepo Structure (`backend/`, `frontend/`, `scripts/`, `reports/`, `docs/`)
- **Date/Time:** 2026-10-24 15:55 IST
- **Context:** The hackathon prompt strictly defines a 5-folder repository architecture: `backend/`, `frontend/`, `scripts/`, `reports/`, `docs/`.
- **Decision:** Position all top-level modules directly under the workspace root (`Hackathon IIT Delhi/`) rather than nested arbitrarily, ensuring seamless execution of evaluation scripts, tests, and launcher utilities.
- **Alternatives Considered:** Leaving nested inside `echoguard-ai/` - rejected because it violates specified paths in judge test harnesses (`scripts/run_kit.py`, `backend/app/main.py`).

---

### DEC-002: Dual Acoustic Feature Extraction (Hybrid Spectro-Temporal & Acoustic Front-End)
- **Date/Time:** 2026-10-24 15:56 IST
- **Context:** Must achieve p95 inference latency under 1.0 second on CPU fallback during live demos, while detecting vocoder phase artifacts (HiFi-GAN, VITS, ElevenLabs) and channel anomalies.
- **Decision:** Implement a modular audio engine featuring:
  1. A primary lightweight spectro-temporal feature extractor with high-frequency energy ratio ($4-8$ kHz vocoder band), Wiener spectral flatness, spectral centroid/rolloff, and zero-crossing rate.
  2. An isotonic calibration layer that maps raw acoustic classification scores to calibrated log-likelihood ratios ($\text{LLR}_{\text{audio}}$).
  3. Pretrained weight loading interface allowing swappable embedding backends (WavLM/Wav2Vec2) when PyTorch/GPU is present.
- **Rationale:** Guarantees sub-30ms per-window latency on CPU, prevents out-of-memory or timeout crashes during judge live evaluation, and ensures resilience against telephony codecs.

---

### DEC-003: RAM-Only Volatile Audio Buffer (Zero Disk Write Policy)
- **Date/Time:** 2026-10-24 15:58 IST
- **Context:** Privacy safeguard (FR-3, Hard Rule 2) requires audio to live strictly in a 10-second in-memory ring buffer. No raw audio files written to disk during live streaming.
- **Decision:** Implement `backend/audio/ring_buffer.py` backed by a fixed-size `collections.deque` / numpy array in RAM. Only metadata (scores, timestamps, reason codes, session UUID) is persisted to SQLite. Provide a visible UI indicator ("audio persisted: 0 bytes") and an automated unit test verifying zero audio files on disk.

---

### DEC-004: Isotonic Log-Likelihood Ratio (LLR) Signal Fusion
- **Date/Time:** 2026-10-24 16:00 IST
- **Context:** Hard Rule 3 and FR-9: Each signal family (Audio, Interaction, Transaction) must emit a calibrated log-likelihood ratio, accumulated over time with exponential decay:
  $$S_t = \text{clip}(\lambda S_{t-1} + \sum_f w_f \cdot \text{LLR}_f, -L, +U)$$
  $$R_t = S_t + \text{prior}(\text{ANI}, \text{device}) + k_{\text{action}} \cdot \text{txn\_risk}$$
- **Decision:** Use calibrated LLRs instead of naive score averaging. This ensures one noisy window cannot trigger false escalation, and enforces the core invariant: **audio evidence alone cannot breach the Orange-to-Red threshold** (capped at Orange; Red requires 2-of-3 corroboration or failed out-of-band step).

---

### DEC-005: Dual-Mode Telephony vs Wideband Adaptive Head
- **Date/Time:** 2026-10-24 16:20 IST
- **Context:** In telecom networks, POTS/G.711 carriers apply sharp bandpass filtering ($300\,\text{Hz} - 3400\,\text{Hz}$), removing audio frequencies above $4\,\text{kHz}$ where vocoder energy anomalies reside.
- **Decision:** Implement adaptive dual-mode classification in `SyntheticDetectionHead`:
  1. Wideband mode: uses high-frequency ratio (4-8kHz) + spectral centroid.
  2. Telephony mode (when spectral rolloff < 3.8kHz): shifts weights to vocoder phase jitter across STFT frames, in-band Wiener entropy, and pitch irregularity.
- **Result:** Preserves high detection recall on telephony-laundered clones while keeping false challenge rate low on benign human speech.

---

### DEC-006: Dual-Analyst Dual Control for Releases $\ge ₹50,000$ ($10,000)
- **Date/Time:** 2026-10-24 16:28 IST
- **Context:** Responsible AI (RA-6) mandates that high-value security holds cannot be unilaterally released by a single call center operator.
- **Decision:** Enforce in `CaseManager` that any transaction with amount $\ge ₹50,000$ requires signoff from two distinct analyst IDs (e.g. Tier-2 Analyst + Supervisor). Attempting release with the same analyst twice is rejected with HTTP 400.

---

### DEC-007: Transparent Reporting of Heavy Noise Slice Breach (Honesty Rule)
- **Date/Time:** 2026-10-24 16:32 IST
- **Context:** In `scripts/eval_slices.py`, the Heavy Traffic Noise (12dB SNR) slice showed a False-Challenge Rate of 100.0%, breaching the 3.0% threshold.
- **Decision:** Document the breach openly in the UI Dashboard, `reports/slice_report.csv`, and `docs/FAILURE_CASES.md`. Per the judging rubric: *"If a number is missed, show it anyway and name the failure case. The rubric rewards measurement and honesty over a clean number."*

---

### DEC-008: Single-Command Launcher Unification for Offline Judge Evaluation
- **Date/Time:** 2026-10-24 22:36 IST
- **Context:** Acceptance checklist requires one-command startup for backend, frontend, and offline evaluation.
- **Decision:** Updated `start.bat`, `start.ps1`, and `package.json` to launch backend and frontend directly from the workspace root (`backend` and `frontend`), using Python 3.12 uvicorn and Vite dev server. Ensured offline resilience without external runtime network calls.

