# EchoGuard AI - Data Card

## 1. Dataset Overview & Heritage

EchoGuard evaluation and benchmarking utilizes public research corpora and synthetic red-team sets adhering to the Pre-Event Disclosure Form:

| Corpus | Source & Citation | License | Samples | Primary Role |
|---|---|---|---|---|
| **ASVspoof 2021 DF** | Yamagishi et al. / ASVspoof Consortium | Open Access / Non-Commercial | 2,500 | Core synthetic voice clone held-out benchmark |
| **In-The-Wild Audio Deepfake** | Müller et al. (2022) | CC BY-NC 4.0 | 1,200 | Real-world deepfake generators (ElevenLabs, Tortoise) |
| **Common Voice (Indian Corpora)** | Mozilla Foundation | CC0 Public Domain | 800 | Bona fide baseline across Indian English, Hindi, Bengali, Tamil, Telugu |
| **ErrorX Red-Team Suite** | ErrorX Custom Scripts | MIT (Self-generated) | 250 | Telephony-augmented adversarial stress test |

---

## 2. Splitting & Leave-One-Generator-Out Protocol

To prevent data contamination and overly optimistic metrics:
- **No Overlapping Generators:** Evaluated generators (ElevenLabs_v2, HiFi-GAN, VITS, StyleTTS2, Tortoise) are strictly held out. The model is never evaluated on generator instances seen during threshold fitting.
- **Strict Speaker Separation:** Bona fide human speakers in evaluation splits do not appear in any feature calibration splits.
- **No Hand-Editing:** All evaluation numbers in `reports/` are generated directly by reproducible automated scripts (`scripts/eval_heldout.py`, `scripts/eval_slices.py`, `scripts/redteam.py`).

---

## 3. Telephony Augmentation Transforms

All evaluation clips undergo simulated telecom network degradations via `backend/audio/augment.py`:
1. **ITU-T G.711 $\mu$-law:** 8 kHz downsampling with 8-bit non-linear quantization.
2. **POTS Bandpass Filter:** Butterworth 4th-order filter limiting frequency response to $300\,\text{Hz} - 3400\,\text{Hz}$.
3. **VoIP Packet Loss:** Random 30ms burst frame drops (3% to 6% loss rate) with comfort noise fill.
4. **Additive Acoustic Noise:** Background street and call-center noise scaled to 12 dB - 28 dB SNR.

---

## 4. Privacy & Compliance Guarantees (DPDP Act 2023)
- **Zero Raw Data Stored:** Customer voice data is processed exclusively in volatile RAM and purged within 100ms of call termination.
- **Score-Only Telemetry:** Only numerical probability scores, log-likelihood ratios, and pseudonymous identifiers (`SESS-XXXXXXXX`) are recorded in the database.
- **No Secondary Use:** Audio features are used solely for real-time fraud defense; never repurposed for ad targeting, biometric tracking, or model retraining without explicit consent.
