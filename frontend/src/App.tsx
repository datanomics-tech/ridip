import { useEffect, useMemo, useRef, useState } from "react";
import DistrictMap from "./DistrictMap";
import { colourFor, LEGEND } from "./scale";
import type { DistrictCollection, Indicator } from "./types";

const LATEST = "2024";
const BASELINE = "2017";

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} returned ${res.status}`);
  return res.json() as Promise<T>;
}

const pct = (v: number) => `${v.toFixed(1)}%`;
const pts = (v: number) => `${Math.abs(v).toFixed(1)} points`;

export default function App() {
  const [districts, setDistricts] = useState<DistrictCollection | null>(null);
  const [poverty, setPoverty] = useState<Indicator | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const panel = useRef<HTMLElement>(null);

  // Show the district profile at the top of the panel whenever the selection changes.
  useEffect(() => {
    panel.current?.scrollTo({ top: 0, behavior: "smooth" });
  }, [selected]);

  useEffect(() => {
    Promise.all([
      getJson<DistrictCollection>("/api/districts"),
      getJson<Indicator>("/api/indicators/poverty_rate"),
    ])
      .then(([d, p]) => {
        setDistricts(d);
        setPoverty(p);
      })
      .catch(() => setError("Data could not be loaded. Check that the API and database are running."));
  }, []);

  // Latest value per district, for colouring the map.
  const latest = useMemo(() => {
    const out: Record<string, number> = {};
    for (const [code, byYear] of Object.entries(poverty?.districts ?? {})) {
      if (byYear[LATEST] !== undefined) out[code] = byYear[LATEST];
    }
    return out;
  }, [poverty]);

  // Districts from lowest to highest poverty (rank 1 = lowest, as NISR ranks them).
  const ranked = useMemo(() => {
    if (!districts) return [];
    return districts.features
      .map((f) => ({ ...f.properties, value: latest[f.properties.code] }))
      .filter((d) => d.value !== undefined)
      .sort((a, b) => a.value - b.value);
  }, [districts, latest]);

  const current = ranked.find((d) => d.code === selected) ?? null;
  const national = poverty?.national[LATEST];
  const nationalBase = poverty?.national[BASELINE];
  const max = ranked.length ? ranked[ranked.length - 1].value : 100;

  return (
    <div className="layout">
      <header className="topbar">
        <span className="brand">RIDIP</span>
        <span className="tagline">Rwanda Integrated Data Intelligence Platform</span>
      </header>

      <main className="content">
        <section className="map-panel" aria-label="Map of poverty rates by district">
          {error && <p className="notice">{error}</p>}
          {!error && !districts && <p className="notice">Loading data…</p>}
          {districts && poverty && (
            <DistrictMap districts={districts} values={latest} selected={selected} onSelect={setSelected} />
          )}
        </section>

        <aside className="side-panel" ref={panel}>
          <p className="eyebrow">Poverty headcount, EICV7 ({LATEST})</p>

          {current && national !== undefined ? (
            <DistrictProfile
              name={current.name}
              province={current.province}
              value={current.value}
              baseline={poverty?.districts[current.code]?.[BASELINE]}
              national={national}
              rank={ranked.findIndex((d) => d.code === current.code) + 1}
              onClear={() => setSelected(null)}
            />
          ) : (
            <>
              <h1>Rwanda</h1>
              {national !== undefined && nationalBase !== undefined && (
                <>
                  <p className="big-number">{pct(national)}</p>
                  <p>
                    of people lived below the poverty line in {LATEST}, down from {pct(nationalBase)} in {BASELINE}.
                    Select a district to see its profile.
                  </p>
                </>
              )}
            </>
          )}

          <h2>Poverty rate</h2>
          <ul className="legend">
            {LEGEND.map((item) => (
              <li key={item.label}>
                <span className="swatch" style={{ background: item.colour }} />
                {item.label}
              </li>
            ))}
          </ul>

          {ranked.length > 0 && (
            <>
              <h2>All districts, lowest to highest</h2>
              <ol className="ranking">
                {ranked.map((d) => (
                  <li key={d.code}>
                    <button
                      type="button"
                      className={d.code === selected ? "active" : undefined}
                      onClick={() => setSelected(d.code)}
                    >
                      <span className="rank-name">{d.name}</span>
                      <span className="bar-track">
                        <span
                          className="bar"
                          style={{ width: `${(d.value / max) * 100}%`, background: colourFor(d.value) }}
                        />
                      </span>
                      <span className="rank-value">{pct(d.value)}</span>
                    </button>
                  </li>
                ))}
              </ol>
            </>
          )}

          <p className="source">
            Poverty:{" "}
            {poverty?.source_url ? <a href={poverty.source_url}>{poverty.source}</a> : poverty?.source}. 2017 values are
            modelled to the EICV7 method. Boundaries: geoBoundaries (Open Data Rwanda / NISR), CC BY 4.0.
          </p>
        </aside>
      </main>
    </div>
  );
}

type ProfileProps = {
  name: string;
  province: string;
  value: number;
  baseline: number | undefined;
  national: number;
  rank: number;
  onClear: () => void;
};

function DistrictProfile({ name, province, value, baseline, national, rank, onClear }: ProfileProps) {
  const gap = value - national;
  return (
    <>
      <h1>{name}</h1>
      <p className="muted">{province} Province · rank {rank} of 30 (1 = lowest poverty)</p>
      <p className="big-number" style={{ color: value >= 30 ? "#B30000" : "#0B2545" }}>
        {pct(value)}
      </p>
      <dl className="facts">
        <dt>Compared with Rwanda ({pct(national)})</dt>
        <dd>{gap === 0 ? "Same as national" : `${pts(gap)} ${gap > 0 ? "above" : "below"} national`}</dd>
        {baseline !== undefined && (
          <>
            <dt>Change since {BASELINE} ({pct(baseline)})</dt>
            <dd>
              {value < baseline ? "Down" : "Up"} {pts(value - baseline)}
            </dd>
          </>
        )}
      </dl>
      <button type="button" onClick={onClear}>
        Back to Rwanda
      </button>
    </>
  );
}
