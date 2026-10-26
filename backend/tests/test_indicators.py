import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.main import app

client = TestClient(app)


def poverty_loaded() -> bool:
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT count(*) FROM indicator_values")).scalar_one() > 0
    except SQLAlchemyError:
        return False


pytestmark = pytest.mark.skipif(not poverty_loaded(), reason="Poverty data is not loaded")


def test_poverty_has_all_districts_and_national_values():
    body = client.get("/api/indicators/poverty_rate").json()
    assert body["years"] == [2017, 2024]
    assert body["national"] == {"2017": 39.8, "2024": 27.4}
    assert len(body["districts"]) == 30


def test_poverty_values_match_eicv7_annex_b():
    districts = client.get("/api/indicators/poverty_rate").json()["districts"]
    assert districts["nyamagabe"] == {"2017": 67.6, "2024": 51.4}
    assert districts["nyarugenge"]["2024"] == 6.8
    assert districts["musanze"]["2024"] == 21.0


def test_unknown_indicator_returns_404():
    assert client.get("/api/indicators/not_real").status_code == 404
