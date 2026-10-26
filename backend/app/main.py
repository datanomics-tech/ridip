from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db import check_database
from app.districts import get_districts_geojson
from app.indicators import get_indicator, list_indicators

app = FastAPI(
    title="RIDIP API",
    description="Rwanda Integrated Data Intelligence Platform",
    version="0.2.0",
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


@app.get("/api/districts")
def districts() -> dict:
    """Rwanda's 30 districts as GeoJSON, for the map."""
    try:
        return get_districts_geojson()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="District data unavailable")


@app.get("/api/indicators")
def indicators() -> list[dict]:
    """The indicators that have been loaded."""
    try:
        return list_indicators()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Indicator data unavailable")


@app.get("/api/indicators/{code}")
def indicator(code: str) -> dict:
    """One indicator's values by year, nationally and for each district."""
    try:
        result = get_indicator(code)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Indicator data unavailable")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown indicator: {code}")
    return result
