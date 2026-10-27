import { useEffect, useState } from "react";
import { api } from "../api";
import { fmt } from "../format";
import { needColour } from "../colours";
import { Link } from "../router";
import { DOMAIN_ORDER, type Domain, type IndicatorData, type Overview } from "../types";

export const TRACK_PATH: Record<Domain, string> = {
  finance_poverty: "/finance-poverty",
  agriculture: "/agriculture",
  employment: "/open-innovation/employment",
};

const HEADLINES: Record<Domain, string[]> = {
  finance_poverty: ["poverty_rate", "fin_excluded"],
  agriculture: ["ag_improved_seeds", "ag_irrigated_land"],
  employment: ["emp_unemployment", "emp_youth_neet"],
};

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
          RIDIP brings together official NISR statistics on poverty and financial inclusion, agriculture and employment
          for all 30 districts, compares each district with Rwanda, and explains where need is greatest and why.
        </p>
        <div className="hero-actions">
          <Link to="/explore" className="button primary">Explore the map</Link>
          <Link to="/place/nyagatare" className="button">See a district profile</Link>
        </div>
      </section>

      {error && <p className="notice">Data could not be loaded. The server may be waking up: try again in a minute.</p>}

      <section className="track-grid" aria-label="Tracks">
        {DOMAIN_ORDER.map((dom) => {
          const t = overview?.tracks[dom];
          return (
            <article key={dom} className={`track-card track-${dom}`}>
              <p className="eyebrow">{t?.track}</p>
              <h2>{t?.title ?? "…"}</h2>
              <p className="muted">{t?.question}</p>
              <div className="headline-row">
                {HEADLINES[dom].map((code) => {
                  const d = headline[code];
                  const year = d ? Object.keys(d.national).sort().pop() : undefined;
                  return (
                    <div key={code} className="headline">
                      <strong>{d && year ? fmt(d.national[year], d.unit) : "…"}</strong>
                      <span>{d?.name}{year ? ` (${year})` : ""}</span>
                    </div>
                  );
                })}
              </div>
              <h3>Priority districts</h3>
              <ol className="priority">
                {t?.priority.map((p) => (
                  <li key={p.code}>
                    <Link to={`/place/${p.code}`}>{p.name}</Link>
                    <span className="need-pill" style={{ background: needColour(p.need), color: p.need >= 60 ? "#fff" : "#3b0d0d" }} title="Need score (0-100)">{Math.round(p.need)}</span>
                  </li>
                ))}
              </ol>
              <Link to={TRACK_PATH[dom]} className="button">Open {t?.title.toLowerCase() ?? "track"}</Link>
            </article>
          );
        })}
      </section>

      {overview && (
        <section className="groups">
          <h2>Districts with similar profiles</h2>
          <p className="muted">
            Districts grouped by k-means clustering on all 21 indicators. Programmes that work in one district are
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
          Each track's <strong>need score</strong> (0–100) ranks a district against the others on that track's
          indicators: 100 is the most in need. Scores are built from published NISR figures only, and every district
          profile lists the indicators that drive its score. <Link to="/about">Methodology and sources</Link>
        </p>
      </section>
    </main>
  );
}
