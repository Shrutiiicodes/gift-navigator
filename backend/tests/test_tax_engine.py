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
