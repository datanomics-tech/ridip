from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db import check_database

app = FastAPI(
    title="RIDIP API",
    description="Rwanda Integrated Data Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    """Simple check that the API is running."""
    return {"status": "ok", "service": "ridip-api"}


@app.get("/health/db")
def health_db() -> dict:
    """Check that the API can reach the database and that PostGIS is enabled."""
    try:
        versions = check_database()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", **versions}