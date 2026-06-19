"""Unit tests for the rules engine."""
import pytest

from app import rules_engine


def test_all_entities_resolve():
    for eid in rules_engine.list_entity_ids():
        out = rules_engine.recommend(eid)
        assert out["id"] == eid
        assert out["name"]
        assert out["eligibility"], f"{eid} has no eligibility rules"
        assert out["activities"], f"{eid} has no activities"
        assert "weeks" in out["timeline_label"]


def test_unknown_entity_raises():
    with pytest.raises(KeyError):
        rules_engine.recommend("not_a_real_entity")


def test_aif_nonretail_net_worth():
    out = rules_engine.recommend("aif", investor_type="nonretail")
    nw = [r for r in out["eligibility"] if "net worth" in r["rule"].lower()][0]
    assert "500,000" in nw["rule"]
    assert "non-retail" in nw["rule"]


def test_aif_retail_net_worth():
    out = rules_engine.recommend("aif", investor_type="retail")
    nw = [r for r in out["eligibility"] if "net worth" in r["rule"].lower()][0]
    assert "3,000,000" in nw["rule"]
    assert "retail" in nw["rule"]


def test_bank_capital_resolved():
    out = rules_engine.recommend("bank")
    cap = [r for r in out["eligibility"] if "assigned capital" in r["rule"].lower()][0]
    assert "20,000,000" in cap["rule"]


def test_every_rule_has_a_source():
    for eid in rules_engine.list_entity_ids():
        out = rules_engine.recommend(eid)
        for rule in out["eligibility"]:
            assert rule["source"], f"{eid} rule missing source: {rule['rule']}"


def test_wizard_options_cover_all_entities():
    opts = rules_engine.wizard_options()
    keys = {o["key"] for o in opts}
    assert keys == set(rules_engine.list_entity_ids())
