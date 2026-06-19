"""Tax engine: estimates saving from the GIFT IFSC tax holiday vs staying onshore.

Deliberately simplified. Ignores minimum alternate tax, surcharge, GST and
entity-specific rules. Pure module - no web-framework imports.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"

DISCLAIMER = (
    "Indicative model only. Assumes eligible income qualifies for the Section 80LA "
    "100% deduction during a 10-year window of the block period, with a concessional "
    "rate thereafter. Ignores minimum alternate tax, surcharge, GST and entity-specific "
    "rules. Not legal or tax advice."
)


@lru_cache(maxsize=1)
def load_tax_rules() -> dict[str, Any]:
    return json.loads((DATA_DIR / "tax_rules.json").read_text(encoding="utf-8"))


def estimate(annual_income_usd: float, onshore_rate_pct: float) -> dict[str, Any]:
    """Estimate annual, holiday-period and full-block savings.

    During the holiday, eligible income is fully deducted, so IFSC tax = 0.
    After the holiday (within the block), a concessional rate applies onshore-side
    comparison continues at the user's onshore rate.
    """
    if annual_income_usd < 0:
        raise ValueError("annual_income_usd must be non-negative")
    if not (0 <= onshore_rate_pct <= 100):
        raise ValueError("onshore_rate_pct must be between 0 and 100")

    rules = load_tax_rules()["section_80la"]
    holiday_years = int(rules["holiday_years"])
    block_years = int(rules["block_period_years"])
    post_rate = float(rules["post_holiday_rate_pct"]) / 100.0

    onshore_rate = onshore_rate_pct / 100.0

    onshore_tax_annual = annual_income_usd * onshore_rate
    ifsc_tax_annual = 0.0  # full deduction during the holiday
    annual_saving = onshore_tax_annual - ifsc_tax_annual

    # Holiday window: full saving each year.
    holiday_total_saving = annual_saving * holiday_years

    # Remaining years inside the block: IFSC pays concessional rate, onshore pays full.
    remaining_years = max(0, block_years - holiday_years)
    onshore_block_tail = annual_income_usd * onshore_rate * remaining_years
    ifsc_block_tail = annual_income_usd * post_rate * remaining_years
    block_tail_saving = onshore_block_tail - ifsc_block_tail

    block_total_saving = holiday_total_saving + block_tail_saving

    return {
        "annual_income_usd": round(annual_income_usd, 2),
        "onshore_rate_pct": round(onshore_rate_pct, 2),
        "onshore_tax_annual": round(onshore_tax_annual, 2),
        "ifsc_tax_annual": round(ifsc_tax_annual, 2),
        "annual_saving": round(annual_saving, 2),
        "holiday_years": holiday_years,
        "holiday_total_saving": round(holiday_total_saving, 2),
        "block_period_years": block_years,
        "post_holiday_rate_pct": rules["post_holiday_rate_pct"],
        "block_total_saving": round(block_total_saving, 2),
        "disclaimer": DISCLAIMER,
    }
