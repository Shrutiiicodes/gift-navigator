"""Free-text intake classifier.

Hybrid design: cheap, deterministic keyword scoring runs FIRST. The LLM is only
called as a fallback when keyword confidence is below a threshold - so the common
case is free, fast and explainable, and the LLM cost/latency is bounded. This
gating is itself a measurable design decision for the dissertation.
"""
from __future__ import annotations

import os
import re
from typing import Any, Optional

from .rules_engine import load_entities

CONFIDENCE_THRESHOLD = 0.30  # below this, escalate to the LLM (if configured)


def _tokenize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def keyword_score(text: str) -> tuple[Optional[str], float, list[str]]:
    """Score the text against each entity's match_keywords.

    Returns (best_entity_id, confidence, matched_terms). Confidence is the
    winner's share of total keyword hits across all entities (0..1).
    """
    clean = _tokenize(text)
    hits: dict[str, list[str]] = {}
    total = 0
    for eid, e in load_entities().items():
        matched = []
        for kw in e["match_keywords"]:
            # word-boundary match with lightweight plural tolerance (kw / kw+s).
            if re.search(rf"(?<![a-z]){re.escape(kw)}s?(?![a-z])", clean):
                matched.append(kw)
        if matched:
            hits[eid] = matched
            total += len(matched)

    if not hits:
        return None, 0.0, []

    best = max(hits, key=lambda k: len(hits[k]))
    confidence = len(hits[best]) / total if total else 0.0
    return best, round(confidence, 3), hits[best]


def _llm_classify(text: str) -> Optional[dict[str, Any]]:
    """Optional LLM fallback via Groq. Returns None if no API key is configured.

    Kept import-local so the package works with zero extra dependencies when
    the LLM path is disabled.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq  # type: ignore
    except ImportError:
        return None

    ids = list(load_entities().keys())
    client = Groq(api_key=api_key)
    prompt = (
        "You route a business description to ONE GIFT City IFSC entity type.\n"
        f"Valid ids: {', '.join(ids)}.\n"
        "Reply with ONLY the id, nothing else.\n\n"
        f"Business: {text}"
    )
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=1024,            # reasoning models need room to think + answer
            temperature=0,
            reasoning_effort="low",     # minimize thinking for a simple routing task
            messages=[{"role": "user", "content": prompt}],
        )
        out = (resp.choices[0].message.content or "").strip().lower()
        guess = next((i for i in ids if i == out), None) \
            or next((i for i in ids if i in out), None)
        if guess:
            return {"entity_id": guess, "confidence": 0.75, "method": "llm"}
    except Exception as e:
        return None
    return None


def classify(text: str) -> dict[str, Any]:
    """Classify free-text into an entity id using the hybrid strategy."""
    best, confidence, matched = keyword_score(text)

    if best is not None and confidence >= CONFIDENCE_THRESHOLD:
        return {
            "entity_id": best,
            "confidence": confidence,
            "method": "keyword",
            "matched_terms": matched,
            "note": None,
        }

    # Low keyword confidence -> try the LLM fallback.
    llm = _llm_classify(text)
    if llm is not None:
        return {
            "entity_id": llm["entity_id"],
            "confidence": llm["confidence"],
            "method": "llm",
            "matched_terms": matched,
            "note": "Resolved by LLM fallback (low keyword confidence).",
        }

    # No LLM available - return best keyword guess or a safe default.
    if best is not None:
        return {
            "entity_id": best,
            "confidence": confidence,
            "method": "keyword",
            "matched_terms": matched,
            "note": "Low-confidence keyword match; consider the guided wizard.",
        }

    return {
        "entity_id": "fintech",
        "confidence": 0.0,
        "method": "fallback",
        "matched_terms": [],
        "note": "No clear match. Showing a common starting point; use the wizard for accuracy.",
    }
