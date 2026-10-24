"""
EchoGuard AI - Relational Score Store & Metadata Database
Fulfills FR-23:
- Stores only scores, reason codes, timestamps, and pseudonymous session IDs (SESS-XXXXXXXX)
- Strictly ZERO raw audio stored in database tables
- SQLite backend with ACID transaction guarantees
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.config import settings


class DatabaseManager:
    """Manages SQLite tables for sessions, scores, cases, and verification challenges."""

    def __init__(self, db_path: str = "echoguard.db"):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Sessions table (pseudonymous metadata only)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                customer_id_masked TEXT NOT NULL,
                ani_caller_id TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                final_tier TEXT DEFAULT 'GREEN',
                risk_score REAL DEFAULT 0.0,
                status TEXT DEFAULT 'ACTIVE'
            )
            """)

            # Scores time-series table (zero audio, numeric metrics only)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS score_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                window_index INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                tier TEXT NOT NULL,
                risk_score REAL NOT NULL,
                llr_audio REAL NOT NULL,
                llr_interaction REAL NOT NULL,
                llr_transaction REAL NOT NULL,
                reason_codes_json TEXT,
                processing_latency_ms REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
            """)

            # Cases table for Orange/Red fraud analyst triage
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                customer_id_masked TEXT NOT NULL,
                tier TEXT NOT NULL,
                risk_score REAL NOT NULL,
                action_attempted TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                reason_codes_json TEXT NOT NULL,
                has_dual_control_requirement INTEGER DEFAULT 0,
                first_analyst_id TEXT,
                second_analyst_id TEXT,
                investigation_notes TEXT DEFAULT ''
            )
            """)

            # Out-of-band verification challenges table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_challenges (
                challenge_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                token TEXT NOT NULL,
                action_type TEXT NOT NULL,
                amount REAL NOT NULL,
                payee TEXT NOT NULL,
                number_matching_code INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """)

            # Customer appeals & false-positive clearance table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_appeals (
                appeal_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                appeal_reason TEXT NOT NULL,
                status TEXT NOT NULL,
                why_it_fired TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resolved_at TEXT
            )
            """)

            conn.commit()


db = DatabaseManager()
