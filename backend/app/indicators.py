import time

from sqlalchemy import text

from app.db import engine

META_COLUMNS = "code, domain, name, unit, direction, source, source_url, note, value_type"


CACHE_SECONDS = 300
_cache: dict = {"at": 0.0, "data": None}


def load_all() -> tuple[dict, list[dict]]:
    """All indicator metadata and values, re-read from the database at most every 5 minutes,
    so a rerun of the loader shows up without restarting the app."""
    if _cache["data"] is None or time.monotonic() - _cache["at"] > CACHE_SECONDS:
        _cache["data"] = _read()
        _cache["at"] = time.monotonic()
    return _cache["data"]


def clear_cache() -> None:
    _cache["data"] = None


def _read() -> tuple[dict, list[dict]]:
    with engine.connect() as conn:
        meta = {r["code"]: dict(r) for r in conn.execute(text(f"SELECT {META_COLUMNS} FROM indicators ORDER BY position")).mappings()}
        values = [dict(r) for r in conn.execute(
            text("SELECT indicator_code, area_code, year, value, se FROM indicator_values ORDER BY year")).mappings()]
    return meta, values


def list_indicators() -> list[dict]:
    meta, values = load_all()
    years: dict[str, set] = {}
    for v in values:
        years.setdefault(v["indicator_code"], set()).add(v["year"])
    return [{**m, "years": sorted(years.get(c, []))} for c, m in meta.items()]   # already in display order


def get_indicator(code: str) -> dict | None:
    """One indicator with its values by year, for Rwanda and for each district."""
    meta, values = load_all()
    if code not in meta:
        return None
    national: dict[str, float] = {}
    districts: dict[str, dict[str, float]] = {}
    se: dict[str, dict[str, float]] = {}
    for v in values:
        if v["indicator_code"] != code:
            continue
        year = str(v["year"])
        if v["area_code"] == "rwanda":
            national[year] = v["value"]
        else:
            districts.setdefault(v["area_code"], {})[year] = v["value"]
        if v["se"] is not None:
            se.setdefault(v["area_code"], {})[year] = v["se"]
    years = sorted({v["year"] for v in values if v["indicator_code"] == code})
    return {**meta[code], "years": years, "national": national, "districts": districts, "se": se}
