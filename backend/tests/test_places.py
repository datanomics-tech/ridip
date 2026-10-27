import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.test_indicators import indicators_loaded

client = TestClient(app)
pytestmark = pytest.mark.skipif(not indicators_loaded(), reason="Indicators are not loaded")


def test_place_profile_has_three_tracks_and_insights():
    body = client.get("/api/places/nyagatare").json()
    assert body["name"] == "Nyagatare"
    assert set(body["tracks"]) == {"agriculture", "finance_poverty", "employment"}
    poverty = next(i for i in body["tracks"]["finance_poverty"]["indicators"] if i["code"] == "poverty_rate")
    assert poverty["value"] == 36.4 and poverty["national"] == 27.4
    assert poverty["significance"] == "significantly above"
    assert body["insights"] and body["group"]["name"].startswith("Group")


def test_kigali_is_not_ranked_on_agriculture():
    body = client.get("/api/places/nyarugenge").json()
    assert body["tracks"]["agriculture"]["need"] is None
    assert body["tracks"]["finance_poverty"]["need"] is not None


def test_overview_priorities_and_groups():
    body = client.get("/api/overview").json()
    for track in body["tracks"].values():
        assert len(track["priority"]) == 5
    members = [m["code"] for g in body["groups"] for m in g["members"]]
    assert sorted(members) == sorted(body["group_of"]) and len(members) == 30


def test_csv_downloads():
    report = client.get("/api/places/huye/report.csv")
    assert report.status_code == 200 and report.text.startswith("district,track,indicator")
    assert len(report.text.strip().splitlines()) == 22
    data = client.get("/api/data.csv")
    assert data.status_code == 200 and len(data.text.strip().splitlines()) == 1871


def test_unknown_place_returns_404():
    assert client.get("/api/places/atlantis").status_code == 404
