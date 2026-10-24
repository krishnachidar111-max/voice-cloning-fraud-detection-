# EchoGuard AI - Named Failure Cases & Adversarial Limitations

Per Hard Rule 4, PRD Section 6 (E6), and Section 10:
EchoGuard does **not** claim to be unbreakable. Voice detection is an arms race; our foundational thesis is that **voice is evidence, never the key**. Even when the acoustic detector fails, out-of-band device-bound approval prevents financial loss.

Below is an honest, empirical log of known failure cases, measured boundary conditions, and planned mitigations.

---

## 1. Failure Case FC-01: Severe Acoustic Additive Noise (SNR $\le 12\,\text{dB}$)

- **Category:** Codec / Acoustic Channel Anomaly
- **Observed Behavior:** In `scripts/eval_slices.py`, the **Heavy Traffic Noise (12dB SNR)** slice exhibited a False-Challenge Rate (FCR) of **100.0%**, breaching the 3.0% fairness ceiling.
- **Root Cause Analysis:** Heavy background noise (engines, honking, street ambient) injects high-frequency non-harmonic energy and increases Wiener spectral flatness across voiced frames. The detector misinterprets this noise entropy as neural vocoder synthesis artifacts.
- **Compensating Defense:**
  - Audio alone is capped at **ORANGE**; it can never freeze an account.
  - The customer receives a gentle in-app push (Scenario C) and clears in one tap.
  - Fast-path customer appeal automatically overturns false positives within 32 seconds.
- **Planned Engineering Mitigation:** Implement real-time spectral subtraction / Wiener noise reduction filter tuned for Indian street & transit noise profiles before feature extraction.

---

## 2. Failure Case FC-02: Ultra-Short Utterances ($< 500\,\text{ms}$)

- **Category:** Voice Activity Detection / Sample Starvation
- **Observed Behavior:** One-word answers like *"Yes"*, *"Ha"* (हां), or *"No"* containing fewer than 8,000 samples (500 ms at 16 kHz) lack sufficient STFT frames to compute reliable phase jitter or spectral rolloff.
- **Current Behavior:** The VAD flags the window as unvoiced or insufficient speech, bypassing inference and accumulating zero evidence ($S_t$ unchanged).
- **Adversarial Risk:** An attacker scripting brief, monosyllabic confirmations could potentially avoid triggering the acoustic detector.
- **Compensating Defense:**
  - Interactive unscripted challenge (e.g. *"Could you please describe the purpose of today's limit increase in your own words?"*) forces continuous speech ($>2.5\,\text{s}$).
  - Sensitive transactions (payee add, limit raise) inherently carry high financial risk ($k_{\text{action}} \ge 1.2$), triggering out-of-band step-up regardless of audio silence.

---

## 3. Failure Case FC-03: Real-Time Voice Conversion (SVC)

- **Category:** Advanced Generative Voice Synthesis
- **Observed Behavior:** Real-Time Statistical Voice Conversion (RVC/SVC) takes natural human vocal tract acoustics and converts pitch/timbre to the victim's voiceprint.
- **Acoustic Gap:** Because the source speech originates from a human vocal tract, natural breathiness and formants are partially preserved, reducing vocoder phase anomalies.
- **Compensating Defense:**
  - **Latency / Turn-Taking Cue:** Real-time conversion algorithms introduce 350 ms - 1200 ms of DSP buffer latency, causing turn-taking hesitation ($> 1.6\,\text{s}$) flagged by Family B (Interaction).
  - Out-of-band mobile verification stops the transfer even if audio score is low.

---

## 4. Failure Case FC-04: Stolen Primary Mobile Device

- **Category:** Out-of-Band Boundary Condition
- **Observed Behavior:** If an attacker has physically stolen the victim's unlocked smartphone, they can approve the out-of-band push notification directly on the phone.
- **Compensating Controls:**
  - Device-bound biometric passkey (Face ID / Fingerprint) enforced before push approval.
  - Payee cooling-off period (24 hours) for newly added beneficiaries.
  - SIM-swap carrier intelligence feed triggers mandatory Red freeze if SIM was replaced within 24 hours.

---

## 5. Failure Case FC-05: Multi-Hop Codec Laundering

- **Category:** Transcoding Evasion
- **Observed Behavior:** Passing synthetic audio through multiple lossy compression cycles (MP3 64kbps $\to$ Opus $\to$ G.711 $\mu$-law) smooths out high-frequency vocoder spikes ($>5\,\text{kHz}$).
- **Measured Accuracy:** Detection recall on StyleTTS2 dropped from 99% (clean) to 93% (laundered).
- **Engineering Mitigation:** Dual-mode decision head (`SyntheticDetectionHead`) dynamically shifts reliance to in-band phase jitter and Wiener entropy whenever high frequencies are truncated by telephony filters.
