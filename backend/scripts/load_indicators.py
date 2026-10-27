"""Load all RIDIP indicators into the database.

Run from the backend folder, after load_districts:  python -m scripts.load_indicators

Reads data/seed/indicators.csv and data/seed/indicator_values.csv, which are built from
official NISR files by analytics/etl/build_seed.py (see data/seed/README.md).
The tables are rebuilt on every run, so the script is safe to repeat.
"""
import csv
from pathlib import Path

from sqlalchemy import text

from app.db import engine

SEED = Path(__file__).resolve().parents[2] / "data" / "seed"
DOMAINS = {"agriculture", "finance_poverty", "employment", "health", "education", "transport"}

SCHEMA = """
DROP TABLE IF EXISTS indicator_values;
DROP TABLE IF EXISTS indicators;
CREATE TABLE indicators (
    code        TEXT PRIMARY KEY,
    domain      TEXT NOT NULL,
    name        TEXT NOT NULL,
    unit        TEXT NOT NULL,
    direction   TEXT NOT NULL CHECK (direction IN ('higher', 'lower')),
    source      TEXT NOT NULL,
    source_url  TEXT,
    note        TEXT,
    value_type  TEXT NOT NULL DEFAULT 'official',
    position    INTEGER NOT NULL
);
CREATE TABLE indicator_values (
    indicator_code  TEXT NOT NULL REFERENCES indicators (code) ON DELETE CASCADE,
    area_code       TEXT NOT NULL,
    year            INTEGER NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    se              DOUBLE PRECISION,
    PRIMARY KEY (indicator_code, area_code, year)
);
CREATE INDEX indicator_values_area_idx ON indicator_values (area_code);
"""


def read(name: str) -> list[dict]:
    with (SEED / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    indicators = read("indicators.csv")
    values = read("indicator_values.csv")
    codes = {i["code"] for i in indicators}

    with engine.begin() as conn:
        districts = set(conn.execute(text("SELECT code FROM districts")).scalars())
        if len(districts) != 30:
            raise RuntimeError("Load the district boundaries first: python -m scripts.load_districts")

        for i in indicators:
            if i["domain"] not in DOMAINS:
                raise ValueError(f"{i['code']}: unknown domain {i['domain']!r}")
        rows = []
        for v in values:
            if v["indicator_code"] not in codes:
                raise ValueError(f"Value for unknown indicator {v['indicator_code']!r}")
            if v["area_code"] not in districts and v["area_code"] != "rwanda":
                raise ValueError(f"Unknown area {v['area_code']!r}")
            rows.append({**v, "year": int(v["year"]), "value": float(v["value"]),
                         "se": float(v["se"]) if v["se"] else None})
        for code in codes:
            covered = {r["area_code"] for r in rows if r["indicator_code"] == code}
            if not districts <= covered:
                raise ValueError(f"{code}: missing districts {sorted(districts - covered)}")

        for statement in SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.execute(
            text("""INSERT INTO indicators (code, domain, name, unit, direction, source, source_url, note, value_type, position)
                    VALUES (:code, :domain, :name, :unit, :direction, :source, :source_url, :note, :value_type, :position)"""),
            [{**i, "position": n} for n, i in enumerate(indicators)],
        )
        conn.execute(
            text("""INSERT INTO indicator_values (indicator_code, area_code, year, value, se)
                    VALUES (:indicator_code, :area_code, :year, :value, :se)"""),
            rows,
        )
    print(f"Loaded {len(indicators)} indicators and {len(rows)} values.")


if __name__ == "__main__":
    main()
