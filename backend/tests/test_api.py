"""API tests: routing, validation, and the logging/analytics round trip."""
import pytest
from fastapi.testclient import TestClient

import main
from app import logging_store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(logging_store, "DB_PATH", tmp_path / "test.db")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    return TestClient(main.app)


def test_entities_expose_branch(client):
    opts = {o["key"]: o for o in client.get("/entities").json()["options"]}
    assert len(opts["aif"]["branch"]["options"]) == 2
    assert opts["bank"]["branch"] is None


def test_recommend_ok(client):
    r = client.post("/recommend", json={"entity_id": "aif", "investor_type": "retail"})
    assert r.status_code == 200
    assert r.json()["id"] == "aif"
    assert r.json()["last_reviewed"]


def test_recommend_unknown_entity_404(client):
    assert client.post("/recommend", json={"entity_id": "nope"}).status_code == 404


def test_recommend_bad_investor_type_422(client):
    r = client.post("/recommend", json={"entity_id": "aif", "investor_type": "whale"})
    assert r.status_code == 422


def test_tax_estimate_ok(client):
    r = client.post(
        "/tax/estimate", json={"annual_income_usd": 2_000_000, "onshore_rate_pct": 25}
    )
    assert r.status_code == 200
    assert r.json()["annual_saving"] == 500_000


def test_tax_estimate_block_out_of_bounds_400(client):
    r = client.post(
        "/tax/estimate",
        json={"annual_income_usd": 1, "onshore_rate_pct": 25, "block_period_years": 40},
    )
    assert r.status_code == 400


def test_classify_match_and_no_match(client):
    r = client.post("/classify", json={"text": "a venture capital fund for startups"})
    assert r.json()["entity_id"] == "aif"
    r = client.post("/classify", json={"text": "zzz qqq"})
    assert r.status_code == 200
    assert r.json()["entity_id"] is None


def test_event_rejects_unknown_kind_and_entity(client):
    assert client.post("/event", json={"kind": "spam"}).status_code == 422
    assert client.post("/event", json={"kind": "start", "entity_id": "x"}).status_code == 422
    assert client.post("/event", json={"kind": "start"}).status_code == 200


def test_feedback_rejects_unknown_entity(client):
    r = client.post("/feedback", json={"entity_id": "nope", "helpful": True})
    assert r.status_code == 422


def test_funnel_counts_sessions_not_events(client):
    # Session A: starts once, gets three recommendations, leaves feedback.
    client.post("/event", json={"kind": "start", "session_id": "A"})
    for _ in range(3):
        client.post("/recommend", json={"entity_id": "bank", "session_id": "A"})
    client.post(
        "/feedback",
        json={"entity_id": "bank", "helpful": False, "comment": "why", "session_id": "A"},
    )
    # Session B: starts and stops.
    client.post("/event", json={"kind": "start", "session_id": "B"})

    data = client.get("/analytics").json()
    funnel = {f["stage"]: f for f in data["funnel"]}
    assert funnel["start"]["count"] == 2
    assert funnel["recommend"]["count"] == 1  # 3 events, 1 session
    assert funnel["recommend"]["drop_from_prev_pct"] == 50.0
    assert funnel["feedback"]["count"] == 1
    assert data["most_queried"] == [
        {"entity_id": "bank", "count": 3, "name": "IFSC Banking Unit (IBU)"}
    ]
    assert data["feedback"] == {"helpful": 0, "total": 1}


def test_export_disabled_without_token_and_guarded_with_one(client, monkeypatch):
    assert client.get("/export").status_code == 404
    monkeypatch.setenv("ADMIN_TOKEN", "s3cret")
    assert client.get("/export").status_code == 401
    client.post("/feedback", json={"entity_id": "bank", "helpful": True, "comment": "ok"})
    r = client.get("/export", headers={"X-Admin-Token": "s3cret"})
    assert r.status_code == 200
    assert r.json()["feedback"][0]["comment"] == "ok"


def test_old_database_gains_session_column(tmp_path, monkeypatch):
    import sqlite3

    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, "
        "kind TEXT NOT NULL, entity_id TEXT, payload TEXT)"
    )
    conn.execute("INSERT INTO events (ts, kind) VALUES ('t', 'start')")
    conn.commit()
    conn.close()

    monkeypatch.setattr(logging_store, "DB_PATH", path)
    logging_store.log_event("start", session_id="A")
    funnel = logging_store.analytics()["funnel"]
    assert funnel[0]["count"] == 2  # legacy row + session A
