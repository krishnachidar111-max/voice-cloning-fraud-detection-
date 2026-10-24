# EchoGuard - Assets, Dependencies & Dataset Inventory

Per Hard Rule 1 (Pre-Event Disclosure Conformance), every pre-existing asset, external model, dependency, and dataset used in EchoGuard is inventoried below with license, provider, and operational scope.

---

## 1. External Models & Pretrained Representations

| Asset | Provider / Author | License | Description & Usage | Status |
|---|---|---|---|---|
| **WavLM Base+** | Microsoft / Hugging Face | MIT License | Pretrained self-supervised speech representation model used for phonetic & spectral feature extraction. | Offline weights cache / Distilled CPU fallback |
| **AASIST / Acoustic Spectral Head** | Audio-Visual Speech Processing Lab / ErrorX custom | Apache 2.0 / MIT | Graph attention & spectral anomaly classifier trained for synthetic artifact detection. | Live-trained & Calibrated |
| **Isotonic Calibrator** | scikit-learn | BSD-3-Clause | Non-parametric monotonic regression mapping raw classifier outputs to calibrated probabilities and LLRs. | Live fit on validation split |

---

## 2. Evaluation & Benchmark Datasets

| Dataset | Source / Citation | License | Samples Used | Purpose |
|---|---|---|---|---|
| **ASVspoof 2021 DF Subset** | ASVspoof Consortium | Open Access / Academic | 2,500 held-out bona fide & deepfake speech samples | Primary benchmark for EER, min-tDCF, and leave-one-generator-out evaluation |
| **In-The-Wild Audio Deepfake** | Müller et al. | CC BY-NC 4.0 | 1,200 real-world public clones (ElevenLabs, Tortoise, etc.) | Held-out generator testing |
| **Common Voice (Indian Accents & Dialects)** | Mozilla Foundation | CC0 Public Domain | 800 bona fide Indian English & Hindi audio clips | Per-slice fairness & false-challenge rate analysis |
| **ErrorX Red-Team Synthetic Suite** | ErrorX Team | MIT (Self-generated) | 250 scripted attack samples with telephony codecs ($\mu$-law, AMR, Opus) | Red-team regression & containment rate verification |

---

## 3. Core Software Libraries & Frameworks

| Library | Version | License | Role in System |
|---|---|---|---|
| **FastAPI** | 0.162.0+ | MIT | High-performance asynchronous REST & WebSocket API gateway |
| **Uvicorn** | 0.47.0+ | BSD-3-Clause | ASGI web server for real-time WebSocket audio streaming |
| **Pydantic** | 2.14.0+ | MIT | Data validation, API request/response typing, configuration enforcement |
| **NumPy** | 2.4.0+ | BSD-3-Clause | Vectorized audio signal operations, ring buffer, FFT spectral processing |
| **SciPy** | 1.17.0+ | BSD-3-Clause | Digital signal processing: STFT, butterworth filtering, telephony simulation |
| **scikit-learn** | 1.8.0+ | BSD-3-Clause | Isotonic calibration, evaluation metrics (ROC/DET, EER, ECE) |
| **SQLite3** | 3.45+ | Public Domain | Zero-configuration local database for sessions, scores, case management, and audit logs |
| **React** | 19.0+ | MIT | Frontend UI component framework for Agent, Analyst, Customer, and Demo views |
| **Vite** | 6.0+ | MIT | Frontend development server and bundle orchestrator |
| **Lucide React** | 1.16+ | ISC | Modern cybersecurity and financial UI iconography |

---

## 4. Hardware & Runtime Constraints

- **Live Demo Target:** Offline-capable standalone execution on commodity x86_64 CPU (no internet or cloud GPU required).
- **Inference Budget:** $<100\,\text{ms}$ per 2-second audio window on CPU.
- **Privacy Guarantee:** $0$ bytes of raw audio saved to disk. All buffers destroyed on call termination.
