"""Load EICV7 district poverty rates (2017 modelled, 2024 actual) into the database.

Run from the backend folder, after load_districts:  python -m scripts.load_poverty

Source: NISR, EICV7 Poverty Profile, Annex B. The values live in
data/seed/eicv7_district_poverty.csv (see data/seed/README.md).
"""
import csv
from pathlib import Path

from sqlalchemy import text

from app.db import engine

SEED_FILE = Path(__file__).resolve().parents[2] / "data" / "seed" / "eicv7_district_poverty.csv"

INDICATOR = {
    "code": "poverty_rate",
    "name": "Headcount poverty rate",
    "unit": "% of population",
    "description": "Share of people living below the national poverty line.",
    "source": "NISR, EICV7 Poverty Profile (Annex B)",
    "source_url": "https://www.statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf",
}
NATIONAL = {2017: 39.8, 2024: 27.4}
YEAR_COLUMNS = {2017: "poverty_2017", 2024: "poverty_2024"}

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS indicators (
    code         TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    unit         TEXT NOT NULL,
    description  TEXT,
    source       TEXT NOT NULL,
    source_url   TEXT
);
CREATE TABLE IF NOT EXISTS indicator_values (
    indicator_code  TEXT NOT NULL REFERENCES indicators (code) ON DELETE CASCADE,
    area_code       TEXT NOT NULL,
    year            INTEGER NOT NULL,
    value           NUMERIC(6, 2) NOT NULL,
    PRIMARY KEY (indicator_code, area_code, year)
);
"""

UPSERT_INDICATOR = text(
    """
    INSERT INTO indicators (code, name, unit, description, source, source_url)
    VALUES (:code, :name, :unit, :description, :source, :source_url)
    ON CONFLICT (code) DO UPDATE SET
      name = EXCLUDED.name, unit = EXCLUDED.unit, description = EXCLUDED.description,
      source = EXCLUDED.source, source_url = EXCLUDED.source_url
    """
)
UPSERT_VALUE = text(
    """
    INSERT INTO indicator_values (indicator_code, area_code, year, value)
    VALUES (:indicator_code, :area_code, :year, :value)
    ON CONFLICT (indicator_code, area_code, year) DO UPDATE SET value = EXCLUDED.value
    """
)


def read_seed() -> list[dict]:
    with SEED_FILE.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = read_seed()
    if len(rows) != 30:
        raise ValueError(f"Expected 30 districts in {SEED_FILE.name}, found {len(rows)}")

    with engine.begin() as conn:
        known = set(conn.execute(text("SELECT code FROM districts")).scalars())
        if len(known) != 30:
            raise RuntimeError("Load the district boundaries first: python -m scripts.load_districts")

        values = []
        for row in rows:
            code = row["district"].strip().lower()
            if code not in known:
                raise ValueError(f"Unknown district in seed file: {row['district']!r}")
            for year, column in YEAR_COLUMNS.items():
                value = float(row[column])
                if not 0 <= value <= 100:
                    raise ValueError(f"{row['district']} {year}: {value} is not a percentage")
                values.append({"indicator_code": INDICATOR["code"], "area_code": code, "year": year, "value": value})
        for year, value in NATIONAL.items():
            values.append({"indicator_code": INDICATOR["code"], "area_code": "rwanda", "year": year, "value": value})

        for statement in CREATE_TABLES.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.execute(UPSERT_INDICATOR, INDICATOR)
        conn.execute(UPSERT_VALUE, values)
    print(f"Loaded {len(values)} poverty values (30 districts x 2 years + national).")


if __name__ == "__main__":
    main()
