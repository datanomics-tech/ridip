import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.main import app

client = TestClient(app)


def indicators_loaded() -> bool:
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT count(*) FROM indicators")).scalar_one() >= 21
    except SQLAlchemyError:
        return False


pytestmark = pytest.mark.skipif(not indicators_loaded(), reason="Indicators are not loaded")


def test_all_three_tracks_have_indicators():
    body = client.get("/api/indicators").json()
    domains = {i["domain"] for i in body}
    assert domains == {"agriculture", "finance_poverty", "employment"}
    assert len(body) == 21


def test_poverty_values_match_eicv7_annex_b():
    body = client.get("/api/indicators/poverty_rate").json()
    assert body["years"] == [2017, 2024]
    assert body["national"] == {"2017": 39.8, "2024": 27.4}
    assert len(body["districts"]) == 30
    assert body["districts"]["nyamagabe"] == {"2017": 67.6, "2024": 51.4}
    assert body["se"]["nyamagabe"]["2024"] == 3.21          # EICV7 Main Indicators Report, Table A9.23


def test_values_match_other_sources():
    seeds = client.get("/api/indicators/ag_improved_seeds").json()
    assert seeds["districts"]["nyagatare"]["2025"] == 55.24  # SAS 2025, Table 33
    neet = client.get("/api/indicators/emp_youth_neet").json()
    assert round(neet["districts"]["nyarugenge"]["2025"], 1) == 19.4  # LFS 2025, Table 21
    banked = client.get("/api/indicators/fin_banked").json()
    assert banked["districts"]["nyarugenge"]["2024"] == 59    # FinScope 2024, Figure 13


def test_unknown_indicator_returns_404():
    assert client.get("/api/indicators/not_real").status_code == 404
