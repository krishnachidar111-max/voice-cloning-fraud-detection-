import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Flame,
  CheckCircle2,
  Lock,
  Unlock,
  Volume2,
  AlertTriangle,
  UserCheck,
  FileText,
  Clock,
  ArrowRight
} from 'lucide-react';
import { CaseSummary, fetchCases, takeCaseAction } from '../services/api';

export const AnalystConsole: React.FC = () => {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseSummary | null>(null);
  const [analystId, setAnalystId] = useState<string>('ANALYST_ROHIT_01');
  const [notes, setNotes] = useState<string>('Customer identity confirmed via out-of-band channel.');
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadCases = async () => {
    try {
      const data = await fetchCases();
      setCases(data);
      if (data.length > 0 && !selectedCase) {
        setSelectedCase(data[0]);
      }
    } catch (e) {
      console.error('Failed to load cases:', e);
    }
  };

  useEffect(() => {
    loadCases();
    const interval = setInterval(loadCases, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (action: 'HOLD' | 'RELEASE' | 'CONFIRM_FRAUD') => {
    if (!selectedCase) return;
    try {
      const res = await takeCaseAction(selectedCase.case_id, analystId, action, notes);
      setActionMessage(res.message || 'Action executed successfully.');
      loadCases();
    } catch (e: any) {
      setActionMessage('Error: ' + e.message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', borderLeft: '4px solid #ef4444' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Tier-2 Fraud Analyst Investigation Console</h2>
            <span className="mock-pill">Human-in-the-Loop</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            Dual-control approval required for releases ≥ ₹50,000. All decisions cryptographically recorded to the immutable audit ledger.
          </p>
        </div>

        {/* Analyst Identity Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Logged in as:</span>
          <select
            value={analystId}
            onChange={(e) => setAnalystId(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              fontWeight: '600'
            }}
          >
            <option value="ANALYST_ROHIT_01">Analyst Rohit (Tier 2)</option>
            <option value="SUPERVISOR_PRIYA_02">Supervisor Priya (Dual Control)</option>
            <option value="LEAD_ARJUN_03">Fraud Lead Arjun (CISO Team)</option>
          </select>
        </div>
      </div>

      {/* Main Investigation Split View */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '24px' }}>
        {/* Left: Active Alerts & Case Queue */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '600' }}>Active Security Alerts ({cases.length})</h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Auto-refreshed</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', maxHeight: '560px' }}>
            {cases.map((c) => (
              <div
                key={c.case_id}
                onClick={() => { setSelectedCase(c); setActionMessage(null); }}
                style={{
                  padding: '14px',
                  borderRadius: '10px',
                  background: selectedCase?.case_id === c.case_id ? 'rgba(59, 130, 246, 0.12)' : 'rgba(0,0,0,0.2)',
                  border: selectedCase?.case_id === c.case_id ? '1px solid #3b82f6' : '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: '700', fontFamily: 'monospace', color: '#93c5fd' }}>
                    {c.case_id}
                  </span>
                  <span
                    className={`tier-badge ${
                      c.tier === 'RED' ? 'tier-badge-red' : c.tier === 'ORANGE' ? 'tier-badge-orange' : 'tier-badge-amber'
                    }`}
                    style={{ fontSize: '0.68rem', padding: '2px 8px' }}
                  >
                    {c.tier}
                  </span>
                </div>

                <div style={{ fontSize: '0.88rem', fontWeight: '600', marginBottom: '4px' }}>{c.action_attempted}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>Amount: ₹{c.amount.toLocaleString()}</span>
                  <span style={{ color: c.status === 'CONFIRMED_FRAUD' ? '#f87171' : c.status === 'RELEASED' ? '#34d399' : '#fbbf24', fontWeight: '600' }}>
                    {c.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Detailed Case Investigation Dossier */}
        {selectedCase ? (
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CASE DOSSIER</span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginTop: '2px' }}>{selectedCase.case_id}</h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Customer: {selectedCase.customer_id_masked} | Session: {selectedCase.session_id}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Fused Risk Score</span>
                <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#f87171', fontFamily: 'monospace' }}>
                  {selectedCase.risk_score.toFixed(2)}
                </div>
              </div>
            </div>

            {/* Dual Control Status Banner */}
            {selectedCase.has_dual_control_requirement && (
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: selectedCase.status === 'RELEASED' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  border: selectedCase.status === 'RELEASED' ? '1px solid #10b981' : '1px solid #f59e0b',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}
              >
                <Lock size={18} style={{ color: selectedCase.status === 'RELEASED' ? '#10b981' : '#f59e0b' }} />
                <div>
                  <strong>Dual-Analyst Dual Control Required (Transaction ≥ ₹50,000)</strong>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    1st Analyst: {selectedCase.first_analyst_id || 'Pending'} | 2nd Supervisor: {selectedCase.second_analyst_id || 'Pending'}
                  </div>
                </div>
              </div>
            )}

            {/* Plain-Language Reason Codes Timeline */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '10px' }}>Evidence Reason Codes</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {selectedCase.reason_codes.map((rc, idx) => (
                  <div key={idx} style={{ padding: '10px 14px', borderRadius: '8px', background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: '700', color: '#38bdf8', fontFamily: 'monospace' }}>{rc.code}</span>
                      <span style={{ fontSize: '0.72rem', color: '#f87171' }}>{rc.family}</span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>{rc.plain_language_explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Audio Clip Verification Notice */}
            <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Volume2 size={20} style={{ color: '#38bdf8' }} />
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: '600' }}>30s Encrypted Evidence Clip (Case-ID Gated)</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  FR-24 Audit Rule: Viewing this clip creates an immutable log entry tied to {analystId}.
                </div>
              </div>
            </div>

            {/* Analyst Action Controls */}
            <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Investigation Findings & Notes</label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem'
                  }}
                />
              </div>

              {actionMessage && (
                <div style={{ padding: '8px 12px', borderRadius: '6px', background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', fontSize: '0.82rem' }}>
                  {actionMessage}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.2fr', gap: '10px' }}>
                <button
                  onClick={() => handleAction('HOLD')}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: 'rgba(245, 158, 11, 0.15)',
                    border: '1px solid rgba(245, 158, 11, 0.4)',
                    color: '#fbbf24',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Maintain Hold
                </button>

                <button
                  onClick={() => handleAction('RELEASE')}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: 'rgba(16, 185, 129, 0.15)',
                    border: '1px solid rgba(16, 185, 129, 0.4)',
                    color: '#34d399',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Release Hold
                </button>

                <button
                  onClick={() => handleAction('CONFIRM_FRAUD')}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    background: '#dc2626',
                    color: '#fff',
                    border: 'none',
                    fontWeight: '700',
                    cursor: 'pointer'
                  }}
                >
                  Confirm Fraud (Freeze)
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Select a case from the queue to inspect forensic evidence.
          </div>
        )}
      </div>
    </div>
  );
};
