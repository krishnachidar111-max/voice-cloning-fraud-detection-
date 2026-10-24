import React from 'react';
import { Phone, Clock, User, ShieldCheck, AlertCircle, PhoneForwarded } from 'lucide-react';
import { StreamingVerdict } from '../services/api';

interface AgentWidgetProps {
  verdict: StreamingVerdict | null;
}

export const AgentWidget: React.FC<AgentWidgetProps> = ({ verdict }) => {
  const tier = verdict?.tier || 'GREEN';

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Frontline Call Center Agent Interface Header */}
      <div className="glass-panel" style={{ padding: '20px 24px', borderLeft: '4px solid #38bdf8' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Frontline Servicing Terminal</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
              Standard CRM / Contact Center Agent View (FR-18 & Hard Rule 3 Conformance)
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(56, 189, 248, 0.1)', padding: '6px 12px', borderRadius: '6px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
            <Phone size={16} style={{ color: '#38bdf8' }} />
            <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#38bdf8' }}>Call In Progress (02:45)</span>
          </div>
        </div>

        {/* Responsible AI Compliance Notice */}
        <div style={{ marginTop: '12px', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
          🔒 <strong>Agent Non-Accusatory Guardrail:</strong> Technical deepfake scores and probabilities are hidden by design to prevent cognitive bias or premature customer accusations.
        </div>
      </div>

      {/* Customer Header Details */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Customer Name</span>
            <div style={{ fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
              <User size={16} style={{ color: '#94a3b8' }} /> Rajesh Kumar Sharma
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Account Number</span>
            <div style={{ fontSize: '1rem', fontWeight: '600', fontFamily: 'monospace', marginTop: '2px' }}>
              HDFC-****-****-4912
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Calling Line Identity (CLI)</span>
            <div style={{ fontSize: '1rem', fontWeight: '600', fontFamily: 'monospace', marginTop: '2px' }}>
              +91 98*** **310 (Delhi Circle)
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Neutral Agent Prompt Card */}
      <div className="glass-panel" style={{ padding: '28px', border: tier === 'RED' ? '1px solid rgba(239, 68, 68, 0.4)' : tier === 'ORANGE' ? '1px solid rgba(249, 115, 22, 0.4)' : '1px solid var(--border-subtle)' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          System Operational Guidance
        </span>

        <div style={{ marginTop: '14px', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: tier === 'RED' ? '#f87171' : tier === 'ORANGE' ? '#fb923c' : tier === 'AMBER' ? '#fbbf24' : '#34d399' }}>
            {verdict ? verdict.agent_guidance : 'Standard customer servicing. All security verifications clear.'}
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '8px', lineHeight: '1.5' }}>
            {verdict ? verdict.recommended_action : 'Proceed with requested workflow normally.'}
          </p>
        </div>

        {/* Scripted Agent Dialogue Prompts */}
        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '18px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.78rem', color: '#38bdf8', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase' }}>
            Recommended Script to Read to Caller:
          </div>

          {tier === 'GREEN' && (
            <p style={{ fontStyle: 'italic', color: 'var(--text-main)', fontSize: '0.95rem' }}>
              "Thank you for confirming your account details, Mr. Sharma. I have retrieved your current balance and recent statement. How else may I assist you today?"
            </p>
          )}

          {tier === 'AMBER' && (
            <p style={{ fontStyle: 'italic', color: 'var(--text-main)', fontSize: '0.95rem' }}>
              "To ensure your account safety for this transaction, I have sent a quick approval notification to your registered mobile banking app. Could you please unlock your phone and tap 'Confirm'?"
            </p>
          )}

          {tier === 'ORANGE' && (
            <p style={{ fontStyle: 'italic', color: 'var(--text-main)', fontSize: '0.95rem' }}>
              "For this sensitive account modification, our security policy requires independent mobile confirmation. A 2-digit number matching challenge has been dispatched to your primary device. Please enter the number displayed on your banking app screen."
            </p>
          )}

          {tier === 'RED' && (
            <p style={{ fontStyle: 'italic', color: 'var(--text-main)', fontSize: '0.95rem' }}>
              "Thank you for your patience, Mr. Sharma. For security reasons related to high-value servicing, I am initiating a warm transfer to our Senior Account Security Team to complete this request safely. Please remain on the line."
            </p>
          )}
        </div>

        {/* Transfer Button for RED tier */}
        {tier === 'RED' && (
          <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                borderRadius: '8px',
                background: '#dc2626',
                color: '#fff',
                border: 'none',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              <PhoneForwarded size={18} /> Warm Transfer to Senior Fraud Specialist
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
