import json

from sqlalchemy import text

from app.db import engine


def get_districts_geojson() -> dict:
    """Return all districts as a GeoJSON FeatureCollection."""
    query = text(
        """
        SELECT code, name, province, ST_AsGeoJSON(geom, 5) AS geometry
        FROM districts
        ORDER BY name
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    features = [
        {
            "type": "Feature",
            "properties": {
                "code": row["code"],
                "name": row["name"],
                "province": row["province"],
            },
            "geometry": json.loads(row["geometry"]),
        }
        for row in rows
    ]
    return {"type": "FeatureCollection", "features": features}
