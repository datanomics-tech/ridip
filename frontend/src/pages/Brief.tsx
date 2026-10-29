import { useEffect, useState } from "react";
import { api } from "../api";
import { fmt } from "../format";
import { Link, navigate } from "../router";
import { DOMAIN_ORDER, type Brief as BriefData, type Domain, type DomainInfo, type Evidence } from "../types";
import { NEED_MEANING } from "./Place";

const FLAG: Record<string, string> = {
  above: "Above Rwanda (approx. 95% check)",
  below: "Below Rwanda (approx. 95% check)",
  "no clear difference": "No clear difference (approx. 95% check)",
};

function toCsv(b: BriefData): string {
  const rows = [["district", "sector", "rule_id", "indicator", "value", "rwanda", "unit", "year", "difference", "value_type", "source", "source_url"]];
  for (const s of b.statements)
    for (const e of s.evidence)
      rows.push([b.district, b.sector, s.rule_id, e.name, String(e.value), String(e.national ?? ""), e.unit, String(e.year),
        e.difference_flag ?? "no standard error published", e.value_type, e.source, e.source_url ?? ""]);
  return rows.map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
}

export default function Brief({ code, domain }: { code: string; domain: string | null }) {
  const [domains, setDomains] = useState<Record<Domain, DomainInfo> | null>(null);
  const [brief, setBrief] = useState<BriefData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const dom = (DOMAIN_ORDER as string[]).includes(domain ?? "") ? (domain as Domain) : "finance_poverty";

  useEffect(() => { api.domains().then(setDomains).catch(() => {}); }, []);
  useEffect(() => {
    setBrief(null);
    setError(null);
    api.brief(code, dom).then(setBrief).catch(() => setError("This brief could not be loaded. Try again in a minute."));
  }, [code, dom]);

  const download = () => {
    if (!brief) return;
    const url = URL.createObjectURL(new Blob([toCsv(brief)], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `ridip-brief-${brief.code}-${dom}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const evidence: Evidence[] = brief ? brief.statements.flatMap((s) => s.evidence).filter((e, n, all) => all.findIndex((x) => x.code === e.code) === n) : [];
  const today = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

  return (
    <main className="page">
      <div className="no-print row brief-controls">
        <Link to={`/place/${code}`}>← Back to the district profile</Link>
        <label className="field inline">
          <span>Sector</span>
          <select value={dom} onChange={(e) => navigate(`/brief/${code}?domain=${e.target.value}`)}>
            {DOMAIN_ORDER.map((d) => <option key={d} value={d}>{domains?.[d]?.title ?? d}</option>)}
          </select>
        </label>
        <button type="button" onClick={() => window.print()} disabled={!brief}>Print / save as PDF</button>
        <button type="button" onClick={download} disabled={!brief}>Download CSV</button>
      </div>

      {error && <p className="notice">{error}</p>}
      {!error && !brief && <p className="notice">Preparing the brief…</p>}

      {brief && (
        <article className="report-doc brief">
          <header>
            <p className="eyebrow">RIDIP evidence-to-action brief · {today} · rules v{brief.version}</p>
            <h1>{brief.district}: {brief.sector}</h1>
            <p className="muted">{brief.province} Province · {brief.track}</p>
            <p className="purpose"><strong>Purpose:</strong> {brief.purpose}</p>
          </header>

          <section>
            <h2>Relative need</h2>
            {brief.need_rank !== null ? (
              <p>
                Need score <strong>{Math.round(brief.need ?? 0)}/100</strong>, rank {brief.need_rank} of {brief.need_of} ({brief.level}).
                {brief.rank_range && ` Rank range if one indicator is left out: ${brief.rank_range[0]}–${brief.rank_range[1]}.`}
              </p>
            ) : <p>Not ranked on this sector.</p>}
            <p className="meaning small">{NEED_MEANING}</p>
          </section>

          <section>
            <h2>Observed evidence</h2>
            <ul className="statements">
              {brief.statements.map((s, n) => (
                <li key={n}><span className="rule">{s.rule_id}</span> {s.text}</li>
              ))}
            </ul>
            {evidence.length > 0 && (
              <div className="table-wrap">
                <table className="report-table">
                  <thead><tr><th>Indicator</th><th>{brief.district}</th><th>Rwanda</th><th>Year</th><th>Difference</th><th>Source</th></tr></thead>
                  <tbody>
                    {evidence.map((e, n) => (
                      <tr key={n}>
                        <td>{e.name}{e.value_type === "derived" ? " (derived)" : ""}</td>
                        <td>{fmt(e.value, e.unit)}</td>
                        <td>{fmt(e.national, e.unit)}</td>
                        <td>{e.year}</td>
                        <td>{e.difference_flag ? FLAG[e.difference_flag] : "Descriptive (no standard error published)"}</td>
                        <td>{e.source_url ? <a href={e.source_url}>{e.source}</a> : e.source}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section>
            <h2>Planning question</h2>
            <p>{brief.planning_question}</p>
            <p className="muted small">{brief.nst2}</p>
          </section>

          <section>
            <h2>Possible next steps (analytical, before any decision)</h2>
            <ol>{brief.follow_up.map((f, n) => <li key={n}>{f}</li>)}</ol>
            {brief.group.peers.length > 0 && (
              <p>Districts with a similar overall profile ({brief.group.name}): {brief.group.peers.join(", ")}.</p>
            )}
          </section>

          <section>
            <h2>Caveats</h2>
            <ul>{brief.caveats.map((c, n) => <li key={n}>{c}</li>)}</ul>
          </section>

          <footer className="small muted">
            Generated by RIDIP from published NISR statistics with fixed rules (no AI model, no prediction). Method:
            ridip.onrender.com/about. Each statement lists its rule id and can be recomputed from the same data.
          </footer>
        </article>
      )}
    </main>
  );
}
