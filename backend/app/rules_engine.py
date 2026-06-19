"""Rules engine: maps wizard answers to a recommended IFSC entity structure.

Pure module - no web-framework imports - so it can be unit tested and reused
by the evaluation harness directly.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def load_entities() -> dict[str, dict[str, Any]]:
    """Load entities.json and index it by id. Cached after first read."""
    raw = json.loads((DATA_DIR / "entities.json").read_text(encoding="utf-8"))
    return {e["id"]: e for e in raw["entities"]}


def list_entity_ids() -> list[str]:
    return list(load_entities().keys())


def _timeline_label(entity: dict[str, Any]) -> str:
    low, high = entity["timeline_weeks"]
    note = entity.get("timeline_note", "").strip()
    base = f"~{low}-{high} weeks"
    return f"{base} ({note})" if note else base


def _resolve_eligibility(
    entity: dict[str, Any], investor_type: Optional[str]
) -> list[dict[str, Any]]:
    """Turn raw eligibility entries into resolved rules with human values.

    The only branch in the current dataset is the AIF net-worth rule, which
    depends on retail vs non-retail investor type.
    """
    resolved: list[dict[str, Any]] = []
    for item in entity["eligibility"]:
        rule_text = item["rule"]
        value: Optional[str] = None

        if "value_nonretail_usd" in item and "value_retail_usd" in item:
            is_retail = investor_type == "retail"
            amount = (
                item["value_retail_usd"] if is_retail else item["value_nonretail_usd"]
            )
            kind = "retail fund" if is_retail else "non-retail fund"
            value = f"USD {amount:,.0f} ({kind})"
            rule_text = f"{rule_text}: {value}"
        elif "value_usd" in item:
            value = f"USD {item['value_usd']:,.0f}"
            rule_text = f"{rule_text}: {value}"

        resolved.append(
            {
                "rule": rule_text,
                "source": item["source"],
                "ref_url": item.get("ref_url"),
                "value": value,
            }
        )
    return resolved


def recommend(entity_id: str, investor_type: Optional[str] = None) -> dict[str, Any]:
    """Return the resolved recommendation payload for a chosen entity.

    Raises KeyError if the entity id is unknown - the API layer maps that to 404.
    """
    entities = load_entities()
    if entity_id not in entities:
        raise KeyError(entity_id)

    entity = entities[entity_id]
    return {
        "id": entity["id"],
        "name": entity["name"],
        "sub": entity["sub"],
        "tag": entity["tag"],
        "regulator": entity["regulator"],
        "what": entity["what"],
        "eligibility": _resolve_eligibility(entity, investor_type),
        "timeline_label": _timeline_label(entity),
        "activities": entity["activities"],
    }


def wizard_options() -> list[dict[str, str]]:
    """Surface the first-step wizard options (one card per entity)."""
    icons = {
        "aif": "TrendingUp",
        "bank": "Landmark",
        "gic": "Puzzle",
        "lease": "Plane",
        "insure": "Shield",
        "fintech": "Zap",
        "broker": "LineChart",
    }
    out = []
    for eid, e in load_entities().items():
        out.append(
            {
                "key": eid,
                "icon": icons.get(eid, "HelpCircle"),
                "title": e["what"].split(".")[0],
                "name": e["name"],
                "tag": e["tag"],
            }
        )
    return out
