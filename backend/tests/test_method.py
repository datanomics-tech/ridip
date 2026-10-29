"""Acceptance tests for the scoring method (plan section 2.3) and the priority brief (section 4)."""
import copy

import pytest
from fastapi.testclient import TestClient

from app import analytics
from app.indicators import load_all
from app.main import app
from tests.test_indicators import indicators_loaded

client = TestClient(app)
pytestmark = pytest.mark.skipif(not indicators_loaded(), reason="Indicators are not loaded")


def build_with(change) -> dict:
    """Run the model on a modified copy of the loaded data."""
    meta, values = load_all()
    values = copy.deepcopy(values)
    change(values)
    return analytics._build_model((meta, values))


def test_orientation_worse_value_never_lowers_need():
    # Poverty: lower is better. Raising Huye's poverty must not lower its z-score or its finance need rank.
    base = analytics.model()
    def worse(values):
        for v in values:
            if v["indicator_code"] == "poverty_rate" and v["area_code"] == "huye" and v["year"] == 2024:
                v["value"] += 10
    m = build_with(worse)
    assert m["z"]["poverty_rate"]["huye"] > base["z"]["poverty_rate"]["huye"]
    assert m["need_rank"]["finance_poverty"]["huye"] <= base["need_rank"]["finance_poverty"]["huye"]


def test_higher_is_better_indicator_is_reversed():
    # Improved seeds: higher is better, so the district with the highest use has the lowest (most negative) z.
    m = analytics.model()
    z = m["z"]["ag_improved_seeds"]
    best = max(m["value"]["ag_improved_seeds"], key=lambda d: m["value"]["ag_improved_seeds"][d] if d in z else -1)
    assert z[best] == min(z.values())


def test_missing_district_value_excludes_indicator_with_reason():
    def drop(values):
        values[:] = [v for v in values if not (v["indicator_code"] == "tr_bicycle" and v["area_code"] == "rutsiro")]
    m = build_with(drop)
    assert "tr_bicycle" in m["excluded"] and "every district" in m["excluded"]["tr_bicycle"]
    assert "tr_bicycle" not in m["sector_codes"]["transport"]


def test_zero_variance_indicator_is_excluded_not_divided_by_zero():
    def flatten(values):
        for v in values:
            if v["indicator_code"] == "tr_motorcycle":
                v["value"] = 2.0
    m = build_with(flatten)
    assert "no variation" in m["excluded"]["tr_motorcycle"]
    assert m["z"]["tr_motorcycle"] == {}


def test_ties_are_ordered_alphabetically_and_repeatably():
    def tie(values):
        for v in values:
            if v["indicator_code"] == "edu_literacy" and v["year"] == 2024 and v["area_code"] in ("bugesera", "nyanza"):
                v["value"] = 80.0
    m1, m2 = build_with(tie), build_with(tie)
    assert m1["rank"]["edu_literacy"] == m2["rank"]["edu_literacy"]
    assert m1["rank"]["edu_literacy"]["bugesera"] + 1 == m1["rank"]["edu_literacy"]["nyanza"]


def test_kigali_not_ranked_on_agriculture():
    for code in ("nyarugenge", "gasabo", "kicukiro"):
        brief = client.get(f"/api/places/{code}/priority-brief", params={"domain": "agriculture"}).json()
        assert brief["need_rank"] is None and brief["statements"][0]["rule_id"] == "R0-not-ranked"


def test_sensitivity_reported_for_every_sector():
    body = client.get("/api/method").json()
    assert set(body["sensitivity"]) == {"agriculture", "finance_poverty", "employment", "health", "education", "transport"}
    for s in body["sensitivity"].values():
        assert len(s["scenarios"]) == s["indicators"]
        assert 0 <= s["min_top5_overlap"] <= 5
    assert body["excluded"] == []


def test_priority_brief_is_deterministic_traceable_and_not_causal():
    url, params = "/api/places/gicumbi/priority-brief", {"domain": "health"}
    a, b = client.get(url, params=params).json(), client.get(url, params=params).json()
    assert a == b and a["version"] == "1.0"
    drivers = [s for s in a["statements"] if s["rule_id"] == "R2-driver"]
    assert drivers and all(s["evidence"] and s["evidence"][0]["source"] for s in drivers)
    assert drivers[0]["evidence"][0]["code"] == "health_stunting" and drivers[0]["evidence"][0]["value"] == 38.8
    target = next(s for s in a["statements"] if s["rule_id"] == "R4-target")
    assert "national target, not one assigned to the district" in target["text"]
    text = " ".join(s["text"] for s in a["statements"]).lower()
    for phrase in ("will reduce", "will improve", "leads to", "caused by", "because of"):
        assert phrase not in text


def test_priority_brief_unknown_inputs_404():
    assert client.get("/api/places/atlantis/priority-brief", params={"domain": "health"}).status_code == 404
    assert client.get("/api/places/huye/priority-brief", params={"domain": "space"}).status_code == 404


def test_difference_flag_only_with_standard_errors():
    body = client.get("/api/places/nyagatare").json()
    for track in body["tracks"].values():
        for i in track["indicators"]:
            if i["se"] is None:
                assert i["difference_flag"] is None
            else:
                assert i["difference_flag"] in ("above", "below", "no clear difference")
