import { fmt } from "./format";
import { needColour } from "./colours";
import { Link } from "./router";
import { HEADLINES, TRACK_PATH } from "./tracks";
import type { Domain, IndicatorData, Overview } from "./types";

type Props = { domain: Domain; overview: Overview | null; headline: Record<string, IndicatorData> };

/** One sector: its question, two national headline figures and the five districts most in need. */
export default function TrackCard({ domain, overview, headline }: Props) {
  const t = overview?.tracks[domain];
  return (
    <article className={`track-card track-${domain}`}>
      <p className="eyebrow">{t?.track}</p>
      <h2>{t?.title ?? "…"}</h2>
      <p className="muted">{t?.question}</p>
      <div className="headline-row">
        {HEADLINES[domain].map((code) => {
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
            <span className="need-pill" style={{ background: needColour(p.need), color: p.need >= 60 ? "#fff" : "#3b0d0d" }} title="Need score (0-100)">
              {Math.round(p.need)}
            </span>
          </li>
        ))}
      </ol>
      <Link to={TRACK_PATH[domain]} className="button">Open {t?.title.toLowerCase() ?? "sector"}</Link>
    </article>
  );
}
