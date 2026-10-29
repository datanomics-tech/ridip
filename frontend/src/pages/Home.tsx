import { useEffect, useState } from "react";
import { api } from "../api";
import { Link, navigate } from "../router";
import { NEED_MEANING } from "./Place";
import { DOMAIN_ORDER, type IndicatorData, type Overview } from "../types";
import TrackCard from "../TrackCard";
import { HEADLINES } from "../tracks";

export default function Home() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [headline, setHeadline] = useState<Record<string, IndicatorData>>({});
  const [error, setError] = useState(false);
  const [places, setPlaces] = useState<{ code: string; name: string }[]>([]);

  useEffect(() => {
    api.overview().then(setOverview).catch(() => setError(true));
    api.districts().then((d) => setPlaces(d.features.map((f) => f.properties).sort((x, y) => x.name.localeCompare(y.name)))).catch(() => {});
    Object.values(HEADLINES).flat().forEach((code) =>
      api.indicator(code).then((d) => setHeadline((h) => ({ ...h, [code]: d }))).catch(() => {}),
    );
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <h1>Where should Rwanda act first?</h1>
        <p>
          RIDIP brings together 39 official NISR indicators on agriculture, poverty and financial inclusion,
          employment, health, education and transport for all 30 districts, compares each district with Rwanda, and
          shows where relative need is greatest and which indicators drive it.
        </p>
        <div className="hero-actions">
          <label className="field start">
            <span>Start with a district</span>
            <select defaultValue="" onChange={(e) => e.target.value && navigate(`/place/${e.target.value}`)} aria-label="Start with a district">
              <option value="" disabled>{places.length ? "Choose one of the 30 districts" : "Loading districts…"}</option>
              {places.map((p) => <option key={p.code} value={p.code}>{p.name}</option>)}
            </select>
          </label>
          <Link to="/explore" className="button">Or explore the map</Link>
        </div>
      </section>

      {error && <p className="notice">Data could not be loaded. The server may be waking up: try again in a minute.</p>}

      <section className="track-grid" aria-label="Tracks">
        {DOMAIN_ORDER.map((dom) => (
          <TrackCard key={dom} domain={dom} overview={overview} headline={headline} />
        ))}
      </section>

      {overview && (
        <section className="groups">
          <h2>Districts with similar profiles</h2>
          <p className="muted">
            Districts grouped by k-means clustering on all 39 indicators. Programmes that work in one district are
            most likely to transfer to others in the same group.
          </p>
          <div className="group-grid">
            {overview.groups.map((g) => (
              <article key={g.id} className="group-card">
                <h3>{g.name}: {g.label}</h3>
                <p className="chips">
                  {g.members.map((m) => <Link key={m.code} to={`/place/${m.code}`} className="chip">{m.name}</Link>)}
                </p>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="how">
        <h2>How to read the need scores</h2>
        <p>
          Each sector's <strong>need score</strong> (0–100) ranks a district against the others on that sector's
          indicators: 100 is the most in need. Scores are built from published NISR figures only, and every district
          profile lists the indicators that drive its score. <Link to="/about">Methodology and sources</Link>
        </p>
        <p className="meaning">{NEED_MEANING}</p>
        <p className="muted small">
          Source years differ by sector (EICV7 2023/24, FinScope 2024, LFS 2025, SAS 2025 and others); each figure shows
          its own year and source. A "rank sensitive" tag means the rank moves more than 5 places if any one indicator is left out.
        </p>
      </section>
    </main>
  );
}
