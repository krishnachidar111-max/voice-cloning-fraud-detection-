import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Upload,
  Play,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Sparkles,
  Smartphone,
  PhoneCall,
  Lock,
  ArrowRight
} from 'lucide-react';
import { StreamingVerdict, analyzeAudioFile, requestStepUp } from '../services/api';

interface DemoControlProps {
  verdict: StreamingVerdict | null;
  setVerdict: (v: StreamingVerdict | null) => void;
  onNavigateToCustomer: () => void;
  onNavigateToAnalyst: () => void;
}

export const DemoControl: React.FC<DemoControlProps> = ({
  verdict,
  setVerdict,
  onNavigateToCustomer,
  onNavigateToAnalyst
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [selectedAction, setSelectedAction] = useState('add_payee');
  const [amount, setAmount] = useState<number>(85000);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string>('scenario_b');
  const [sessionId, setSessionId] = useState<string>('SESS-DEMO-8041');
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // 1. Microphone Live Recording Handler
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlobUrl(URL.createObjectURL(audioBlob));
        const file = new File([audioBlob], 'live_mic_recording.wav', { type: 'audio/wav' });
        await handleAudioFileProcess(file);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      alert('Microphone access denied or unavailable: ' + err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // 2. Audio File Processing (Upload or Preset)
  const handleAudioFileProcess = async (file: File) => {
    setIsProcessing(true);
    try {
      const res = await analyzeAudioFile(file, sessionId, selectedAction, amount);
      setVerdict(res);
    } catch (err) {
      console.error('Inference error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setAudioBlobUrl(URL.createObjectURL(file));
      handleAudioFileProcess(file);
    }
  };

  // 3. Scenario Presets
  const applyPreset = async (scenario: string) => {
    setActiveScenario(scenario);
    setIsProcessing(true);

    if (scenario === 'scenario_a') {
      // Legit Customer, Balance Check
      setSelectedAction('balance_inquiry');
      setAmount(0);
      setVerdict({
        session_id: 'SESS-LEGIT-1001',
        timestamp: new Date().toISOString(),
        window_index: 1,
        tier: 'GREEN',
        risk_score: 0.35,
        accumulated_evidence: 0.35,
        llr_audio: -2.1,
        llr_interaction: -1.2,
        llr_transaction: -2.5,
        reason_codes: [
          {
            code: 'SYS-ROUTINE-VERIFICATION',
            family: 'SYSTEM',
            severity: 'LOW',
            description: 'All monitored signals within standard operational baselines.',
            plain_language_explanation: 'Natural human voice cadence and typical balance inquiry. Zero friction applied.'
          }
        ],
        audio_persisted_bytes: 0,
        processing_latency_ms: 18.4,
        agent_guidance: 'Standard customer servicing. All security verifications clear.',
        recommended_action: 'Proceed with requested workflow normally.'
      });
      setIsProcessing(false);
    } else if (scenario === 'scenario_b') {
      // Cloned Voice Attacker at Contact Center
      setSelectedAction('add_payee');
      setAmount(95000);
      setVerdict({
        session_id: 'SESS-ATTACK-2002',
        timestamp: new Date().toISOString(),
        window_index: 3,
        tier: 'RED',
        risk_score: 5.4,
        accumulated_evidence: 5.4,
        llr_audio: 4.8,
        llr_interaction: 1.6,
        llr_transaction: 4.2,
        reason_codes: [
          {
            code: 'AUD-VOCODER-HF-DISRUPTION',
            family: 'AUDIO',
            severity: 'HIGH',
            description: 'Neural vocoder phase anomalies in 4-8kHz synthesis band.',
            plain_language_explanation: 'Synthetic voice clone detected with neural synthesis artifacts.'
          },
          {
            code: 'TXN-RECENT-CREDENTIAL-CHANGE',
            family: 'TRANSACTION',
            severity: 'CRITICAL',
            description: 'SIM-swap carrier signal reported 4 hours prior.',
            plain_language_explanation: 'Mobile carrier registered a SIM card replacement shortly before this transaction.'
          },
          {
            code: 'INT-LATENCY-TURN-DELAY',
            family: 'INTERACTION',
            severity: 'MEDIUM',
            description: 'Turn-taking latency exceeded 1.6s, characteristic of real-time TTS buffer lag.',
            plain_language_explanation: 'Unusual pauses detected between prompts, indicating text-to-speech generation delay.'
          }
        ],
        audio_persisted_bytes: 0,
        processing_latency_ms: 28.5,
        agent_guidance: 'Security policy hold triggered. Warm transfer to Senior Fraud Specialist required.',
        recommended_action: 'Keep customer on hold. Account temporarily protected pending analyst review.'
      });
      setIsProcessing(false);
    } else if (scenario === 'scenario_c') {
      // Genuine Accented Customer on Noisy Line (False-Positive Path)
      setSelectedAction('raise_limit');
      setAmount(30000);
      setVerdict({
        session_id: 'SESS-ACCENT-3003',
        timestamp: new Date().toISOString(),
        window_index: 2,
        tier: 'AMBER',
        risk_score: 1.85,
        accumulated_evidence: 1.85,
        llr_audio: 0.9,
        llr_interaction: -0.4,
        llr_transaction: 1.2,
        reason_codes: [
          {
            code: 'AUD-TELEPHONY-CODEC-CHANNEL',
            family: 'AUDIO',
            severity: 'LOW',
            description: 'Elevated acoustic background noise on cellular G.711 channel.',
            plain_language_explanation: 'High ambient noise detected on the line. One-tap mobile app push sent to verify identity smoothly.'
          }
        ],
        audio_persisted_bytes: 0,
        processing_latency_ms: 21.2,
        agent_guidance: 'Routine high-assurance confirmation initiated.',
        recommended_action: 'Prompt customer to tap Confirm on their mobile banking notification.'
      });
      setIsProcessing(false);
    } else if (scenario === 'scenario_d') {
      // Customer-Side UPI Collect Scam
      setSelectedAction('upi_collect_request');
      setAmount(45000);
      setVerdict({
        session_id: 'SESS-UPI-4004',
        timestamp: new Date().toISOString(),
        window_index: 2,
        tier: 'ORANGE',
        risk_score: 3.4,
        accumulated_evidence: 3.4,
        llr_audio: 3.1,
        llr_interaction: 1.2,
        llr_transaction: 2.8,
        reason_codes: [
          {
            code: 'TXN-HIGH-SENSITIVITY-ACTION',
            family: 'TRANSACTION',
            severity: 'HIGH',
            description: 'UPI collect approval requested while customer is actively engaged on a call.',
            plain_language_explanation: 'A collect request was presented while customer is on a call. High probability of social engineering.'
          }
        ],
        safety_rule_applied: 'SAFETY_RULE_1_AUDIO_ALONE_CAPPED_AT_ORANGE',
        audio_persisted_bytes: 0,
        processing_latency_ms: 24.1,
        agent_guidance: 'Secondary authentication required for sensitive action.',
        recommended_action: 'Mandatory mobile app approval in progress. Do not proceed until verified.'
      });
      setIsProcessing(false);
    }
  };

  const handleTriggerStepUp = async () => {
    if (!verdict) return;
    try {
      await requestStepUp(verdict.session_id, selectedAction, amount, 'Rohan Verma (New Payee)');
      onNavigateToCustomer();
    } catch (e) {
      alert('Failed to request step-up challenge: ' + e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner: Core Thesis & Zero-Disk Privacy Guarantee */}
      <div className="glass-panel" style={{ padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', borderLeft: '4px solid #3b82f6' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', letterSpacing: '-0.02em' }}>Live Voice Defense Controller</h2>
            <span className="mock-pill">Interactive Demo Hub</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Core Thesis: <span style={{ color: '#38bdf8', fontWeight: '600' }}>"Voice is evidence, never the key."</span> Even if the audio detector misses, the out-of-band step blocks the fraud.
          </p>
        </div>

        {/* 0-byte Disk Audio Compliance Shield */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '10px 16px', borderRadius: '10px' }}>
          <ShieldCheck style={{ color: '#10b981' }} size={24} />
          <div>
            <div style={{ fontSize: '0.78rem', color: '#6ee7b7', fontWeight: '600', textTransform: 'uppercase' }}>RAM-Only Privacy Guarantee</div>
            <div style={{ fontSize: '0.92rem', fontWeight: '700', color: '#10b981' }}>Audio Persisted: 0 bytes</div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* Left Column: Audio Ingest & Presets */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Audio Input Card */}
          <div className="glass-panel" style={{ padding: '22px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Mic size={18} style={{ color: '#38bdf8' }} /> Audio Ingestion Stream
            </h3>

            {/* Mic and File buttons */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '18px' }}>
              <button
                onClick={isRecording ? stopRecording : startRecording}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  border: isRecording ? '1px solid #ef4444' : '1px solid rgba(255,255,255,0.1)',
                  background: isRecording ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255,255,255,0.05)',
                  color: isRecording ? '#f87171' : 'var(--text-main)',
                  transition: 'all 0.2s'
                }}
              >
                {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
                {isRecording ? 'Stop Recording' : 'Record Mic'}
              </button>

              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  border: '1px solid rgba(255,255,255,0.1)',
                  background: 'rgba(255,255,255,0.05)',
                  color: 'var(--text-main)',
                  textAlign: 'center'
                }}
              >
                <Upload size={18} />
                Upload WAV
                <input type="file" accept="audio/*" onChange={handleFileUpload} style={{ display: 'none' }} />
              </label>
            </div>

            {audioBlobUrl && (
              <div style={{ marginTop: '10px', marginBottom: '14px' }}>
                <audio controls src={audioBlobUrl} style={{ width: '100%', height: '36px' }} />
              </div>
            )}

            {/* Action Sensitivity & Amount Selector */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Banking Action Type</label>
                <select
                  value={selectedAction}
                  onChange={(e) => setSelectedAction(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                >
                  <option value="balance_inquiry">Balance Inquiry (Low Sensitivity)</option>
                  <option value="add_payee">Add Beneficiary / Payee (High Sensitivity)</option>
                  <option value="raise_limit">Raise Daily Limit (High Sensitivity)</option>
                  <option value="credentials_reset">Reset Passcode / PIN (Critical)</option>
                  <option value="sim_swap_signal">SIM Swap Signal Reported (Critical)</option>
                  <option value="upi_collect_request">UPI Collect Request (Scenario S1)</option>
                  <option value="wire_transfer">RTGS / Wire Transfer</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Transfer Amount (INR ₹)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            </div>
          </div>

          {/* India-Grounded Scenario Presets */}
          <div className="glass-panel" style={{ padding: '22px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} style={{ color: '#f59e0b' }} /> Threat Scenario Presets (Stage 2)
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button
                onClick={() => applyPreset('scenario_a')}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: activeScenario === 'scenario_a' ? '1px solid #10b981' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_a' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  color: 'var(--text-main)'
                }}
              >
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>Scenario A: Legitimate Customer</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Natural voice, balance check → Zero added friction</div>
                </div>
                <span className="tier-badge tier-badge-green" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>GREEN</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_b')}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: activeScenario === 'scenario_b' ? '1px solid #ef4444' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_b' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  color: 'var(--text-main)'
                }}
              >
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>Scenario B: Cloned-Voice Attacker (S2)</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Contact center payee add → Push denied → Red Freeze</div>
                </div>
                <span className="tier-badge tier-badge-red" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>RED</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_c')}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: activeScenario === 'scenario_c' ? '1px solid #f59e0b' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_c' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  color: 'var(--text-main)'
                }}
              >
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>Scenario C: Accented on Noisy Line</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Genuine rural dialect → One-tap Amber clearance</div>
                </div>
                <span className="tier-badge tier-badge-amber" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>AMBER</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_d')}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: activeScenario === 'scenario_d' ? '1px solid #f97316' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_d' ? 'rgba(249, 115, 22, 0.12)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  color: 'var(--text-main)'
                }}
              >
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>Scenario D: Customer-Side UPI Scam (S1)</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Fake relative call → Intercepted at UPI Gateway hook</div>
                </div>
                <span className="tier-badge tier-badge-orange" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>ORANGE</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Live Verdict Display & Safety Invariants */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Real-Time Tier Verdict Card */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Fused Policy Engine Verdict
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                Session: {verdict ? verdict.session_id : sessionId}
              </span>
            </div>

            {/* Big Tier Badge */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
              {verdict?.tier === 'GREEN' && (
                <div className="tier-badge tier-badge-green" style={{ fontSize: '1.25rem', padding: '10px 22px' }}>
                  <ShieldCheck size={26} /> GREEN: PASS WORKFLOW
                </div>
              )}
              {verdict?.tier === 'AMBER' && (
                <div className="tier-badge tier-badge-amber" style={{ fontSize: '1.25rem', padding: '10px 22px' }}>
                  <AlertTriangle size={26} /> AMBER: IN-APP STEP-UP
                </div>
              )}
              {verdict?.tier === 'ORANGE' && (
                <div className="tier-badge tier-badge-orange" style={{ fontSize: '1.25rem', padding: '10px 22px' }}>
                  <Lock size={26} /> ORANGE: MANDATORY OOB
                </div>
              )}
              {verdict?.tier === 'RED' && (
                <div className="tier-badge tier-badge-red" style={{ fontSize: '1.25rem', padding: '10px 22px' }}>
                  <Flame size={26} /> RED: SECURITY HOLD
                </div>
              )}
              {!verdict && (
                <div style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Awaiting audio input or scenario selection...</div>
              )}
            </div>

            {/* Fused Risk & Multi-Family Breakdown */}
            {verdict && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Accumulated Risk Score (R):</span>
                  <span style={{ fontSize: '1.1rem', fontWeight: '700', color: verdict.risk_score > 3.0 ? '#f87171' : '#34d399', fontFamily: 'monospace' }}>
                    {verdict.risk_score.toFixed(2)}
                  </span>
                </div>

                {/* 3 Family LLR Progress Bars */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                  <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '4px' }}>Audio LLR (45%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: '700', color: verdict.llr_audio > 1.0 ? '#fb923c' : '#94a3b8', fontFamily: 'monospace' }}>
                      {verdict.llr_audio.toFixed(2)}
                    </div>
                  </div>

                  <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '4px' }}>Interaction (25%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: '700', color: verdict.llr_interaction > 1.0 ? '#fb923c' : '#94a3b8', fontFamily: 'monospace' }}>
                      {verdict.llr_interaction.toFixed(2)}
                    </div>
                  </div>

                  <div style={{ background: 'rgba(0,0,0,0.25)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '4px' }}>Transaction (30%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: '700', color: verdict.llr_transaction > 1.0 ? '#fb923c' : '#94a3b8', fontFamily: 'monospace' }}>
                      {verdict.llr_transaction.toFixed(2)}
                    </div>
                  </div>
                </div>

                {/* Safety Invariant Banner */}
                {verdict.safety_rule_applied && (
                  <div style={{ padding: '10px 14px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', fontSize: '0.82rem', color: '#93c5fd' }}>
                    <strong>Safety Rule Enforced:</strong> Audio alone capped at Orange. Cannot trigger Red unilateral freeze without corroboration.
                  </div>
                )}
              </div>
            )}

            {/* Quick Actions to Out-of-Band & Case Console */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '10px' }}>
              <button
                onClick={handleTriggerStepUp}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                <Smartphone size={18} /> Test Out-Of-Band Push
              </button>

              <button
                onClick={onNavigateToAnalyst}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '12px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  background: 'rgba(255,255,255,0.06)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--border-subtle)',
                  cursor: 'pointer'
                }}
              >
                View Analyst Queue <ArrowRight size={16} />
              </button>
            </div>
          </div>

          {/* Plain-Language Explainable Reason Codes Card */}
          <div className="glass-panel" style={{ padding: '22px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', marginBottom: '14px' }}>Explainable Reason Codes (FR-14 & FR-20)</h3>

            {verdict?.reason_codes && verdict.reason_codes.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {verdict.reason_codes.map((rc, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      background: 'rgba(0,0,0,0.2)',
                      border: '1px solid var(--border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#38bdf8', fontFamily: 'monospace' }}>
                        {rc.code}
                      </span>
                      <span style={{ fontSize: '0.72rem', padding: '2px 6px', borderRadius: '4px', background: rc.severity === 'HIGH' || rc.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)', color: rc.severity === 'HIGH' || rc.severity === 'CRITICAL' ? '#f87171' : '#fbbf24' }}>
                        {rc.severity}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{rc.plain_language_explanation}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No active reason codes.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
