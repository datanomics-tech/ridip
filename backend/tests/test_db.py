import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.db import check_database
from app.main import app

client = TestClient(app)


def database_available() -> bool:
    try:
        check_database()
        return True
    except SQLAlchemyError:
        return False


@pytest.mark.skipif(not database_available(), reason="Database is not running")
def test_health_db_reports_postgis():
    response = client.get("/health/db")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["postgis"]