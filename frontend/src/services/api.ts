/**
 * Phantom Trace - Frontend API Service & WebSocket Client
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';
export const WS_BASE_URL = (import.meta.env.VITE_WS_BASE_URL as string) || (API_BASE_URL.startsWith('http') ? API_BASE_URL.replace(/^http/, 'ws') : 'ws://127.0.0.1:8000');

export interface ReasonCode {
  code: string;
  family: 'AUDIO' | 'INTERACTION' | 'TRANSACTION' | 'SYSTEM';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  plain_language_explanation: string;
}

export interface StreamingVerdict {
  session_id: string;
  timestamp: string;
  window_index: number;
  tier: 'GREEN' | 'AMBER' | 'ORANGE' | 'RED';
  risk_score: number;
  accumulated_evidence: number;
  llr_audio: number;
  llr_interaction: number;
  llr_transaction: number;
  reason_codes: ReasonCode[];
  safety_rule_applied?: string;
  audio_persisted_bytes: number;
  processing_latency_ms: number;
  agent_guidance: string;
  recommended_action: string;
}

export interface VerificationChallenge {
  challenge_id: string;
  session_id: string;
  token: string;
  action_type: string;
  amount: number;
  payee: string;
  number_matching_code: number;
  status: 'PENDING' | 'APPROVED' | 'DENIED' | 'EXPIRED';
  expires_at: string;
  created_at: string;
}

export interface CaseSummary {
  case_id: string;
  session_id: string;
  customer_id_masked: string;
  tier: 'AMBER' | 'ORANGE' | 'RED';
  risk_score: number;
  action_attempted: string;
  amount: number;
  status: 'ACTIVE_HOLD' | 'RELEASED' | 'CONFIRMED_FRAUD' | 'AUTO_CLEARED' | 'APPEALED';
  created_at: string;
  updated_at: string;
  reason_codes: ReasonCode[];
  has_dual_control_requirement: boolean;
  first_analyst_id?: string;
  second_analyst_id?: string;
}

export interface AuditLogEntry {
  log_id: number;
  timestamp: string;
  actor_id: string;
  action: string;
  case_id?: string;
  session_id?: string;
  reason: string;
  ip_address: string;
  previous_hash: string;
  current_hash: string;
}

export async function fetchHealthStatus() {
  const res = await fetch(`${API_BASE_URL}/`);
  return res.json();
}

export async function analyzeAudioFile(file: File, sessionId: string, actionType: string, amount: number) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  formData.append('action_type', actionType);
  formData.append('amount', amount.toString());
  formData.append('is_novel_payee', amount > 25000 ? 'true' : 'false');
  formData.append('recent_credential_change', amount > 50000 ? 'true' : 'false');

  const res = await fetch(`${API_BASE_URL}/api/audio/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json() as Promise<StreamingVerdict>;
}

export async function requestStepUp(sessionId: string, actionType: string, amount: number, payeeName: string) {
  const res = await fetch(`${API_BASE_URL}/api/verification/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      action_type: actionType,
      amount: amount,
      payee_name: payeeName,
    }),
  });
  return res.json() as Promise<VerificationChallenge>;
}

export async function getActiveChallenge(sessionId: string) {
  const res = await fetch(`${API_BASE_URL}/api/verification/active/${sessionId}`);
  if (!res.ok) return null;
  return res.json() as Promise<VerificationChallenge | null>;
}

export async function respondChallenge(challengeId: string, decision: 'APPROVE' | 'DENY', code?: number) {
  const res = await fetch(`${API_BASE_URL}/api/verification/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      challenge_id: challengeId,
      decision: decision,
      entered_matching_code: code,
    }),
  });
  return res.json();
}

export async function interceptUPI(sessionId: string, vpa: string, amount: number, urgency: boolean, tier: string) {
  const res = await fetch(`${API_BASE_URL}/api/upi/intercept?session_tier=${tier}&out_of_band_approved=${tier === 'GREEN'}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      upi_collect_vpa: vpa,
      amount: amount,
      payer_vpa: 'victim@okhdfcbank',
      urgency_flag: urgency,
    }),
  });
  return res.json();
}

export async function fetchCases() {
  const res = await fetch(`${API_BASE_URL}/api/cases`);
  return res.json() as Promise<CaseSummary[]>;
}

export async function takeCaseAction(caseId: string, analystId: string, action: string, notes: string) {
  const res = await fetch(`${API_BASE_URL}/api/cases/${caseId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analyst_id: analystId, action, notes }),
  });
  return res.json();
}

export async function submitAppeal(caseId: string, sessionId: string, customerId: string, reason: string) {
  const res = await fetch(`${API_BASE_URL}/api/cases/appeal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      case_id: caseId,
      session_id: sessionId,
      customer_id: customerId,
      contact_number: '+91 98765 43210',
      appeal_reason: reason,
    }),
  });
  return res.json();
}

export async function fetchAuditLogs() {
  const res = await fetch(`${API_BASE_URL}/api/audit/logs`);
  return res.json() as Promise<AuditLogEntry[]>;
}

export async function verifyAuditChain() {
  const res = await fetch(`${API_BASE_URL}/api/audit/verify`);
  return res.json();
}

export async function fetchEvalSummary() {
  const res = await fetch(`${API_BASE_URL}/api/eval/summary`);
  return res.json();
}
