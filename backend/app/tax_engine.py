"""Tax engine: estimates saving from the GIFT IFSC tax holiday vs staying onshore.

Two modes:
  * Simple (default): full Section 80LA deduction during the holiday, concessional rate
    on the tail of the block. Surcharge/cess/MAT all off, so it reduces to the original
    first-order model and stays backward compatible.
  * Advanced: layers surcharge and cess onto every tax figure, and optionally applies
    minimum alternate tax (MAT) during the holiday and as a floor afterwards - narrowing
    the gap to a filing-grade estimate.

Pure module - no web-framework imports.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).parent / "data"

DISCLAIMER = (
    "Indicative model only. Simple mode assumes eligible income qualifies for the "
    "Section 80LA 100% deduction during a 10-year window of the block period, with a "
    "concessional rate thereafter. Advanced mode adds surcharge, cess and (optionally) "
    "minimum alternate tax, but still ignores GST and entity-specific rules. "
    "Not legal or tax advice."
)


@lru_cache(maxsize=1)
def load_tax_rules() -> dict[str, Any]:
    return json.loads((DATA_DIR / "tax_rules.json").read_text(encoding="utf-8"))


def _with_surcharge_cess(base_tax: float, surcharge_pct: float, cess_pct: float) -> float:
    """Surcharge applies on tax; cess applies on (tax + surcharge)."""
    after_surcharge = base_tax * (1 + surcharge_pct / 100.0)
    after_cess = after_surcharge * (1 + cess_pct / 100.0)
    return after_cess


def estimate(
    annual_income_usd: float,
    onshore_rate_pct: float,
    block_period_years: Optional[int] = None,
    advanced: bool = False,
    surcharge_pct: Optional[float] = None,
    cess_pct: Optional[float] = None,
    mat_rate_pct: Optional[float] = None,
    apply_mat: bool = False,
) -> dict[str, Any]:
    """Estimate annual, holiday-period and full-block savings, plus a year-by-year series.

    In simple mode (advanced=False) surcharge/cess are 0 and MAT is off, so the result
    matches the original model exactly.
    """
    if annual_income_usd < 0:
        raise ValueError("annual_income_usd must be non-negative")
    if not (0 <= onshore_rate_pct <= 100):
        raise ValueError("onshore_rate_pct must be between 0 and 100")

    rules = load_tax_rules()
    s80 = rules["section_80la"]
    holiday_years = int(s80["holiday_years"])
    post_rate = float(s80["post_holiday_rate_pct"]) / 100.0

    bounds = rules.get("block_period_bounds_years", {"min": holiday_years, "max": 25})
    if block_period_years is None:
        block_years = int(s80["block_period_years"])
    else:
        block_years = int(block_period_years)
        if not (bounds["min"] <= block_years <= bounds["max"]):
            raise ValueError(
                f"block_period_years must be between {bounds['min']} and {bounds['max']}"
            )

    # Advanced knobs - default to the data file's values when advanced is on, else neutral.
    adv = rules.get("advanced_defaults", {})
    if advanced:
        sc = adv.get("surcharge_pct", 0) if surcharge_pct is None else surcharge_pct
        ce = adv.get("cess_pct", 0) if cess_pct is None else cess_pct
        mat = adv.get("mat_rate_pct", 0) if mat_rate_pct is None else mat_rate_pct
    else:
        sc, ce, mat = 0.0, 0.0, 0.0
        apply_mat = False

    onshore_rate = onshore_rate_pct / 100.0
    mat_rate = mat / 100.0

    # Per-year tax figures.
    onshore_tax_annual = _with_surcharge_cess(
        annual_income_usd * onshore_rate, sc, ce
    )

    # During the holiday: 100% deduction => base tax 0, but MAT can apply as a floor.
    holiday_base = mat_rate * annual_income_usd if apply_mat else 0.0
    ifsc_holiday_annual = _with_surcharge_cess(holiday_base, sc, ce)

    # After the holiday: concessional rate, with MAT as a floor if enabled.
    post_base = post_rate * annual_income_usd
    if apply_mat:
        post_base = max(post_base, mat_rate * annual_income_usd)
    ifsc_post_annual = _with_surcharge_cess(post_base, sc, ce)

    annual_saving = onshore_tax_annual - ifsc_holiday_annual
    holiday_total_saving = annual_saving * holiday_years

    remaining_years = max(0, block_years - holiday_years)
    block_tail_saving = (onshore_tax_annual - ifsc_post_annual) * remaining_years
    block_total_saving = holiday_total_saving + block_tail_saving

    # Year-by-year cumulative series (powers the cumulative chart).
    series = []
    cum_onshore = cum_ifsc = 0.0
    for year in range(1, block_years + 1):
        in_holiday = year <= holiday_years
        ifsc_year = ifsc_holiday_annual if in_holiday else ifsc_post_annual
        cum_onshore += onshore_tax_annual
        cum_ifsc += ifsc_year
        series.append(
            {
                "year": year,
                "phase": "holiday" if in_holiday else "concessional",
                "onshore_cumulative": round(cum_onshore, 2),
                "ifsc_cumulative": round(cum_ifsc, 2),
                "saving_cumulative": round(cum_onshore - cum_ifsc, 2),
            }
        )

    return {
        "annual_income_usd": round(annual_income_usd, 2),
        "onshore_rate_pct": round(onshore_rate_pct, 2),
        "onshore_tax_annual": round(onshore_tax_annual, 2),
        "ifsc_tax_annual": round(ifsc_holiday_annual, 2),
        "annual_saving": round(annual_saving, 2),
        "holiday_years": holiday_years,
        "holiday_total_saving": round(holiday_total_saving, 2),
        "block_period_years": block_years,
        "post_holiday_rate_pct": s80["post_holiday_rate_pct"],
        "ifsc_post_holiday_annual": round(ifsc_post_annual, 2),
        "block_total_saving": round(block_total_saving, 2),
        "advanced": advanced,
        "surcharge_pct": sc,
        "cess_pct": ce,
        "mat_rate_pct": mat,
        "apply_mat": apply_mat,
        "series": series,
        "disclaimer": DISCLAIMER,
    }
