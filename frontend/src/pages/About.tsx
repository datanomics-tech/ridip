import { useEffect, useState } from "react";
import { api } from "../api";
import { DOMAIN_ORDER, type Domain, type DomainInfo, type IndicatorMeta } from "../types";

export default function About() {
  const [list, setList] = useState<IndicatorMeta[]>([]);
  const [domains, setDomains] = useState<Record<Domain, DomainInfo> | null>(null);
  useEffect(() => {
    api.indicators().then(setList).catch(() => {});
    api.domains().then(setDomains).catch(() => {});
  }, []);
  return (
    <main className="page about">
      <h1>Methodology and sources</h1>
      <p>
        RIDIP uses only published, aggregated statistics from the National Institute of Statistics of Rwanda (NISR).
        No personal or household-level data is stored.
      </p>
      <h2>Need scores</h2>
      <ol>
        <li>For each indicator, the latest district values are standardised (z-scores) and oriented so that a positive score means worse than the average district.</li>
        <li>A track's score is the average over its indicators; the need score is the district's percentile (0 = least need, 100 = most).</li>
        <li>The three City of Kigali districts are mainly urban, so they are not ranked on agriculture.</li>
        <li>Where NISR publishes standard errors (EICV7), a district is called significantly above or below Rwanda when the difference exceeds 1.96 combined standard errors (95% confidence).</li>
        <li>District groups come from k-means clustering (k = 4) on all indicators.</li>
      </ol>
      <h2>Indicators</h2>
      {DOMAIN_ORDER.map((d) => (
        <section key={d}>
          <h3>{domains?.[d]?.track}</h3>
          <p className="muted">{domains?.[d]?.nst2}</p>
          <div className="table-wrap">
            <table className="report-table">
              <thead><tr><th>Indicator</th><th>Unit</th><th>Years</th><th>Source</th></tr></thead>
              <tbody>
                {list.filter((i) => i.domain === d).map((i) => (
                  <tr key={i.code}>
                    <td>{i.name}{i.note ? <div className="muted small">{i.note}</div> : null}</td>
                    <td>{i.unit}</td>
                    <td>{i.years.join(", ")}</td>
                    <td>{i.source_url ? <a href={i.source_url}>{i.source}</a> : i.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
      <p><a className="button" href="/api/data.csv">Download all data (CSV)</a> <a className="button" href="/docs">API documentation</a></p>
      <p className="muted small">Boundaries: geoBoundaries (Open Data Rwanda / NISR), CC BY 4.0. Base map © OpenStreetMap contributors.</p>
    </main>
  );
}
