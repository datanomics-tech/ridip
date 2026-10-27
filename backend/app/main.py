import csv
import io
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app import analytics
from app.db import check_database
from app.districts import get_districts_geojson
from app.domains import DOMAINS
from app.indicators import get_indicator, list_indicators, load_all

app = FastAPI(
    title="RIDIP API",
    description="Rwanda Integrated Data Intelligence Platform: NISR district indicators for agriculture, "
                "finance & poverty and employment, with explainable need scores.",
    version="0.3.0",
)


def unavailable(what: str) -> HTTPException:
    return HTTPException(status_code=503, detail=f"{what} unavailable")


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
        raise unavailable("Database")
    return {"status": "ok", **versions}


@app.get("/api/districts")
def districts() -> dict:
    """Rwanda's 30 districts as GeoJSON, for the map."""
    try:
        return get_districts_geojson()
    except SQLAlchemyError:
        raise unavailable("District data")


@app.get("/api/domains")
def domains() -> dict:
    """The three tracks and their link to national priorities (NST2, Vision 2050)."""
    return DOMAINS


@app.get("/api/indicators")
def indicators() -> list[dict]:
    """Every loaded indicator, with its track, unit, source and available years."""
    try:
        return list_indicators()
    except SQLAlchemyError:
        raise unavailable("Indicator data")


@app.get("/api/indicators/{code}")
def indicator(code: str) -> dict:
    """One indicator's values by year, nationally and for each district (with standard errors where published)."""
    try:
        result = get_indicator(code)
    except SQLAlchemyError:
        raise unavailable("Indicator data")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown indicator: {code}")
    return result


@app.get("/api/overview")
def overview() -> dict:
    """Need index for every district in each track, priority districts and the district typology."""
    try:
        return analytics.overview()
    except SQLAlchemyError:
        raise unavailable("Indicator data")


@app.get("/api/places/{code}")
def place(code: str) -> dict:
    """A district profile: every indicator with national comparison, rank, trend, need scores and insights."""
    try:
        result = analytics.place_profile(code)
    except SQLAlchemyError:
        raise unavailable("Indicator data")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown district: {code}")
    return result


def csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.get("/api/places/{code}/report.csv")
def place_report(code: str) -> StreamingResponse:
    """Download a district profile as CSV."""
    profile = place(code)
    rows = []
    for dom, track in profile["tracks"].items():
        for i in track["indicators"]:
            rows.append({"district": profile["name"], "track": track["title"], "indicator": i["name"],
                         "year": i["year"], "value": i["value"], "unit": i["unit"], "rwanda": i["national"],
                         "gap_to_rwanda": i["gap"], "rank_of_30": i["rank"], "significance": i["significance"] or "",
                         "source": i["source"]})
    return csv_response(rows, f"ridip-{code}-profile.csv")


@app.get("/api/data.csv")
def all_data() -> StreamingResponse:
    """Download every indicator value (long format) with its metadata."""
    try:
        meta, values = load_all()
    except SQLAlchemyError:
        raise unavailable("Indicator data")
    rows = [{"indicator_code": v["indicator_code"], "indicator": meta[v["indicator_code"]]["name"],
             "track": DOMAINS[meta[v["indicator_code"]]["domain"]]["title"], "area": v["area_code"],
             "year": v["year"], "value": v["value"], "se": "" if v["se"] is None else v["se"],
             "unit": meta[v["indicator_code"]]["unit"], "source": meta[v["indicator_code"]]["source"]}
            for v in values]
    return csv_response(rows, "ridip-indicators.csv")


# In production the built React app is served from the same address as the API.
# Locally, run "npm run dev" in frontend/ instead; this folder only exists after a build.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        """Serve files from the build, and index.html for app routes such as /place/nyagatare."""
        if path.startswith(("api/", "health")):
            raise HTTPException(status_code=404)
        file = (FRONTEND_DIST / path).resolve()
        if path and file.is_file() and FRONTEND_DIST in file.parents:
            return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
