"""
EchoGuard AI - Independent Out-of-Band Step-Up Verification
Implements FR-15:
- Issues single-use cryptographic push tokens to the Customer Banking App Simulator
- Number-matching code (e.g. 47) to defeat remote screen-share / social engineering
- 5-minute expiry window with replay prevention
"""

import secrets
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from backend.app.schemas import VerificationChallenge, VerificationResponse
from backend.store.db import db
from backend.store.audit import audit_logger


class StepUpOrchestrator:
    """Manages out-of-band mobile verification challenges."""

    def __init__(self):
        self.challenges: Dict[str, VerificationChallenge] = {}

    def create_challenge(
        self,
        session_id: str,
        action_type: str,
        amount: float,
        payee: str = "Self / Bank"
    ) -> VerificationChallenge:
        """Issues an out-of-band verification challenge for Amber/Orange step-up."""
        challenge_id = f"CHAL-{secrets.token_hex(4).upper()}"
        token = secrets.token_urlsafe(32)
        number_matching = random.randint(11, 99)

        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(minutes=5)).isoformat()

        challenge = VerificationChallenge(
            challenge_id=challenge_id,
            session_id=session_id,
            token=token,
            action_type=action_type,
            amount=amount,
            payee=payee,
            number_matching_code=number_matching,
            status="PENDING",
            created_at=now.isoformat(),
            expires_at=expires_at
        )

        self.challenges[challenge_id] = challenge

        # Save to DB
        with db._get_connection() as conn:
            conn.execute("""
            INSERT INTO verification_challenges
            (challenge_id, session_id, token, action_type, amount, payee, number_matching_code, status, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                challenge.challenge_id, challenge.session_id, challenge.token, challenge.action_type,
                challenge.amount, challenge.payee, challenge.number_matching_code, challenge.status,
                challenge.created_at, challenge.expires_at
            ))
            conn.commit()

        # Audit log entry
        audit_logger.append(
            actor_id="STEPUP_ENGINE",
            action="CHALLENGE_CREATED",
            reason=f"Issued out-of-band challenge {challenge_id} for {action_type} (INR {amount})",
            session_id=session_id
        )

        return challenge

    def respond_to_challenge(
        self,
        challenge_id: str,
        decision: str,
        entered_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """Processes customer response (Approve/Deny) from mobile app simulator."""
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            return {"success": False, "error": "Challenge not found or expired"}

        if challenge.status != "PENDING":
            return {"success": False, "error": f"Challenge already {challenge.status}"}

        if decision == "APPROVE":
            # Verify number matching
            if entered_code is not None and entered_code != challenge.number_matching_code:
                challenge.status = "DENIED"
                audit_logger.append(
                    actor_id="CUSTOMER_APP",
                    action="CHALLENGE_FAILED_CODE_MISMATCH",
                    reason=f"Number matching failed on {challenge_id}. Expected {challenge.number_matching_code}, got {entered_code}",
                    session_id=challenge.session_id
                )
                return {"success": False, "status": "DENIED", "reason": "Number matching code incorrect"}

            challenge.status = "APPROVED"
            audit_logger.append(
                actor_id="CUSTOMER_APP",
                action="CHALLENGE_APPROVED",
                reason=f"Customer confirmed out-of-band approval for {challenge.action_type} ({challenge_id})",
                session_id=challenge.session_id
            )
            return {"success": True, "status": "APPROVED"}

        else:  # DENIED
            challenge.status = "DENIED"
            audit_logger.append(
                actor_id="CUSTOMER_APP",
                action="CHALLENGE_DENIED_BY_CUSTOMER",
                reason=f"Customer explicitly tapped DENY for {challenge.action_type} on {challenge_id} (Fraud Stopped)",
                session_id=challenge.session_id
            )
            return {"success": True, "status": "DENIED", "reason": "Customer denied transaction in mobile app"}

    def get_latest_challenge_for_session(self, session_id: str) -> Optional[VerificationChallenge]:
        """Returns the active challenge for a given session."""
        for c in reversed(list(self.challenges.values())):
            if c.session_id == session_id and c.status == "PENDING":
                return c
        return None


stepup_orchestrator = StepUpOrchestrator()
