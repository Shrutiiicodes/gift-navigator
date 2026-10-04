"""Free-text intake classifier.

Hybrid design: cheap, deterministic keyword scoring runs FIRST. The LLM is only
called as a fallback when keyword evidence is weak - so the common case is free,
fast and explainable, and the LLM cost/latency is bounded.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import date
from functools import lru_cache
from typing import Any, Optional

from .rules_engine import load_entities

log = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.30  # below this, escalate to the LLM (if configured)
MIN_HITS = 2                 # a single keyword hit is not enough evidence on its own
LLM_TIMEOUT_S = 8.0

# ponytail: per-process daily cap on LLM calls, resets on restart. Move to the DB
# if the API ever runs on more than one worker.
_llm_calls = {"day": None, "count": 0}


def _tokenize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def keyword_score(text: str) -> tuple[Optional[str], float, list[str], bool]:
    """Score the text against each entity's match_keywords.

    Returns (best_entity_id, confidence, matched_terms, tied). Confidence is the
    winner's share of total keyword hits across all entities (0..1); `tied` is
    True when another entity has as many hits as the winner.
    """
    clean = _tokenize(text)
    hits: dict[str, list[str]] = {}
    total = 0
    for eid, e in load_entities().items():
        matched = []
        for kw in e["match_keywords"]:
            # Keywords go through the same normalisation as the text (so "in-house"
            # matches), then word-boundary match with plural tolerance (kw / kw+s).
            norm = _tokenize(kw).strip()
            if re.search(rf"(?<![a-z]){re.escape(norm)}s?(?![a-z])", clean):
                matched.append(kw)
        if matched:
            hits[eid] = matched
            total += len(matched)

    if not hits:
        return None, 0.0, [], False

    ranked = sorted(hits, key=lambda k: len(hits[k]), reverse=True)
    best = ranked[0]
    tied = len(ranked) > 1 and len(hits[ranked[1]]) == len(hits[best])
    return best, round(len(hits[best]) / total, 3), hits[best], tied


def _llm_cap_reached() -> bool:
    cap = int(os.environ.get("LLM_DAILY_CAP", "200"))
    today = date.today()
    if _llm_calls["day"] != today:
        _llm_calls.update(day=today, count=0)
    if _llm_calls["count"] >= cap:
        return True
    _llm_calls["count"] += 1
    return False


@lru_cache(maxsize=512)
def _llm_route(text: str, api_key: str) -> Optional[str]:
    """One Groq call -> entity id (or None if the reply names no valid id).

    Cached per text so repeats are free. Raises on API failure, and lru_cache
    does not cache exceptions, so a transient error is retried next time.
    """
    from groq import Groq  # import-local: the package works without groq installed

    if _llm_cap_reached():
        raise RuntimeError("daily LLM call cap reached")

    entities = load_entities()
    ids = list(entities.keys())
    client = Groq(api_key=api_key, timeout=LLM_TIMEOUT_S)
    # Describe each id - bare ids like "gic" or "aif" are not enough for the model.
    options = "\n".join(
        f"- {eid}: {e['name']} ({e['tag']}). {e['what']}" for eid, e in entities.items()
    )
    prompt = (
        "You route a business description to ONE GIFT City IFSC entity type.\n"
        f"Entity types:\n{options}\n\n"
        "Reply with ONLY the id (the word before the colon), nothing else.\n\n"
        f"Business: {text}"
    )
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        max_tokens=1024,            # reasoning models need room to think + answer
        temperature=0,
        reasoning_effort="low",     # minimize thinking for a simple routing task
        messages=[{"role": "user", "content": prompt}],
    )
    out = (resp.choices[0].message.content or "").strip().lower()
    return next((i for i in ids if i == out), None) \
        or next((i for i in ids if i in out), None)


def _llm_classify(text: str) -> Optional[dict[str, Any]]:
    """Optional LLM fallback via Groq. Returns None if unconfigured or it fails."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        guess = _llm_route(text, api_key)
    except Exception as exc:  # network, auth, timeout, cap, groq not installed
        log.warning("LLM fallback failed: %s", exc)
        return None
    if guess:
        return {"entity_id": guess, "confidence": 0.75, "method": "llm"}
    return None


def classify(text: str) -> dict[str, Any]:
    """Classify free-text into an entity id using the hybrid strategy.

    entity_id is None when nothing matched and no LLM answer is available - the
    caller should send the user to the guided wizard rather than guess.
    """
    best, confidence, matched, tied = keyword_score(text)

    strong = (
        best is not None
        and confidence >= CONFIDENCE_THRESHOLD
        and len(matched) >= MIN_HITS
        and not tied
    )
    if strong:
        return {
            "entity_id": best,
            "confidence": confidence,
            "method": "keyword",
            "matched_terms": matched,
            "note": None,
        }

    # Weak keyword evidence -> try the LLM fallback.
    llm = _llm_classify(text)
    if llm is not None:
        return {
            "entity_id": llm["entity_id"],
            "confidence": llm["confidence"],
            "method": "llm",
            "matched_terms": matched,
            "note": "Resolved by LLM fallback (weak keyword evidence).",
        }

    # No LLM available - return the weak keyword guess, with an honest confidence.
    if best is not None:
        return {
            "entity_id": best,
            "confidence": min(confidence, 0.5),
            "method": "keyword",
            "matched_terms": matched,
            "note": "Low-confidence keyword match; consider the guided wizard.",
        }

    return {
        "entity_id": None,
        "confidence": 0.0,
        "method": "fallback",
        "matched_terms": [],
        "note": "No clear match. Pick the closest option in the guided wizard.",
    }
