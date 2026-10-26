from sqlalchemy import text

from app.db import engine


def list_indicators() -> list[dict]:
    query = text("SELECT code, name, unit, source FROM indicators ORDER BY name")
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(query).mappings()]


def get_indicator(code: str) -> dict | None:
    """One indicator with its values by year, for Rwanda and for each district."""
    with engine.connect() as conn:
        meta = conn.execute(
            text("SELECT code, name, unit, description, source, source_url FROM indicators WHERE code = :code"),
            {"code": code},
        ).mappings().first()
        if meta is None:
            return None
        rows = conn.execute(
            text("SELECT area_code, year, value FROM indicator_values WHERE indicator_code = :code ORDER BY year"),
            {"code": code},
        ).mappings().all()

    national: dict[str, float] = {}
    districts: dict[str, dict[str, float]] = {}
    for r in rows:
        year, value = str(r["year"]), float(r["value"])
        if r["area_code"] == "rwanda":
            national[year] = value
        else:
            districts.setdefault(r["area_code"], {})[year] = value

    years = sorted({int(r["year"]) for r in rows})
    return {**dict(meta), "years": years, "national": national, "districts": districts}
