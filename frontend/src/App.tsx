import React, { useState } from 'react';
import {
  Shield,
  Phone,
  Smartphone,
  UserCheck,
  BarChart3,
  Sliders,
  CheckCircle2,
  Lock
} from 'lucide-react';
import { DemoControl } from './pages/DemoControl';
import { AgentWidget } from './pages/AgentWidget';
import { CustomerApp } from './pages/CustomerApp';
import { AnalystConsole } from './pages/AnalystConsole';
import { Dashboard } from './pages/Dashboard';
import { StreamingVerdict } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'demo' | 'agent' | 'customer' | 'analyst' | 'dashboard'>('demo');
  const [verdict, setVerdict] = useState<StreamingVerdict | null>(null);
  const [sessionId, setSessionId] = useState<string>('SESS-DELHI-8041');

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Application Navbar */}
      <header
        style={{
          borderBottom: '1px solid var(--border-subtle)',
          background: 'rgba(10, 14, 26, 0.85)',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          padding: '12px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
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
              <h1 style={{ fontSize: '1.2rem', fontWeight: '800', letterSpacing: '-0.02em' }}>EchoGuard AI</h1>
              <span style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', borderRadius: '4px', fontWeight: '700' }}>v2.0</span>
              <span className="mock-pill">MOCK CORE BANKING</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Real-Time Voice Cloning Defense in Banking & Payment Workflows
            </div>
          </div>
        </div>

        {/* Global Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '6px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setActiveTab('demo')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'demo' ? '#2563eb' : 'transparent',
              color: activeTab === 'demo' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            <Sliders size={15} /> Demo Controller
          </button>

          <button
            onClick={() => setActiveTab('agent')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'agent' ? '#2563eb' : 'transparent',
              color: activeTab === 'agent' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            <Phone size={15} /> Agent Widget
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
              cursor: 'pointer'
            }}
          >
            <Smartphone size={15} /> Customer App (OOB)
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
              cursor: 'pointer'
            }}
          >
            <UserCheck size={15} /> Analyst Console
          </button>

          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'dashboard' ? '#2563eb' : 'transparent',
              color: activeTab === 'dashboard' ? '#fff' : 'var(--text-muted)',
              fontWeight: '600',
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            <BarChart3 size={15} /> Dashboard & Audit
          </button>
        </nav>
      </header>

      {/* Main Content View Container */}
      <main style={{ flex: 1, padding: '28px 32px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'demo' && (
          <DemoControl
            verdict={verdict}
            setVerdict={setVerdict}
            onNavigateToCustomer={() => setActiveTab('customer')}
            onNavigateToAnalyst={() => setActiveTab('analyst')}
          />
        )}
        {activeTab === 'agent' && <AgentWidget verdict={verdict} />}
        {activeTab === 'customer' && <CustomerApp sessionId={verdict?.session_id || sessionId} />}
        {activeTab === 'analyst' && <AnalystConsole />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
        <div>EchoGuard AI • Team ErrorX • Amazon AI Cyber Security Hackathon (Track 1)</div>
        <div>Zero-Disk Privacy by Design • Designed for DPDP Act 2023 & RBI Cyber Security Framework</div>
      </footer>
    </div>
  );
};
