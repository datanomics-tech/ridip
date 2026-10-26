"""Load Rwanda's 30 district boundaries into PostGIS.

Run from the backend folder:  python -m scripts.load_districts

Boundary source: geoBoundaries (gbOpen, RWA ADM2), originally from Open Data
Rwanda / NISR, licensed CC BY 4.0. The downloaded file is cached in data/raw/,
which is not committed to Git.
"""
import json
import urllib.request
from pathlib import Path

from sqlalchemy import text

from app.db import engine

SOURCE_URL = (
    "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/"
    "releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2_simplified.geojson"
)
CACHE_FILE = Path(__file__).resolve().parents[2] / "data" / "raw" / "rwa_districts.geojson"

PROVINCES = {
    "City of Kigali": ["Gasabo", "Kicukiro", "Nyarugenge"],
    "Eastern": ["Bugesera", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Nyagatare", "Rwamagana"],
    "Northern": ["Burera", "Gakenke", "Gicumbi", "Musanze", "Rulindo"],
    "Southern": ["Gisagara", "Huye", "Kamonyi", "Muhanga", "Nyamagabe", "Nyanza", "Nyaruguru", "Ruhango"],
    "Western": ["Karongi", "Ngororero", "Nyabihu", "Nyamasheke", "Rubavu", "Rusizi", "Rutsiro"],
}
PROVINCE_OF = {district: province for province, names in PROVINCES.items() for district in names}

CREATE_TABLE = """
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS districts (
    code      TEXT PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    province  TEXT NOT NULL,
    geom      geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS districts_geom_idx ON districts USING GIST (geom);
"""

UPSERT = text(
    """
    INSERT INTO districts (code, name, province, geom)
    VALUES (:code, :name, :province, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geometry), 4326)))
    ON CONFLICT (code) DO UPDATE
      SET name = EXCLUDED.name, province = EXCLUDED.province, geom = EXCLUDED.geom
    """
)


def download() -> dict:
    if not CACHE_FILE.exists():
        print(f"Downloading district boundaries to {CACHE_FILE} ...")
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(SOURCE_URL, CACHE_FILE)
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))


def main() -> None:
    features = download()["features"]
    rows = []
    for feature in features:
        name = feature["properties"]["shapeName"].strip()
        if name not in PROVINCE_OF:
            raise ValueError(f"Unknown district name in source file: {name!r}")
        rows.append(
            {
                "code": name.lower(),
                "name": name,
                "province": PROVINCE_OF[name],
                "geometry": json.dumps(feature["geometry"]),
            }
        )
    if len(rows) != 30:
        raise ValueError(f"Expected 30 districts, found {len(rows)}")

    with engine.begin() as conn:
        for statement in CREATE_TABLE.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.execute(UPSERT, rows)
    print(f"Loaded {len(rows)} districts.")


if __name__ == "__main__":
    main()
