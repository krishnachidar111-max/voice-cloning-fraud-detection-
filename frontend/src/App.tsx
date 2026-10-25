import React, { useState, useEffect } from 'react';
import {
  Shield,
  PhoneCall,
  Smartphone,
  UserCheck,
  ShieldCheck,
  Activity,
  Zap,
  Lock
} from 'lucide-react';
import { DemoControl } from './pages/DemoControl';
import { CustomerApp } from './pages/CustomerApp';
import { AnalystConsole } from './pages/AnalystConsole';
import { Dashboard } from './pages/Dashboard';
import { StreamingVerdict, fetchHealthStatus } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'live' | 'customer' | 'analyst' | 'trust'>('live');
  const [verdict, setVerdict] = useState<StreamingVerdict | null>(null);
  const [sessionId, setSessionId] = useState<string>('SESS-DELHI-8041');
  const [healthStatus, setHealthStatus] = useState<any | null>(null);

  useEffect(() => {
    fetchHealthStatus().then(setHealthStatus).catch(err => {
      console.warn('Backend offline or health unreachable:', err);
    });
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* Top Application Navbar */}
      <header
        style={{
          borderBottom: '1px solid var(--border-subtle)',
          background: 'rgba(10, 14, 26, 0.90)',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          padding: '12px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #3b82f6, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(59, 130, 246, 0.4)'
            }}
          >
            <Shield size={22} color="#fff" />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.2rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Phantom Trace</h1>
              <span style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', borderRadius: '4px', fontWeight: '700' }}>v2.0</span>
              <span className="mock-pill">MOCK CORE BANKING</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Real-Time Voice Cloning Defense in Banking & Payment Workflows
            </div>
          </div>
        </div>

        {/* Global Navigation Tabs (4 Tabs Only) */}
        <nav style={{ display: 'flex', gap: '6px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setActiveTab('live')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'live' ? '#2563eb' : 'transparent',
              color: activeTab === 'live' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <PhoneCall size={15} /> Live Call
          </button>

          <button
            onClick={() => setActiveTab('customer')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'customer' ? '#2563eb' : 'transparent',
              color: activeTab === 'customer' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <Smartphone size={15} /> Customer Phone
          </button>

          <button
            onClick={() => setActiveTab('analyst')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'analyst' ? '#2563eb' : 'transparent',
              color: activeTab === 'analyst' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <UserCheck size={15} /> Analyst
          </button>

          <button
            onClick={() => setActiveTab('trust')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'trust' ? '#2563eb' : 'transparent',
              color: activeTab === 'trust' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <ShieldCheck size={15} /> Trust
          </button>
        </nav>
      </header>

      {/* Main Content View Container */}
      <main style={{ flex: 1, padding: '24px 28px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'live' && (
          <DemoControl
            verdict={verdict}
            setVerdict={setVerdict}
            onNavigateToCustomer={() => setActiveTab('customer')}
            onNavigateToAnalyst={() => setActiveTab('analyst')}
            isFallbackMode={healthStatus?.fallback_mode}
          />
        )}
        {activeTab === 'customer' && (
          <CustomerApp sessionId={verdict?.session_id || sessionId} />
        )}
        {activeTab === 'analyst' && (
          <AnalystConsole />
        )}
        {activeTab === 'trust' && (
          <Dashboard />
        )}
      </main>

      {/* Persistent Footer Strip */}
      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(10, 14, 26, 0.95)',
          padding: '12px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '0.78rem',
          color: 'var(--text-dim)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontWeight: '700' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
            Audio saved: 0 bytes (RAM-only ring buffer)
          </span>
          <span>•</span>
          <span style={{ color: '#38bdf8' }}>Latency p95: 29.3 ms</span>
          <span>•</span>
          <span style={{ color: '#a78bfa' }}>Model: v2.0 (Learned Engine)</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span className="mock-pill">MOCK TELEPHONY (SIPREC)</span>
          <span className="mock-pill">MOCK CORE BANKING</span>
          <span className="mock-pill">MOCK UPI SWITCH</span>
          <span className="mock-pill">MOCK SIM-SWAP FEED</span>
        </div>
      </footer>
    </div>
  );
};
