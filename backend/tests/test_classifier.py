"""Unit tests for the hybrid classifier, plus the golden-set regression gate."""
import pytest

from app import classifier
from eval import run_eval


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)


def test_hyphenated_keyword_matches():
    best, _, matched, _ = classifier.keyword_score("an in-house captive unit")
    assert best == "gic"
    assert "in-house" in matched


def test_strong_keyword_match_has_no_note():
    out = classifier.classify("a venture capital fund")
    assert out["entity_id"] == "aif"
    assert out["method"] == "keyword"
    assert out["note"] is None


def test_single_hit_is_not_trusted():
    # "exchange" alone used to score confidence 1.0 for broker.
    out = classifier.classify("we cover risks in exchange for premiums")
    assert out["confidence"] <= 0.5
    assert out["note"]


def test_no_match_returns_none():
    out = classifier.classify("zzz qqq")
    assert out["entity_id"] is None
    assert out["method"] == "fallback"


def test_weak_evidence_escalates_to_llm(monkeypatch):
    monkeypatch.setattr(
        classifier,
        "_llm_classify",
        lambda text: {"entity_id": "insure", "confidence": 0.75, "method": "llm"},
    )
    out = classifier.classify("we cover risks in exchange for premiums")
    assert out["entity_id"] == "insure"
    assert out["method"] == "llm"


def test_strong_evidence_skips_llm(monkeypatch):
    def boom(text):
        raise AssertionError("LLM must not be called for a strong keyword match")

    monkeypatch.setattr(classifier, "_llm_classify", boom)
    assert classifier.classify("a venture capital fund")["entity_id"] == "aif"


def test_llm_failure_falls_back_to_keyword(monkeypatch):
    def fail(text, api_key):
        raise TimeoutError("groq down")

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(classifier, "_llm_route", fail)
    out = classifier.classify("we cover risks in exchange for premiums")
    assert out["method"] == "keyword"
    assert out["entity_id"] == "broker"


def test_llm_daily_cap(monkeypatch):
    monkeypatch.setenv("LLM_DAILY_CAP", "2")
    monkeypatch.setattr(classifier, "_llm_calls", {"day": None, "count": 0})
    assert [classifier._llm_cap_reached() for _ in range(3)] == [False, False, True]


def test_golden_set_does_not_regress():
    """Keyword-only baseline. Raise the floor when the keyword lists improve."""
    report = run_eval.run()
    assert report["by_difficulty"]["easy"]["accuracy"] == 1.0
    assert report["accuracy"] >= 0.84
    confident_misses = [f for f in report["failures"] if f["confidence"] > 0.5]
    assert not confident_misses, confident_misses
