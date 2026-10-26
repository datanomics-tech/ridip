import { useEffect, useMemo, useState } from "react";
import DistrictMap, { PROVINCE_COLOURS } from "./DistrictMap";
import type { DistrictCollection } from "./types";

export default function App() {
  const [districts, setDistricts] = useState<DistrictCollection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/districts")
      .then((res) => {
        if (!res.ok) throw new Error(`The API returned ${res.status}`);
        return res.json();
      })
      .then(setDistricts)
      .catch(() =>
        setError("District data could not be loaded. Check that the API and database are running."),
      );
  }, []);

  const current = useMemo(
    () => districts?.features.find((f) => f.properties.code === selected) ?? null,
    [districts, selected],
  );

  return (
    <div className="layout">
      <header className="topbar">
        <span className="brand">RIDIP</span>
        <span className="tagline">Rwanda Integrated Data Intelligence Platform</span>
      </header>

      <main className="content">
        <section className="map-panel" aria-label="Map of Rwanda's districts">
          {error && <p className="notice">{error}</p>}
          {!error && !districts && <p className="notice">Loading districts…</p>}
          {districts && <DistrictMap districts={districts} selected={selected} onSelect={setSelected} />}
        </section>

        <aside className="side-panel">
          {current ? (
            <>
              <p className="eyebrow">{current.properties.province}</p>
              <h1>{current.properties.name}</h1>
              <p>District indicators will appear here once NISR data is loaded.</p>
              <button type="button" onClick={() => setSelected(null)}>
                Clear selection
              </button>
            </>
          ) : (
            <>
              <h1>Rwanda's 30 districts</h1>
              <p>Select a district on the map to see its profile.</p>
            </>
          )}

          <h2>Provinces</h2>
          <ul className="legend">
            {Object.entries(PROVINCE_COLOURS).map(([name, colour]) => (
              <li key={name}>
                <span className="swatch" style={{ background: colour }} />
                {name}
              </li>
            ))}
          </ul>

          <p className="source">
            Boundaries: geoBoundaries (Open Data Rwanda / NISR), CC BY 4.0.
          </p>
        </aside>
      </main>
    </div>
  );
}
