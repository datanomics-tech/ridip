from sqlalchemy import create_engine, text

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def check_database() -> dict:
    """Connect to the database and report the PostgreSQL and PostGIS versions."""
    with engine.connect() as conn:
        postgres = conn.execute(text("SHOW server_version")).scalar_one()
        postgis = conn.execute(text("SELECT PostGIS_Version()")).scalar_one()
    return {"postgres": postgres, "postgis": postgis}