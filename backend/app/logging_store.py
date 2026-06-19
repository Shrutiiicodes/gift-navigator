"""SQLite-backed logging for recommendation events and user feedback.

The event log doubles as a usage dataset for the evaluation chapter.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(os.environ.get("GIFT_DB_PATH", Path(__file__).parent / "gift.db"))


_initialized = False


def _conn() -> sqlite3.Connection:
    global _initialized
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if not _initialized:
        _create_tables(conn)
        _initialized = True
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            kind TEXT NOT NULL,
            entity_id TEXT,
            payload TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            entity_id TEXT,
            helpful INTEGER NOT NULL,
            comment TEXT
        )
        """
    )


def init_db() -> None:
    with _conn() as conn:
        _create_tables(conn)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(kind: str, entity_id: Optional[str] = None, payload: Any = None) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO events (ts, kind, entity_id, payload) VALUES (?, ?, ?, ?)",
            (_now(), kind, entity_id, json.dumps(payload) if payload is not None else None),
        )


def log_feedback(entity_id: str, helpful: bool, comment: Optional[str]) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (ts, entity_id, helpful, comment) VALUES (?, ?, ?, ?)",
            (_now(), entity_id, 1 if helpful else 0, comment),
        )
        return int(cur.lastrowid)


def stats() -> dict[str, Any]:
    """Aggregate counts for a simple admin/usage view."""
    with _conn() as conn:
        by_entity = conn.execute(
            "SELECT entity_id, COUNT(*) c FROM events WHERE kind='recommend' "
            "GROUP BY entity_id ORDER BY c DESC"
        ).fetchall()
        fb = conn.execute(
            "SELECT SUM(helpful) helpful, COUNT(*) total FROM feedback"
        ).fetchone()
    return {
        "recommendations_by_entity": {r["entity_id"]: r["c"] for r in by_entity},
        "feedback_helpful": fb["helpful"] or 0,
        "feedback_total": fb["total"] or 0,
    }
