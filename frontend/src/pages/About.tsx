import { useEffect, useState } from "react";
import { api } from "../api";
import { DOMAIN_ORDER, type Domain, type DomainInfo, type IndicatorMeta, type Method } from "../types";
import { NEED_MEANING } from "./Place";

export default function About() {
  const [list, setList] = useState<IndicatorMeta[]>([]);
  const [domains, setDomains] = useState<Record<Domain, DomainInfo> | null>(null);
  const [method, setMethod] = useState<Method | null>(null);
  useEffect(() => {
    api.method().then(setMethod).catch(() => {});
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
      <p className="meaning">{NEED_MEANING}</p>
      <ol>
        <li>For each indicator, the latest year with a value for every district is used. Values are standardised (z-scores) and oriented so that a positive score means worse than the average district.</li>
        <li>A sector's score is the equally weighted average over its indicators; the need score is the district's percentile (0 = least relative need, 100 = most).</li>
        <li>The three City of Kigali districts are mainly urban, so they are not ranked on agriculture.</li>
        <li>District groups come from k-means clustering (k = 4, fixed start) on all indicators.</li>
      </ol>
      {method && (
        <>
          <h2>Method safeguards</h2>
          <dl className="method">
            <dt>Weighting</dt><dd>{method.weighting}</dd>
            <dt>Orientation</dt><dd>{method.orientation}</dd>
            <dt>Ties</dt><dd>{method.tie_policy}</dd>
            <dt>Coverage</dt><dd>{method.coverage}</dd>
            <dt>No variation</dt><dd>{method.zero_variance}</dd>
            <dt>Kigali</dt><dd>{method.kigali_rule}</dd>
            <dt>Difference flag</dt><dd>{method.difference_flag}</dd>
            <dt>Stable rank</dt><dd>{method.stable_rule}</dd>
          </dl>
          {method.excluded.length > 0 && (
            <p className="muted small">Not scored: {method.excluded.map((e) => `${e.name} (${e.reason.toLowerCase()})`).join("; ")}.</p>
          )}

          <h2>Sensitivity: does the ranking depend on one indicator?</h2>
          <p>
            Each sector was re-ranked with one indicator left out at a time. The table shows the worst case for the five
            highest-need districts and the share of districts whose rank never moves more than 5 places.
          </p>
          <div className="table-wrap">
            <table className="report-table">
              <thead><tr><th>Sector</th><th>Indicators</th><th>Worst top-5 overlap</th><th>Districts with stable rank</th><th>Most influential indicator</th></tr></thead>
              <tbody>
                {DOMAIN_ORDER.filter((d) => method.sensitivity[d]).map((d) => {
                  const s = method.sensitivity[d];
                  const worst = [...s.scenarios].sort((a, b) => b.max_move - a.max_move)[0];
                  return (
                    <tr key={d}>
                      <td>{domains?.[d]?.title ?? d}</td>
                      <td>{s.indicators}</td>
                      <td>{s.min_top5_overlap} of 5</td>
                      <td>{Math.round(s.share_of_districts_stable * 100)}%</td>
                      <td>{worst ? `${worst.left_out_name} (up to ${worst.max_move} places)` : "–"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="muted small">Read lower-stability sectors (health, agriculture) as broad groupings rather than exact positions.</p>

          <h2>Verified national targets</h2>
          <p>Only targets confirmed in an official NST2 document are shown as numbers. They are national targets, not district targets.</p>
          <ul>
            {Object.entries(method.targets).map(([code, t]) => (
              <li key={code}>
                {list.find((i) => i.code === code)?.name ?? code}: {t.baseline} → {t.value} by {t.year} ({t.label}).{" "}
                <a href={t.source_url}>{t.source}</a>
              </li>
            ))}
          </ul>

          <h2>Source years</h2>
          <p className="muted small">
            Sectors combine surveys from different years, so the profile shows each figure's year:{" "}
            {DOMAIN_ORDER.filter((d) => method.source_years[d]).map((d) => `${domains?.[d]?.title ?? d} ${method.source_years[d].join("/")}`).join(" · ")}.
          </p>

          <h2>Known limitations</h2>
          <ul>
            <li>Need scores are relative: a low score does not mean a district has no problem.</li>
            <li>The scores describe the data; they do not show causes or predict the effect of a programme.</li>
            <li>Only EICV7 indicators carry standard errors; other figures are descriptive.</li>
            <li>Poverty change uses the 2017 figures re-estimated by NISR for comparison.</li>
            <li>District boundaries and statistics are 2024–2025; sector boundaries are not covered.</li>
          </ul>
        </>
      )}
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
