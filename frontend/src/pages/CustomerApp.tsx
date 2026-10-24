import React, { useState, useEffect } from 'react';
import {
  Smartphone,
  ShieldAlert,
  ShieldCheck,
  Check,
  X,
  AlertOctagon,
  CreditCard,
  Send,
  HelpCircle,
  RefreshCw,
  Lock
} from 'lucide-react';
import {
  getActiveChallenge,
  respondChallenge,
  submitAppeal,
  interceptUPI,
  VerificationChallenge
} from '../services/api';

interface CustomerAppProps {
  sessionId: string;
  onActionComplete?: () => void;
}

export const CustomerApp: React.FC<CustomerAppProps> = ({ sessionId, onActionComplete }) => {
  const [challenge, setChallenge] = useState<VerificationChallenge | null>(null);
  const [enteredCode, setEnteredCode] = useState<string>('');
  const [responseStatus, setResponseStatus] = useState<string | null>(null);
  const [appealResult, setAppealResult] = useState<any | null>(null);
  const [isAppealing, setIsAppealing] = useState(false);
  const [upiInterceptData, setUpiInterceptData] = useState<any | null>(null);

  // Poll active challenge for session
  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const c = await getActiveChallenge(sessionId);
        if (c) setChallenge(c);
      } catch (e) {
        console.error('Failed to poll challenge:', e);
      }
    };
    fetchChallenge();
    const interval = setInterval(fetchChallenge, 2000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const handleDecision = async (decision: 'APPROVE' | 'DENY') => {
    if (!challenge) return;
    const codeNum = enteredCode ? parseInt(enteredCode, 10) : undefined;
    const res = await respondChallenge(challenge.challenge_id, decision, codeNum);
    setResponseStatus(decision === 'APPROVE' ? 'APPROVED' : 'DENIED');
    if (onActionComplete) onActionComplete();
  };

  const handleTestUPICollect = async () => {
    // Scenario S1 UPI Collect scam interception
    const res = await interceptUPI(sessionId, 'shady_relative@paytm', 45000, true, 'ORANGE');
    setUpiInterceptData(res);
  };

  const handleCustomerAppeal = async () => {
    setIsAppealing(true);
    const res = await submitAppeal(
      'CASE-IN-8041',
      sessionId,
      'CUST-4912',
      'I was calling while traveling in a noisy metro station. This was my genuine request.'
    );
    setAppealResult(res);
    setIsAppealing(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '10px' }}>
      {/* Smartphone Device Frame Mockup */}
      <div
        style={{
          width: '380px',
          height: '740px',
          background: '#090d16',
          borderRadius: '44px',
          border: '10px solid #1e293b',
          boxShadow: '0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(59, 130, 246, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          position: 'relative'
        }}
      >
        {/* Smartphone Speaker Notch */}
        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: '10px' }}>
          <div style={{ width: '90px', height: '18px', background: '#1e293b', borderRadius: '10px' }} />
        </div>

        {/* Mobile App Header */}
        <div style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Lock size={16} color="#fff" />
            </div>
            <span style={{ fontWeight: '700', fontSize: '0.95rem' }}>SecureBank Mobile</span>
          </div>
          <span style={{ fontSize: '0.72rem', color: '#10b981', fontWeight: '600' }}>Device Bound</span>
        </div>

        {/* Smartphone Screen Body */}
        <div style={{ flex: 1, padding: '18px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Active Challenge Box */}
          {challenge && challenge.status === 'PENDING' && !responseStatus ? (
            <div
              style={{
                background: 'rgba(249, 115, 22, 0.08)',
                border: '1px solid rgba(249, 115, 22, 0.3)',
                borderRadius: '16px',
                padding: '18px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                animation: 'pulse-subtle 2s infinite ease-in-out'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldAlert size={22} style={{ color: '#f97316' }} />
                <span style={{ fontWeight: '700', fontSize: '0.92rem', color: '#f97316' }}>Security Verification</span>
              </div>

              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                A servicing request was initiated via Phone Banking. Did you authorize this action?
              </p>

              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: '8px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-dim)' }}>Action:</span>
                  <span style={{ fontWeight: '600' }}>{challenge.action_type.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-dim)' }}>Payee / Beneficiary:</span>
                  <span style={{ fontWeight: '600' }}>{challenge.payee}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-dim)' }}>Amount:</span>
                  <span style={{ fontWeight: '700', color: '#38bdf8' }}>₹{challenge.amount.toLocaleString()}</span>
                </div>
              </div>

              {/* Number Matching Challenge Code */}
              <div style={{ textAlign: 'center', padding: '10px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', border: '1px dashed rgba(59, 130, 246, 0.4)' }}>
                <span style={{ fontSize: '0.75rem', color: '#93c5fd', display: 'block', marginBottom: '4px' }}>
                  Anti-Screen Share Number Match:
                </span>
                <span style={{ fontSize: '1.6rem', fontWeight: '800', letterSpacing: '4px', color: '#60a5fa', fontFamily: 'monospace' }}>
                  {challenge.number_matching_code}
                </span>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>Enter Number to Confirm:</label>
                <input
                  type="number"
                  placeholder="e.g. 47"
                  value={enteredCode}
                  onChange={(e) => setEnteredCode(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    background: 'rgba(0,0,0,0.4)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '1rem',
                    textAlign: 'center',
                    fontWeight: '700'
                  }}
                />
              </div>

              {/* Action Buttons: Approve vs Deny */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '6px' }}>
                <button
                  onClick={() => handleDecision('DENY')}
                  style={{
                    padding: '12px',
                    borderRadius: '10px',
                    background: '#dc2626',
                    color: '#fff',
                    border: 'none',
                    fontWeight: '700',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  <X size={18} /> DENY (FRAUD)
                </button>

                <button
                  onClick={() => handleDecision('APPROVE')}
                  style={{
                    padding: '12px',
                    borderRadius: '10px',
                    background: '#16a34a',
                    color: '#fff',
                    border: 'none',
                    fontWeight: '700',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  <Check size={18} /> APPROVE
                </button>
              </div>
            </div>
          ) : (
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '14px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
              <ShieldCheck size={32} style={{ color: '#10b981', margin: '0 auto 8px' }} />
              <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>Account Secure & Protected</div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                Biometric passkey bound to this phone hardware.
              </p>
            </div>
          )}

          {/* Outcome Result Message */}
          {responseStatus && (
            <div
              style={{
                padding: '14px',
                borderRadius: '12px',
                background: responseStatus === 'APPROVED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                border: responseStatus === 'APPROVED' ? '1px solid #10b981' : '1px solid #ef4444',
                textAlign: 'center'
              }}
            >
              <div style={{ fontWeight: '700', fontSize: '0.95rem', color: responseStatus === 'APPROVED' ? '#34d399' : '#f87171' }}>
                {responseStatus === 'APPROVED' ? 'Verification Confirmed' : 'Action Denied: Fraud Blocked'}
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                {responseStatus === 'APPROVED'
                  ? 'Your servicing request has been authorized.'
                  : 'Account frozen. Contact center alert dispatched to Fraud Team.'}
              </p>
            </div>
          )}

          {/* Threat Scenario S1: Simulated UPI Intercept Test */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase' }}>
              Scenario S1: Customer UPI Collect Test
            </span>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', margin: '4px 0 10px' }}>
              Simulates receiving an urgent UPI collect request from a cloned relative during a phone call.
            </p>
            <button
              onClick={handleTestUPICollect}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                background: 'rgba(249, 115, 22, 0.15)',
                border: '1px solid rgba(249, 115, 22, 0.4)',
                color: '#fb923c',
                fontWeight: '600',
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              Simulate Incoming UPI Collect (₹45,000)
            </button>
          </div>

          {/* UPI Interception Result */}
          {upiInterceptData && (
            <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '12px', padding: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f87171', fontWeight: '700', fontSize: '0.85rem' }}>
                <AlertOctagon size={18} /> {upiInterceptData.warning_title}
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px', lineHeight: '1.4' }}>
                {upiInterceptData.warning_message}
              </p>
            </div>
          )}

          {/* False Positive Clearance Appeal Button (FR-20) */}
          <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
            <button
              onClick={handleCustomerAppeal}
              disabled={isAppealing}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.1)',
                color: 'var(--text-muted)',
                fontSize: '0.78rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <HelpCircle size={14} /> Falsely Flagged? Fast-Path Appeal (FR-20)
            </button>
          </div>

          {appealResult && (
            <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid #10b981', borderRadius: '10px', padding: '12px', fontSize: '0.78rem' }}>
              <div style={{ fontWeight: '700', color: '#34d399', marginBottom: '4px' }}>
                Status: {appealResult.status} (Resolved in {appealResult.resolution_time_seconds}s)
              </div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '6px' }}>{appealResult.why_it_fired}</p>
              <div style={{ color: '#6ee7b7', fontSize: '0.72rem' }}>{appealResult.fairness_reassurance}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
