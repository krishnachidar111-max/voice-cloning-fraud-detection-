import React, { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Upload,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Sparkles,
  Smartphone,
  PhoneCall,
  Lock,
  ArrowRight,
  Activity,
  Layers,
  ChevronRight,
  Info
} from 'lucide-react';
import { StreamingVerdict, analyzeAudioFile, requestStepUp } from '../services/api';

interface DemoControlProps {
  verdict: StreamingVerdict | null;
  setVerdict: (v: StreamingVerdict | null) => void;
  onNavigateToCustomer: () => void;
  onNavigateToAnalyst: () => void;
  isFallbackMode?: boolean;
}

export const DemoControl: React.FC<DemoControlProps> = ({
  verdict,
  setVerdict,
  onNavigateToCustomer,
  onNavigateToAnalyst,
  isFallbackMode = false
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [selectedAction, setSelectedAction] = useState('add_payee');
  const [amount, setAmount] = useState<number>(85000);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string>('scenario_b');
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(2);
  const [sessionId, setSessionId] = useState<string>('SESS-DELHI-8041');
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);
  const [historyScores, setHistoryScores] = useState<number[]>([0.1, 0.2, 0.45, 0.8, 1.4, 2.2, 3.8, 5.4]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Animated live waveform simulation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let phase = 0;
    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const mid = height / 2;

      ctx.beginPath();
      ctx.lineWidth = 2;
      ctx.strokeStyle = isRecording ? '#ef4444' : '#38bdf8';

      for (let x = 0; x < width; x++) {
        const freq = isRecording ? 0.05 : 0.02;
        const amp = isRecording ? 25 * Math.sin(x * 0.01 + phase) : 10;
        const y = mid + Math.sin(x * freq + phase) * amp * Math.sin(x * 0.02);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      phase += isRecording ? 0.15 : 0.03;
      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [isRecording]);

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

  // 2. Audio File Processing
  const handleAudioFileProcess = async (file: File) => {
    setIsProcessing(true);
    try {
      const res = await analyzeAudioFile(file, sessionId, selectedAction, amount);
      setVerdict(res);
      setHistoryScores(prev => [...prev.slice(-7), res.risk_score]);
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
  const applyPreset = (scenario: string) => {
    setActiveScenario(scenario);
    if (scenario === 'scenario_a') {
      setSelectedAction('balance_inquiry');
      setAmount(0);
      setCurrentStepIndex(1);
      setHistoryScores([0.05, 0.1, 0.12, 0.15, 0.2, 0.18, 0.22, 0.35]);
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
    } else if (scenario === 'scenario_b') {
      setSelectedAction('add_payee');
      setAmount(95000);
      setCurrentStepIndex(2);
      setHistoryScores([0.2, 0.6, 1.2, 2.1, 3.4, 4.2, 4.9, 5.4]);
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
    } else if (scenario === 'scenario_c') {
      setSelectedAction('raise_limit');
      setAmount(30000);
      setCurrentStepIndex(2);
      setHistoryScores([0.3, 0.5, 0.8, 1.1, 1.4, 1.6, 1.75, 1.85]);
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
    } else if (scenario === 'scenario_d') {
      setSelectedAction('upi_collect_request');
      setAmount(45000);
      setCurrentStepIndex(3);
      setHistoryScores([0.4, 0.9, 1.5, 2.1, 2.6, 3.0, 3.2, 3.4]);
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

  // Plain sentence helper
  const getPlainSentence = (tier?: string) => {
    switch (tier) {
      case 'GREEN': return 'Sounds genuine';
      case 'AMBER': return 'Extra check needed';
      case 'ORANGE': return 'Verification required';
      case 'RED': return 'Sensitive actions frozen';
      default: return 'Awaiting live input';
    }
  };

  const getTierColor = (tier?: string) => {
    switch (tier) {
      case 'GREEN': return '#10b981';
      case 'AMBER': return '#f59e0b';
      case 'ORANGE': return '#f97316';
      case 'RED': return '#ef4444';
      default: return '#64748b';
    }
  };

  const journeySteps = [
    { title: 'Call Ingress', desc: 'Attack / call reaches system' },
    { title: 'Multi-Family Alert', desc: 'Audio + Context risk evaluated' },
    { title: 'Customer Action', desc: 'Out-of-band mobile verification' },
    { title: 'Analyst Review', desc: 'Dual control & hold triage' },
    { title: 'Outcome', desc: 'Fraud contained or customer cleared' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Fallback Mode Banner */}
      {isFallbackMode && (
        <div style={{
          padding: '12px 18px',
          borderRadius: '8px',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid #f59e0b',
          color: '#fbbf24',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontWeight: '600',
          fontSize: '0.88rem'
        }}>
          <AlertTriangle size={18} />
          <span>FALLBACK MODE: models/head.joblib not found; using heuristic spectral engine. Results not calibrated for formal benchmarks.</span>
        </div>
      )}

      {/* Frontline Agent Neutral Guidance Banner */}
      {verdict && (
        <div style={{
          padding: '14px 20px',
          borderRadius: '10px',
          background: 'rgba(59, 130, 246, 0.08)',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Info size={18} style={{ color: '#38bdf8' }} />
            <div>
              <div style={{ fontSize: '0.75rem', color: '#93c5fd', textTransform: 'uppercase', fontWeight: '700' }}>
                Operational Guidance (Neutral • Non-Accusatory)
              </div>
              <div style={{ fontSize: '0.92rem', fontWeight: '600', color: 'var(--text-main)', marginTop: '2px' }}>
                {verdict.agent_guidance}
              </div>
            </div>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
            {verdict.recommended_action}
          </span>
        </div>
      )}

      {/* 3-Column Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr 1fr', gap: '20px' }}>
        
        {/* COLUMN 1: Large Status Card & Multi-Family Signals */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', position: 'relative' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '14px' }}>
              System Verdict
            </div>

            {/* Big Circular Tier Ring */}
            <div style={{
              width: '130px',
              height: '130px',
              borderRadius: '50%',
              margin: '0 auto 16px auto',
              border: `6px solid ${getTierColor(verdict?.tier)}`,
              boxShadow: `0 0 28px ${getTierColor(verdict?.tier)}40`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease'
            }}>
              <span style={{ fontSize: '1.25rem', fontWeight: '900', color: getTierColor(verdict?.tier) }}>
                {verdict ? verdict.tier : 'READY'}
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'monospace', marginTop: '2px' }}>
                R: {verdict ? verdict.risk_score.toFixed(2) : '0.00'}
              </span>
            </div>

            {/* Plain English Sentence */}
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: getTierColor(verdict?.tier) }}>
              "{getPlainSentence(verdict?.tier)}"
            </h3>

            {/* 3 Family Bars */}
            <div style={{ marginTop: '22px', display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Audio Evidence (45%)</span>
                  <span style={{ fontFamily: 'monospace', fontWeight: '700' }}>
                    {verdict ? verdict.llr_audio.toFixed(2) : '0.00'}
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(Math.max((((verdict?.llr_audio || 0) + 4) / 10) * 100, 5), 100)}%`,
                    height: '100%',
                    background: (verdict?.llr_audio || 0) > 1.0 ? '#ef4444' : '#38bdf8'
                  }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Interaction Cadence (25%)</span>
                  <span style={{ fontFamily: 'monospace', fontWeight: '700' }}>
                    {verdict ? verdict.llr_interaction.toFixed(2) : '0.00'}
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(Math.max((((verdict?.llr_interaction || 0) + 4) / 10) * 100, 5), 100)}%`,
                    height: '100%',
                    background: (verdict?.llr_interaction || 0) > 1.0 ? '#f59e0b' : '#38bdf8'
                  }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Transaction Context (30%)</span>
                  <span style={{ fontFamily: 'monospace', fontWeight: '700' }}>
                    {verdict ? verdict.llr_transaction.toFixed(2) : '0.00'}
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(Math.max((((verdict?.llr_transaction || 0) + 4) / 10) * 100, 5), 100)}%`,
                    height: '100%',
                    background: (verdict?.llr_transaction || 0) > 1.0 ? '#f97316' : '#38bdf8'
                  }} />
                </div>
              </div>
            </div>

            {/* Reason Chips */}
            <div style={{ marginTop: '18px', display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center' }}>
              {verdict?.reason_codes?.map((rc, i) => (
                <span
                  key={i}
                  style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)'
                  }}
                  title={rc.plain_language_explanation}
                >
                  {rc.plain_language_explanation.slice(0, 32)}...
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* COLUMN 2: Waveform Canvas, Big Record Button & Rolling Score Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)' }}>
                Live Acoustic Analysis Window
              </span>
              <span style={{ fontSize: '0.75rem', color: isRecording ? '#ef4444' : 'var(--text-dim)', fontWeight: '600' }}>
                {isRecording ? 'RECORDING LIVE...' : 'STREAM IDLE'}
              </span>
            </div>

            {/* Live Waveform Canvas */}
            <div style={{ background: 'rgba(0,0,0,0.35)', borderRadius: '10px', overflow: 'hidden', border: '1px solid var(--border-subtle)', height: '110px' }}>
              <canvas ref={canvasRef} width={400} height={110} style={{ width: '100%', height: '100%', display: 'block' }} />
            </div>

            {/* Big Record Button & Dropzone */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={isRecording ? stopRecording : startRecording}
                style={{
                  flex: 1.2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  padding: '16px',
                  borderRadius: '10px',
                  fontWeight: '700',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  border: isRecording ? '2px solid #ef4444' : '1px solid #3b82f6',
                  background: isRecording ? 'rgba(239, 68, 68, 0.25)' : 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                  color: '#fff',
                  boxShadow: isRecording ? '0 0 20px rgba(239, 68, 68, 0.4)' : '0 4px 14px rgba(37, 99, 235, 0.4)',
                  transition: 'all 0.2s'
                }}
              >
                {isRecording ? <MicOff size={22} /> : <Mic size={22} />}
                {isRecording ? 'Stop Recording' : 'Record Mic'}
              </button>

              <label style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '16px',
                borderRadius: '10px',
                border: '1px dashed rgba(255,255,255,0.2)',
                background: 'rgba(255,255,255,0.03)',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                fontWeight: '600',
                cursor: 'pointer',
                textAlign: 'center'
              }}>
                <Upload size={18} />
                Upload WAV
                <input type="file" accept="audio/*" onChange={handleFileUpload} style={{ display: 'none' }} />
              </label>
            </div>

            {audioBlobUrl && (
              <audio controls src={audioBlobUrl} style={{ width: '100%', height: '36px', marginTop: '6px' }} />
            )}

            {/* Rolling Score Timeline (Past 8 windows) */}
            <div style={{ marginTop: '10px', borderTop: '1px solid var(--border-subtle)', paddingTop: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                <span>Rolling Score Timeline (2s Windows)</span>
                <span style={{ fontFamily: 'monospace' }}>p95: {verdict ? `${verdict.processing_latency_ms}ms` : '29.3ms'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '48px', background: 'rgba(0,0,0,0.2)', padding: '6px', borderRadius: '6px' }}>
                {historyScores.map((s, idx) => {
                  const h = Math.min(Math.max((s / 6.0) * 100, 10), 100);
                  const color = s > 3.0 ? '#ef4444' : s > 1.25 ? '#f59e0b' : '#10b981';
                  return (
                    <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                      <div style={{ width: '100%', height: `${h}%`, background: color, borderRadius: '2px' }} title={`Score: ${s.toFixed(2)}`} />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* COLUMN 3: Scenario Stepper, Actions & Journey Highlighter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Preset Buttons */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h4 style={{ fontSize: '0.92rem', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={16} style={{ color: '#f59e0b' }} /> 4 Stage-2 Threat Presets
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => applyPreset('scenario_a')}
                style={{
                  padding: '9px 12px',
                  borderRadius: '7px',
                  border: activeScenario === 'scenario_a' ? '1px solid #10b981' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_a' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255,255,255,0.02)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  fontSize: '0.82rem'
                }}
              >
                <span>1. Legit Balance Check</span>
                <span className="tier-badge tier-badge-green" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>GREEN</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_b')}
                style={{
                  padding: '9px 12px',
                  borderRadius: '7px',
                  border: activeScenario === 'scenario_b' ? '1px solid #ef4444' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_b' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(255,255,255,0.02)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  fontSize: '0.82rem'
                }}
              >
                <span>2. Cloned Voice Add-Payee</span>
                <span className="tier-badge tier-badge-red" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>RED</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_c')}
                style={{
                  padding: '9px 12px',
                  borderRadius: '7px',
                  border: activeScenario === 'scenario_c' ? '1px solid #f59e0b' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_c' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(255,255,255,0.02)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  fontSize: '0.82rem'
                }}
              >
                <span>3. Accented on Noisy Line (False-Positive)</span>
                <span className="tier-badge tier-badge-amber" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>AMBER</span>
              </button>

              <button
                onClick={() => applyPreset('scenario_d')}
                style={{
                  padding: '9px 12px',
                  borderRadius: '7px',
                  border: activeScenario === 'scenario_d' ? '1px solid #f97316' : '1px solid var(--border-subtle)',
                  background: activeScenario === 'scenario_d' ? 'rgba(249, 115, 22, 0.12)' : 'rgba(255,255,255,0.02)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  fontSize: '0.82rem'
                }}
              >
                <span>4. UPI Collect Scam (S1)</span>
                <span className="tier-badge tier-badge-orange" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>ORANGE</span>
              </button>
            </div>
          </div>

          {/* Action Selector */}
          <div className="glass-panel" style={{ padding: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Action</label>
                <select
                  value={selectedAction}
                  onChange={(e) => setSelectedAction(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.82rem'
                  }}
                >
                  <option value="balance_inquiry">Balance Inquiry</option>
                  <option value="add_payee">Add Payee</option>
                  <option value="raise_limit">Raise Limit</option>
                  <option value="upi_collect_request">UPI Collect</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Amount (₹)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.82rem'
                  }}
                />
              </div>
            </div>
          </div>

          {/* End-to-End Journey Stepper */}
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
              End-to-End Incident Lifecycle
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {journeySteps.map((step, idx) => {
                const isActive = idx === currentStepIndex;
                const isPassed = idx < currentStepIndex;
                return (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    border: isActive ? '1px solid #3b82f6' : '1px solid transparent'
                  }}>
                    <div style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: isPassed ? '#10b981' : isActive ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                      color: '#fff',
                      fontSize: '0.7rem',
                      fontWeight: '700',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      {idx + 1}
                    </div>
                    <div>
                      <div style={{ fontSize: '0.82rem', fontWeight: isActive ? '700' : '500', color: isActive ? '#fff' : 'var(--text-muted)' }}>
                        {step.title}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{step.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick Link to Customer Phone / Analyst */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '14px' }}>
              <button
                onClick={handleTriggerStepUp}
                style={{
                  flex: 1,
                  padding: '9px 12px',
                  borderRadius: '6px',
                  background: '#2563eb',
                  color: '#fff',
                  border: 'none',
                  fontSize: '0.78rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}
              >
                <Smartphone size={14} /> Mobile App Push
              </button>
              <button
                onClick={onNavigateToAnalyst}
                style={{
                  flex: 1,
                  padding: '9px 12px',
                  borderRadius: '6px',
                  background: 'rgba(255,255,255,0.06)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.78rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}
              >
                Analyst Queue <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
