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


# The funnel stages, in order. Each maps to an event 'kind'.
FUNNEL_STAGES = ["start", "recommend", "tax_view", "feedback"]
_STAGE_LABELS = {
    "start": "Started navigator",
    "recommend": "Got a recommendation",
    "tax_view": "Opened tax estimate",
    "feedback": "Left feedback",
}


def analytics() -> dict[str, Any]:
    """Most-queried structures plus a funnel with step-over-step drop-off."""
    with _conn() as conn:
        counts = {
            row["kind"]: row["c"]
            for row in conn.execute(
                "SELECT kind, COUNT(*) c FROM events GROUP BY kind"
            ).fetchall()
        }
        fb_total = conn.execute("SELECT COUNT(*) c FROM feedback").fetchone()["c"]
        by_entity = conn.execute(
            "SELECT entity_id, COUNT(*) c FROM events WHERE kind='recommend' "
            "AND entity_id IS NOT NULL GROUP BY entity_id ORDER BY c DESC"
        ).fetchall()

    counts["feedback"] = fb_total  # feedback lives in its own table

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
    }
