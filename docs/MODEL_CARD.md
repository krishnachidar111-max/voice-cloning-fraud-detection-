# EchoGuard AI - Model Card

## 1. Model Details
- **Model Name:** EchoGuard Learned Audio Engine (`LearnedAudioEngine`)
- **Architecture:** 25-Dimensional Acoustic Feature Extractor (Phase Jitter, Sub-band Contrasts, Mel Energies, Wiener Flatness, HF/LF/Mid Ratios) + scikit-learn `LogisticRegression` Head + `IsotonicRegression` Calibrator.
- **Model File:** `models/head.joblib` (automatic fallback to spectral heuristic when file is absent).
- **Version:** v2.0.0 (Production Release)
- **Input Format:** Single-channel 16,000 Hz float32 PCM audio (2.0s streaming window, 1.0s hop).
- **Output:** Calibrated posterior synthetic speech probability $P(\text{synthetic} \mid x) \in [0.0, 1.0]$ and Log-Likelihood Ratio ($\text{LLR} \in [-5.0, +5.0]$).
- **Inference Hardware Target:** Commodity x86_64 CPU without GPU dependency.
- **License:** Apache 2.0 / MIT

---

## 2. Intended Use & Non-Goals
### Intended Use:
- Real-time detection of synthetic speech, neural voice clones (ElevenLabs, HiFi-GAN, VITS, StyleTTS2, Tortoise), and physical loudspeaker replays in banking and call center servicing workflows.
- Feeding calibrated evidence into the EchoGuard Three-Family Risk Accumulator.

### Explicit Out-of-Scope Uses (Non-Goals):
- **NO Speaker Identification:** The model is strictly speaker-agnostic. It does not identify *who* is speaking or match biometric voiceprints.
- **NO Emotion or Health Inference:** Strictly avoids emotion recognition, sentiment profiling, or medical diagnostics.
- **NO Standalone Adverse Actions:** The model output alone can never freeze an account or deny service (enforced in code: audio score alone is strictly capped at ORANGE).

---

## 3. Training & Calibration Methodology
- **Learned Features (25 Dimensions):**
  - HF energy ratio (4-8 kHz), LF energy ratio (<1 kHz), Mid energy ratio (1-4 kHz).
  - Spectral centroid, rolloff, Wiener flatness, zero-crossing rate.
  - Inter-frame STFT phase angle jitter (detects neural vocoder phase continuity breaks).
  - Spectral bandwidth, 6-band spectral contrast, 4-band Mel filterbank energies.
  - Temporal flatness variance, G.711 telephony flag, high-frequency flatness.
- **Telephony Augmentation Pipeline:**
  - G.711 $\mu$-law 8-bit companding and 8 kHz downsampling.
  - Narrowband Butterworth bandpass filtering (300 Hz - 3400 Hz POTS channel).
  - Additive Gaussian acoustic noise (12 dB - 28 dB SNR).
  - VoIP packet loss simulation (3% - 6% burst frame drop with comfort noise).
- **Calibration:** Monotonic Isotonic Regression mapping raw logits to empirical probabilities, bounded to prevent infinite odds.

---

## 4. Empirical Evaluation Metrics (Directly Grounded in `reports/`)

All values below reflect live evaluation measurements saved in `reports/`:

| Metric | Target | Measured Value | Benchmark Source | Status |
|---|---|---|---|---|
| **Equal Error Rate (EER)** | $\le 5.0\%$ | **15.2%** | `reports/heldout_metrics.json` | **OPEN (Model Improvement Roadmap)** |
| **Recall @ $\le 2\%$ FPR** | $\ge 85.0\%$ | **0.0%** | `reports/heldout_metrics.json` | **OPEN (Threshold Tuning Roadmap)** |
| **Expected Calibration Error (ECE)** | $\le 0.05$ | **0.2413** | `reports/heldout_metrics.json` | **OPEN** |
| **min-tDCF** | $\le 0.15$ | **0.118** | `reports/heldout_metrics.json` | **PASS** |
| **Per-Generator Detected Recall** | $\ge 90.0\%$ | **99.0% - 100.0%** | ElevenLabs, HiFi-GAN, VITS, StyleTTS2, Tortoise | **PASS** |
| **Contained Rate** | $\ge 95.0\%$ | **100.0%** | `reports/redteam_report.json` (7 Vectors) | **PASS** |
| **p95 Window Verdict Latency** | $< 1,000\,\text{ms}$ | **29.26 ms** | `reports/latency_report.json` (CPU Fallback) | **PASS** |

> **Regional Indian Language Evaluation Gap Disclosure:**
> Per the Hackathon Transparency Guidelines, while clean Indian English and synthetic telephony dialects were tested in `eval_slices.py`, real regional accents (Hindi, Bengali, Tamil, Telugu) under heavy traffic noise (12dB SNR) currently exhibit an elevated False Challenge Rate (documented in `FAILURE_CASES.md`). Crucially, EchoGuard's core thesis ensures that even when the acoustic detector is challenged by noisy regional accents, **the customer is never locked out**; benign requests pass through a seamless 1-tap mobile push confirmation rather than account freezes.

---

## 5. Privacy, Ethics & Governance Safeguards
- **Zero Raw Audio Retention:** Processed strictly in a 10-second volatile in-memory ring buffer. 0 bytes of voice audio saved to disk or persistent databases.
- **Auditable Reason Codes:** Every verdict outputs plain-language reason codes explaining which acoustic anomalies were detected.
- **Two-Analyst Dual Control:** Releasing high-value holds ($\ge ₹50,000$) requires two independent fraud specialists.
- **Tamper-Evident Audit Chain:** All actions are cryptographically sealed in an append-only SHA-256 hash ledger.
