"""Unit tests for the tax engine."""
import pytest

from app import tax_engine


def test_basic_saving():
    out = tax_engine.estimate(2_000_000, 25)
    # 25% of 2M = 500k onshore, 0 in IFSC during holiday
    assert out["onshore_tax_annual"] == 500_000
    assert out["ifsc_tax_annual"] == 0
    assert out["annual_saving"] == 500_000


def test_holiday_total_is_ten_years():
    out = tax_engine.estimate(1_000_000, 30)
    assert out["holiday_years"] == 10
    assert out["holiday_total_saving"] == out["annual_saving"] * 10


def test_block_saving_includes_concessional_tail():
    out = tax_engine.estimate(1_000_000, 30)
    # block = 25y: 10y holiday (full saving) + 15y at (30% - 15%) delta
    holiday = 300_000 * 10
    tail = (300_000 - 150_000) * 15  # onshore 30% vs ifsc 15% on 1M, 15 years
    assert out["block_total_saving"] == holiday + tail


def test_zero_income():
    out = tax_engine.estimate(0, 25)
    assert out["onshore_tax_annual"] == 0
    assert out["annual_saving"] == 0
    assert out["block_total_saving"] == 0


def test_zero_rate():
    out = tax_engine.estimate(5_000_000, 0)
    assert out["annual_saving"] == 0


def test_negative_income_rejected():
    with pytest.raises(ValueError):
        tax_engine.estimate(-1, 25)


def test_rate_out_of_bounds_rejected():
    with pytest.raises(ValueError):
        tax_engine.estimate(1_000_000, 150)


def test_disclaimer_present():
    out = tax_engine.estimate(1_000_000, 25)
    assert "Not legal or tax advice" in out["disclaimer"]


# ---- Extension tests: adjustable block, cumulative series, advanced mode ----

def test_series_length_matches_block():
    out = tax_engine.estimate(1_000_000, 25, block_period_years=18)
    assert out["block_period_years"] == 18
    assert len(out["series"]) == 18
    assert out["series"][-1]["year"] == 18


def test_series_is_cumulative_and_monotonic():
    out = tax_engine.estimate(1_000_000, 25)
    savings = [p["saving_cumulative"] for p in out["series"]]
    assert savings == sorted(savings)  # never decreases
    assert out["series"][-1]["saving_cumulative"] == out["block_total_saving"]


def test_series_phase_switches_after_holiday():
    out = tax_engine.estimate(1_000_000, 25)
    assert out["series"][9]["phase"] == "holiday"        # year 10
    assert out["series"][10]["phase"] == "concessional"  # year 11


def test_block_period_out_of_bounds_rejected():
    with pytest.raises(ValueError):
        tax_engine.estimate(1_000_000, 25, block_period_years=40)


def test_advanced_surcharge_cess_increases_onshore_tax():
    simple = tax_engine.estimate(1_000_000, 30)
    adv = tax_engine.estimate(1_000_000, 30, advanced=True)
    # surcharge + cess lift the onshore tax above the plain figure
    assert adv["onshore_tax_annual"] > simple["onshore_tax_annual"]
    # 300k * 1.12 * 1.04 = 349,440
    assert adv["onshore_tax_annual"] == 349_440


def test_mat_floor_lifts_holiday_tax_off_zero():
    no_mat = tax_engine.estimate(1_000_000, 30, advanced=True, apply_mat=False)
    with_mat = tax_engine.estimate(1_000_000, 30, advanced=True, apply_mat=True)
    assert no_mat["ifsc_tax_annual"] == 0
    assert with_mat["ifsc_tax_annual"] > 0
    # 9% MAT * 1.12 * 1.04 = 104,832
    assert with_mat["ifsc_tax_annual"] == 104_832


def test_simple_mode_ignores_advanced_knobs():
    # advanced=False must zero out surcharge/cess/MAT regardless of passed values
    out = tax_engine.estimate(
        1_000_000, 30, surcharge_pct=99, cess_pct=99, mat_rate_pct=99, apply_mat=True
    )
    assert out["surcharge_pct"] == 0
    assert out["ifsc_tax_annual"] == 0
