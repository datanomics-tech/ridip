import { useEffect, useState } from "react";
import { api } from "../api";
import { fmt, fmtGap } from "../format";
import { Link, navigate } from "../router";
import { DOMAIN_ORDER, type Domain, type Profile } from "../types";
import { NEED_MEANING } from "./Place";

const FLAG: Record<string, string> = { above: "Above Rwanda", below: "Below Rwanda", "no clear difference": "No clear difference" };

export default function Report({ place, compare }: { place: string | null; compare: string | null }) {
  const [places, setPlaces] = useState<{ code: string; name: string }[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [other, setOther] = useState<Profile | null>(null);
  const [sections, setSections] = useState<Record<Domain | "insights", boolean>>({
    insights: true, agriculture: true, finance_poverty: true, employment: true, health: true, education: true, transport: true,
  });
  const [format, setFormat] = useState<"pdf" | "csv">("pdf");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api.districts().then((d) => setPlaces(d.features.map((f) => f.properties).sort((x, y) => x.name.localeCompare(y.name)))).catch(() => {});
  }, []);
  useEffect(() => { setReady(false); place ? api.place(place).then(setProfile).catch(() => setProfile(null)) : setProfile(null); }, [place]);
  useEffect(() => { compare ? api.place(compare).then(setOther).catch(() => setOther(null)) : setOther(null); }, [compare]);

  const generate = () => {
    if (!profile) return;
    if (format === "csv") {
      window.location.href = `/api/places/${profile.code}/report.csv`;
      setReady(true);
      return;
    }
    setReady(true);
    setTimeout(() => window.print(), 100);
  };

  const today = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

  return (
    <main className="page">
      <div className="no-print">
        <h1>Report builder</h1>
        <div className="report-form">
          <label className="field">
            <span>District</span>
            <select value={place ?? ""} onChange={(e) => navigate(`/reports/new?place=${e.target.value}${compare ? `&compare=${compare}` : ""}`)}>
              <option value="" disabled>Choose a district</option>
              {places.map((p) => <option key={p.code} value={p.code}>{p.name}</option>)}
            </select>
          </label>
          <fieldset>
            <legend>Sections</legend>
            {(["insights", ...DOMAIN_ORDER] as const).map((s) => (
              <label key={s} className="check">
                <input type="checkbox" checked={sections[s]} onChange={(e) => setSections({ ...sections, [s]: e.target.checked })} />
                {s === "insights" ? "Summary and insights" : profile?.tracks[s].title ?? s}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>Format</legend>
            <label className="check"><input type="radio" checked={format === "pdf"} onChange={() => setFormat("pdf")} /> PDF (print or save as PDF)</label>
            <label className="check"><input type="radio" checked={format === "csv"} onChange={() => setFormat("csv")} /> CSV (spreadsheet)</label>
          </fieldset>
          <button type="button" className="button primary" disabled={!profile} onClick={generate}>Generate report</button>
          {profile && <Link to={`/brief/${profile.code}?domain=finance_poverty`} className="button">Open a sector priority brief instead</Link>}
          {ready && <p className="ready" role="status">Report ready{format === "csv" ? ": the download has started." : ". Use the print dialog to save it as PDF."}</p>}
        </div>
      </div>

      {profile && (
        <article className="report-doc">
          <header>
            <p className="eyebrow">RIDIP district report · {today}</p>
            <h2 className="doc-title">{profile.name} District</h2>
            <p className="muted">{profile.province} · {profile.group.name}: {profile.group.label}</p>
          </header>
          {sections.insights && (
            <section>
              <h2>Summary</h2>
              <div className="table-wrap"><table className="report-table">
                <thead><tr><th>Sector</th><th>Relative need (0–100)</th><th>Rank</th><th>Rank if one indicator left out</th></tr></thead>
                <tbody>
                  {DOMAIN_ORDER.filter((d) => d in profile.tracks).map((d) => {
                    const t = profile.tracks[d];
                    return <tr key={d}><td>{t.title}</td><td>{t.need === null ? "Not ranked" : Math.round(t.need)}</td><td>{t.need_rank === null ? "–" : `${t.need_rank} of ${t.need_of}`}</td><td>{t.rank_range ? `${t.rank_range[0]}–${t.rank_range[1]}${t.rank_stable ? "" : " (sensitive)"}` : "–"}</td></tr>;
                  })}
                </tbody>
              </table></div>
              <p className="meaning small">{NEED_MEANING}</p>
              <ul>{profile.insights.map((i, n) => <li key={n}>{i.text}</li>)}</ul>
            </section>
          )}
          {DOMAIN_ORDER.filter((d) => sections[d] && d in profile.tracks).map((d) => {
            const t = profile.tracks[d];
            return (
              <section key={d}>
                <h2>{t.title}</h2>
                <p className="muted small">{t.nst2}</p>
                <div className="table-wrap"><table className="report-table">
                  <thead>
                    <tr><th>Indicator</th><th>Year</th><th>{profile.name}</th>{other && <th>{other.name}</th>}<th>Rwanda</th><th>Difference</th><th>Approx. 95% flag</th><th>Source</th></tr>
                  </thead>
                  <tbody>
                    {t.indicators.map((i, n) => (
                      <tr key={i.code}>
                        <td>{i.name}</td><td>{i.year}</td><td>{fmt(i.value, i.unit)}</td>
                        {other && <td>{fmt(other.tracks[d].indicators[n].value, i.unit)}</td>}
                        <td>{fmt(i.national, i.unit)}</td><td>{fmtGap(i.gap, i.unit)}</td>
                        <td>{i.difference_flag ? FLAG[i.difference_flag] : "Descriptive"}</td>
                        <td>{i.source}{i.value_type === "derived" ? " (derived)" : ""}</td>
                      </tr>
                    ))}
                  </tbody>
                </table></div>
              </section>
            );
          })}
          <footer className="small muted">
            All figures are published NISR statistics; the source and year are shown on each row, and years differ by survey.
            "Approx. 95% flag" compares the district with Rwanda using published standard errors; "Descriptive" means no
            standard error is published. Need scores are RIDIP calculations of relative need, not causal or predictive
            measures; see ridip.onrender.com/about.
          </footer>
        </article>
      )}
      {!profile && <p className="muted no-print">Choose a district. <Link to="/explore">Or pick one on the map.</Link></p>}
    </main>
  );
}
