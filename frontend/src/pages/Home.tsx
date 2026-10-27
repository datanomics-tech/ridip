import { useEffect, useState } from "react";
import { api } from "../api";
import { Link } from "../router";
import { DOMAIN_ORDER, type IndicatorData, type Overview } from "../types";
import TrackCard from "../TrackCard";
import { HEADLINES } from "../tracks";

export default function Home() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [headline, setHeadline] = useState<Record<string, IndicatorData>>({});
  const [error, setError] = useState(false);

  useEffect(() => {
    api.overview().then(setOverview).catch(() => setError(true));
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
          explains where need is greatest and why.
        </p>
        <div className="hero-actions">
          <Link to="/explore" className="button primary">Explore the map</Link>
          <Link to="/place/nyagatare" className="button">See a district profile</Link>
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
      </section>
    </main>
  );
}
