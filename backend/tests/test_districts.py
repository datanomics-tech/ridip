import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.main import app

client = TestClient(app)


def districts_loaded() -> bool:
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT count(*) FROM districts")).scalar_one() > 0
    except SQLAlchemyError:
        return False


@pytest.mark.skipif(not districts_loaded(), reason="District data is not loaded")
def test_districts_returns_30_features():
    response = client.get("/api/districts")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 30
    names = {f["properties"]["name"] for f in body["features"]}
    assert {"Nyagatare", "Musanze", "Huye", "Gasabo"} <= names
