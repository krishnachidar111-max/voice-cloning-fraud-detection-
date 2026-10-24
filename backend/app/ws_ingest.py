"""
EchoGuard AI - Real-Time Audio WebSocket Ingest Gateway
Implements FR-1, FR-2, FR-3, FR-4:
- Bidirectional WebSocket streaming for browser mic, file streaming, and scripted replay
- 10-second volatile in-memory ring buffer per active call session
- Streaming 2-second windows with 1-second step interval
- Zero disk write guarantee (audio lives in RAM only, destroyed on disconnect)
- Emits real-time StreamingVerdict containing tier, scores, and plain-language reason codes
"""

import json
import base64
import time
import asyncio
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
from backend.audio.ring_buffer import MemoryRingBuffer
from backend.audio.windows import AudioDecoder
from backend.audio.vad import VoiceActivityDetector
from backend.models.infer import AudioInferenceEngine
from backend.fusion.accumulator import EvidenceAccumulator
from backend.fusion.policy import PolicyEngine
from backend.signals.interaction import get_interaction_signal
from backend.signals.transaction import get_transaction_signal
from backend.app.schemas import StreamingVerdict


class SessionState:
    """Encapsulates all in-flight state for a single active phone call or demo session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.ring_buffer = MemoryRingBuffer(capacity_seconds=10.0, sample_rate=16000)
        self.accumulator = EvidenceAccumulator()
        self.vad = VoiceActivityDetector(sample_rate=16000)
        self.window_index = 0
        self.action_type = "balance_inquiry"
        self.amount = 0.0
        self.is_novel_payee = False
        self.velocity_1h_count = 0
        self.recent_credential_change_24h = False
        self.mule_account_risk_score = 0.0
        self.response_latency_s = 0.8
        self.turn_taking_jitter_s = 0.1
        self.prosodic_variance = 0.85
        self.caller_ani_reputation = 0.1
        self.unscripted_challenge_latency_s: Optional[float] = None
        self.out_of_band_failed = False
        self.latest_verdict: Optional[StreamingVerdict] = None

    def purge(self):
        """Zero out volatile buffer memory upon call termination."""
        self.ring_buffer.purge()
        self.accumulator.reset()


class AudioWebSocketManager:
    """Manages active WebSocket connections and audio processing loops."""

    def __init__(self):
        self.active_sessions: Dict[str, SessionState] = {}
        self.inference_engine = AudioInferenceEngine()
        self.policy_engine = PolicyEngine()

    def get_or_create_session(self, session_id: str) -> SessionState:
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = SessionState(session_id)
        return self.active_sessions[session_id]

    async def handle_connection(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        session = self.get_or_create_session(session_id)

        try:
            while True:
                message = await websocket.receive()

                if "bytes" in message and message["bytes"]:
                    # Binary PCM chunk directly from browser audio worklet
                    raw_bytes = message["bytes"]
                    samples, sr = AudioDecoder.decode(raw_bytes)
                    session.ring_buffer.append(samples)

                elif "text" in message and message["text"]:
                    # Structured JSON payload
                    try:
                        data = json.loads(message["text"])
                        msg_type = data.get("type", "")

                        if msg_type == "audio_chunk":
                            audio_b64 = data.get("data", "")
                            if audio_b64:
                                audio_bytes = base64.b64decode(audio_b64)
                                samples, sr = AudioDecoder.decode(audio_bytes)
                                session.ring_buffer.append(samples)

                        elif msg_type == "context_update":
                            # Dynamic banking transaction or interaction update
                            session.action_type = data.get("action_type", session.action_type)
                            session.amount = float(data.get("amount", session.amount))
                            session.is_novel_payee = bool(data.get("is_novel_payee", session.is_novel_payee))
                            session.velocity_1h_count = int(data.get("velocity_1h_count", session.velocity_1h_count))
                            session.recent_credential_change_24h = bool(data.get("recent_credential_change_24h", session.recent_credential_change_24h))
                            session.mule_account_risk_score = float(data.get("mule_account_risk_score", session.mule_account_risk_score))
                            session.response_latency_s = float(data.get("response_latency_s", session.response_latency_s))
                            session.caller_ani_reputation = float(data.get("caller_ani_reputation", session.caller_ani_reputation))
                            if "unscripted_challenge_latency_s" in data:
                                session.unscripted_challenge_latency_s = float(data["unscripted_challenge_latency_s"])

                        elif msg_type == "out_of_band_decision":
                            # Customer responded to push verification
                            decision = data.get("decision", "DENY")
                            session.out_of_band_failed = (decision == "DENY")

                    except json.JSONDecodeError:
                        pass

                # If we have at least 0.5s of audio in buffer, run window evaluation
                window_samples = session.ring_buffer.get_latest(duration_seconds=2.0)
                if len(window_samples) >= 8000:
                    session.window_index += 1

                    # 1. Audio family analysis
                    audio_signal = self.inference_engine.analyze(window_samples, sample_rate=16000)

                    # 2. Interaction family signal
                    interaction_signal = get_interaction_signal(
                        response_latency_s=session.response_latency_s,
                        turn_taking_jitter_s=session.turn_taking_jitter_s,
                        prosodic_variance=session.prosodic_variance,
                        caller_ani_reputation=session.caller_ani_reputation,
                        unscripted_challenge_latency_s=session.unscripted_challenge_latency_s
                    )

                    # 3. Transaction family signal
                    txn_signal = get_transaction_signal(
                        action_type=session.action_type,
                        amount=session.amount,
                        is_novel_payee=session.is_novel_payee,
                        velocity_1h_count=session.velocity_1h_count,
                        recent_credential_change_24h=session.recent_credential_change_24h,
                        mule_account_risk_score=session.mule_account_risk_score
                    )

                    # 4. Evidence accumulation
                    session.accumulator.add_window(
                        llr_audio=audio_signal.llr,
                        llr_interaction=interaction_signal.llr,
                        llr_transaction=txn_signal.llr
                    )

                    # 5. Policy evaluation
                    verdict = self.policy_engine.evaluate(
                        session_id=session_id,
                        window_index=session.window_index,
                        accumulator=session.accumulator,
                        audio_signal=audio_signal,
                        interaction_signal=interaction_signal,
                        txn_signal=txn_signal,
                        out_of_band_failed=session.out_of_band_failed
                    )
                    session.latest_verdict = verdict

                    # Stream verdict back to client
                    await websocket.send_text(verdict.model_dump_json())

                # Yield control briefly to event loop
                await asyncio.sleep(0.05)

        except WebSocketDisconnect:
            pass
        finally:
            # Enforce zero raw audio retention: purge buffer immediately
            session.purge()
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]


ws_manager = AudioWebSocketManager()
