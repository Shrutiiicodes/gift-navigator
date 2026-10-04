"""SQLite-backed logging for recommendation events and user feedback.

The event log doubles as the usage dataset behind the analytics funnel.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

DB_PATH = Path(os.environ.get("GIFT_DB_PATH", Path(__file__).parent / "gift.db"))

_ready: set[str] = set()  # DB paths whose tables have been created/migrated


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    """Open a connection, commit on success, and always close it."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            if str(DB_PATH) not in _ready:
                _create_tables(conn)
                _ready.add(str(DB_PATH))
            yield conn
    finally:
        conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            kind TEXT NOT NULL,
            entity_id TEXT,
            payload TEXT,
            session_id TEXT
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
            comment TEXT,
            session_id TEXT
        )
        """
    )
    # Databases created before session tracking lack the column; old rows keep NULL.
    for table in ("events", "feedback"):
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        if "session_id" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN session_id TEXT")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    kind: str,
    entity_id: Optional[str] = None,
    payload: Any = None,
    session_id: Optional[str] = None,
) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO events (ts, kind, entity_id, payload, session_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                _now(),
                kind,
                entity_id,
                json.dumps(payload) if payload is not None else None,
                session_id,
            ),
        )


def log_feedback(
    entity_id: str,
    helpful: bool,
    comment: Optional[str],
    session_id: Optional[str] = None,
) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (ts, entity_id, helpful, comment, session_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (_now(), entity_id, 1 if helpful else 0, comment, session_id),
        )
        return int(cur.lastrowid)


# The funnel stages, in order. Each maps to an event 'kind'.
FUNNEL_STAGES = ["start", "recommend", "tax_view", "feedback"]
_STAGE_LABELS = {
    "start": "Opened the navigator",
    "recommend": "Got a recommendation",
    "tax_view": "Used tax estimate",
    "feedback": "Left feedback",
}

# Count each session once per stage. Rows without a session id (logged before
# session tracking existed) each count as their own session.
_SESSIONS = "COUNT(DISTINCT COALESCE(session_id, 'row-' || id))"


def analytics() -> dict[str, Any]:
    """Most-queried structures, feedback totals, and a per-session funnel."""
    with _conn() as conn:
        counts = {
            row["kind"]: row["c"]
            for row in conn.execute(
                f"SELECT kind, {_SESSIONS} c FROM events GROUP BY kind"
            ).fetchall()
        }
        fb = conn.execute(
            f"SELECT {_SESSIONS} sessions, COUNT(*) total, SUM(helpful) helpful "
            "FROM feedback"
        ).fetchone()
        by_entity = conn.execute(
            "SELECT entity_id, COUNT(*) c FROM events WHERE kind='recommend' "
            "AND entity_id IS NOT NULL GROUP BY entity_id ORDER BY c DESC"
        ).fetchall()

    counts["feedback"] = fb["sessions"]  # feedback lives in its own table

    funnel = []
    prev = None
    for stage in FUNNEL_STAGES:
        n = counts.get(stage, 0)
        drop = None
        if prev is not None and prev > 0:
            drop = round((1 - n / prev) * 100, 1)
        funnel.append(
            {
                "stage": stage,
                "label": _STAGE_LABELS[stage],
                "count": n,
                "drop_from_prev_pct": drop,
            }
        )
        prev = n if n > 0 else prev

    return {
        "most_queried": [
            {"entity_id": r["entity_id"], "count": r["c"]} for r in by_entity
        ],
        "funnel": funnel,
        "feedback": {"helpful": fb["helpful"] or 0, "total": fb["total"]},
    }


def export() -> dict[str, list[dict[str, Any]]]:
    """Every raw event and feedback row, for pulling the data off the host."""
    with _conn() as conn:
        return {
            table: [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY id")]
            for table in ("events", "feedback")
        }
