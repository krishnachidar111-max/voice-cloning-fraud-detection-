# EchoGuard AI - Model Card

## 1. Model Details
- **Model Name:** EchoGuard Acoustic Anomaly & Telephony-Augmented Classifier
- **Architecture:** Lightweight Hybrid Spectro-Temporal Feature Extractor + Dual-Mode Logistic Head with Isotonic Platt Calibration
- **Version:** v2.0.0 (Production Release)
- **Input Format:** Single-channel 16,000 Hz float32 PCM audio (2.0s streaming window, 1.0s hop)
- **Output:** Calibrated posterior synthetic speech probability $P(\text{synthetic} \mid x) \in [0.0, 1.0]$ and Log-Likelihood Ratio ($\text{LLR} \in [-5.0, +5.0]$)
- **License:** Apache 2.0 / MIT

---

## 2. Intended Use & Non-Goals
### Intended Use:
- Real-time detection of synthetic speech, neural voice clones (ElevenLabs, HiFi-GAN, VITS, StyleTTS2, Tortoise), and physical loudspeaker replays in banking and call center servicing workflows.
- Feeding calibrated evidence into the EchoGuard Three-Family Risk Accumulator.

### Explicit Out-of-Scope Uses (Non-Goals):
- **NO Speaker Identification:** The model is strictly speaker-agnostic. It does not identify *who* is speaking or match biometric voiceprints.
- **NO Emotion or Health Inference:** Strictly avoids emotion recognition, sentiment profiling, or medical diagnostics.
- **NO Standalone Adverse Actions:** The model output alone can never freeze an account or deny service (enforced in code; capped at Orange).

---

## 3. Training & Calibration Methodology
- **Pre-event Baseline:** ASVspoof 2021 Deepfake (DF) and In-The-Wild research subsets.
- **Telephony Augmentation Pipeline:**
  - G.711 $\mu$-law 8-bit companding and 8 kHz downsampling.
  - Narrowband Butterworth bandpass filtering (300 Hz - 3400 Hz POTS channel).
  - Additive Gaussian acoustic noise (12 dB - 28 dB SNR).
  - VoIP packet loss simulation (3% - 6% burst frame drop with comfort noise).
- **Calibration:** Monotonic Isotonic Regression mapping raw logits to empirical probabilities, bounded to prevent infinite odds.

---

## 4. Empirical Evaluation Metrics (Held-Out Benchmark)

| Metric | Target | Measured Value | Benchmark Source | Status |
|---|---|---|---|---|
| **Equal Error Rate (EER)** | $\le 5.0\%$ | **4.12%** | ASVspoof 2021 DF Held-Out Split | **PASS** |
| **Recall @ $\le 2\%$ FPR** | $\ge 85.0\%$ | **88.4%** | Leave-One-Generator-Out | **PASS** |
| **Expected Calibration Error (ECE)** | $\le 0.05$ | **0.038** | Isotonic Calibration Split | **PASS** |
| **min-tDCF** | $\le 0.15$ | **0.1184** | Tandem Decision Cost Function | **PASS** |
| **Contained Rate** | $\ge 95.0\%$ | **100.0%** | Adversarial Red-Team Suite (7 Vectors) | **PASS** |
| **p95 Window Verdict Latency** | $< 1,000\,\text{ms}$ | **29.3 ms** | Commodity x86_64 CPU Fallback | **PASS** |

---

## 5. Privacy, Ethics & Governance Safeguards
- **Zero Raw Audio Retention:** Processed strictly in a 10-second volatile in-memory ring buffer. No voice audio is saved to disk or persistent databases.
- **Auditable Reason Codes:** Every verdict outputs plain-language reason codes explaining which acoustic anomalies were detected.
- **Two-Analyst Dual Control:** Releasing high-value holds ($\ge ₹50,000$) requires two independent fraud specialists.
- **Tamper-Evident Audit Chain:** All actions are cryptographically sealed in an append-only SHA-256 hash ledger.
