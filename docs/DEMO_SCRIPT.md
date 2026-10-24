# EchoGuard AI - Stage 2 Live Demo Script (3 Minutes)

**Team:** ErrorX (Track 1: Voice Cloning Fraud Detection)
**Event:** Amazon AI Cyber Security Hackathon, IIT Delhi
**Target Length:** 3 Minutes + Open Jury Q&A

---

## 0:00 - 0:30 | The Core Thesis & The Threat
- **Speaker:** ML Lead / Presenter
- *"Judges, voice cloning is no longer theoretical. With 3 seconds of public audio, an attacker can clone any voice. Today, Indian banks rely on voice ID, knowledge questions, and agent intuition. Detection alone is an arms race where false alarms fall hardest on elderly, accented, and speech-impaired citizens."*
- *"EchoGuard is built on one inviolable principle: **Voice is evidence, never the key.** Even if our audio detector misses, an out-of-band, device-bound approval step means the fraud still fails."*
- *"Let us show you this live across four India-grounded scenarios."*

---

## 0:30 - 1:10 | Scenario A: Legitimate Customer, Balance Check
- **Action:**
  1. In the **Demo Controller**, select **Scenario A (Legitimate Customer)**.
  2. Click **Apply Preset**.
- **On Screen:**
  - Tier lights up **GREEN**.
  - Notice the green compliance badge: **"Audio Persisted: 0 bytes"**.
  - Switch to **Agent Widget**: Agent sees standard prompt: *"Standard customer servicing. All security verifications clear."*
- **Script:**
  - *"A genuine customer calls to check their balance. Low risk, natural speech cadence. EchoGuard assigns GREEN. Zero friction, zero added steps. Most importantly, not a single byte of their audio is saved to disk. All processing happened in a 10-second volatile RAM ring buffer."*

---

## 1:10 - 2:00 | Scenario B: Cloned-Voice Attacker at Contact Center (Threat S2)
- **Action:**
  1. In **Demo Controller**, select **Scenario B: Cloned-Voice Attacker (S2)**.
  2. Action: **Add Payee & Raise Daily Limit to ₹95,000**.
  3. Click **Apply Preset** (or upload a judge-supplied clone sample).
  4. Click **Test Out-Of-Band Push** -> switches to **Customer App Simulator**.
  5. In the smartphone simulator, the real customer sees an unauthorized push alert: *Add Beneficiary 'Rohan Verma' ₹95,000*.
  6. Tap **DENY (FRAUD)**.
  7. Switch to **Analyst Console**.
- **On Screen:**
  - Tier escalates to **RED: SECURITY HOLD**.
  - Reason codes light up: `AUD-VOCODER-HF-DISRUPTION`, `TXN-RECENT-CREDENTIAL-CHANGE`, `INT-LATENCY-TURN-DELAY`.
  - Analyst Rohit reviews notes and attempts release -> **Dual-Control Warning:** *"Transaction exceeds ₹50,000; requires second supervisor approval."*
  - Switch to Supervisor Priya -> Signoff complete, hold confirmed or released.
- **Script:**
  - *"Here is the attack: An attacker uses an ElevenLabs clone to add a new payee and raise limits. Our detector catches the vocoder phase anomaly and SIM-swap signal. Amber push goes to the real victim's mobile app. The victim taps DENY. The session immediately freezes into RED. The analyst console lights up with explainable reason codes. Because the amount is ₹95,000, our code enforces dual-analyst signoff before any hold can be released."*

---

## 2:00 - 2:30 | Scenario C: Genuine Accented Customer on Noisy Line (False-Positive Path)
- **Action:**
  1. In **Demo Controller**, select **Scenario C: Accented on Noisy Line**.
  2. Switch to **Customer App Simulator** and click **Falsely Flagged? Fast-Path Appeal (FR-20)**.
- **On Screen:**
  - Screen displays instant resolution: **Status: OVERTURNED in 32.4 seconds**.
  - Shows plain-language explanation: *"Why it fired: Severe acoustic background noise resembled synthetic spectral flatness. Cleared via one-tap biometric verification. Zero voiceprints stored."*
- **Script:**
  - *"What happens when a genuine rural or accented customer calls from a noisy railway station? They receive an AMBER push, clear it in one tap, and our portal tells them exactly why it fired in plain words. They are never accused, and never locked out."*

---

## 2:30 - 3:00 | Scenario D & Judge Variation: Simulated UPI Collect Interception
- **Action:**
  1. In **Customer App Simulator**, click **Simulate Incoming UPI Collect (₹45,000)**.
  2. Gateway hook intercepts and displays **High-Risk UPI Collect Intercepted** interstitial.
  3. Switch to **Dashboard**: show the **Per-Slice Fairness Table** and click **Verify Cryptographic Chain**.
- **Script:**
  - *"In India, the most common voice scam is a fake relative calling to pressure a UPI collect approval. Our simulated UPI switch intercepts the payment right at payment time because an active high-risk call is detected. Finally, our Governance Dashboard verifies 100% containment on red-team attacks, p95 latency under 30 milliseconds, and cryptographic hash verification proving our audit trail is tamper-evident."*
  - *"Judges, we invite you to record your own voice or feed any audio file of your choice."*
