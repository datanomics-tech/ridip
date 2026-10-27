import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import DistrictMap from "../DistrictMap";
import { needScale } from "../colours";
import { fmt, fmtGap, isBetter } from "../format";
import { Link, navigate } from "../router";
import { DOMAIN_ORDER, type DistrictCollection, type Domain, type DomainInfo, type IndicatorData, type IndicatorMeta } from "../types";

type Props = { domain?: Domain; indicator?: string | null; year?: string | null; place?: string | null; basePath: string };

export default function Explore({ domain, indicator, year, place, basePath }: Props) {
  const [districts, setDistricts] = useState<DistrictCollection | null>(null);
  const [list, setList] = useState<IndicatorMeta[]>([]);
  const [domains, setDomains] = useState<Record<Domain, DomainInfo> | null>(null);
  const [data, setData] = useState<IndicatorData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([api.districts(), api.indicators(), api.domains()])
      .then(([d, l, dm]) => {
        setDistricts(d);
        setList(l);
        setDomains(dm);
      })
      .catch(() => setError(true));
  }, []);

  const options = domain ? list.filter((i) => i.domain === domain) : list;
  const code = indicator && options.some((o) => o.code === indicator) ? indicator : options[0]?.code;

  useEffect(() => {
    if (code) api.indicator(code).then(setData).catch(() => setError(true));
  }, [code]);

  const ready = data && data.code === code ? data : null;
  // Years in which every district has a value
  const years = ready ? ready.years.filter((y) => Object.values(ready.districts).every((v) => v[String(y)] !== undefined)) : [];
  const yr = year && years.includes(Number(year)) ? year : String(years[years.length - 1] ?? "");

  const values = useMemo(() => {
    const out: Record<string, number> = {};
    if (ready) for (const [d, v] of Object.entries(ready.districts)) if (v[yr] !== undefined) out[d] = v[yr];
    return out;
  }, [ready, yr]);

  const names = useMemo(() => {
    const out: Record<string, { name: string; province: string }> = {};
    districts?.features.forEach((f) => (out[f.properties.code] = f.properties));
    return out;
  }, [districts]);

  const unit = ready?.unit ?? "%";
  const scale = useMemo(
    () => (ready ? needScale(Object.values(values), ready.direction, (v) => fmt(v, unit)) : null),
    [values, ready, unit],
  );
  const ranked = Object.entries(values).sort((a, b) => (ready?.direction === "higher" ? b[1] - a[1] : a[1] - b[1]));
  const national = ready?.national[yr];
  const selected = place && values[place] !== undefined ? place : null;

  const set = (changes: Record<string, string | null>) => {
    const p = new URLSearchParams({ ...(code ? { i: code } : {}), ...(yr ? { y: yr } : {}), ...(selected ? { place: selected } : {}) });
    for (const [k, v] of Object.entries(changes)) v === null ? p.delete(k) : p.set(k, v);
    navigate(`${basePath}?${p.toString()}`);
  };

  const info = domain ? domains?.[domain] : undefined;

  return (
    <main className="explore">
      <section className="map-panel" aria-label="District map">
        {error && <p className="notice">Data could not be loaded. The server may be waking up: try again in a minute.</p>}
        {!error && (!districts || !ready) && <p className="notice">Loading…</p>}
        {districts && ready && scale && (
          <DistrictMap
            districts={districts}
            version={`${code}-${yr}`}
            colour={(c) => scale.colour(values[c])}
            tooltip={(c, n) => `<strong>${n}</strong><br>${fmt(values[c], unit)}`}
            selected={selected}
            onSelect={(c) => set({ place: c })}
          />
        )}
      </section>

      <aside className="side-panel">
        {info ? (
          <>
            <p className="eyebrow">{info.track}</p>
            <h1>{info.title}</h1>
            <p className="muted">{info.question}</p>
          </>
        ) : (
          <>
            <p className="eyebrow">Geographic explorer</p>
            <h1>Explore all indicators</h1>
          </>
        )}

        <label className="field">
          <span>Indicator</span>
          <select value={code ?? ""} onChange={(e) => set({ i: e.target.value, y: null })}>
            {DOMAIN_ORDER.filter((d) => !domain || d === domain).map((d) => (
              <optgroup key={d} label={domains?.[d]?.title ?? d}>
                {options.filter((o) => o.domain === d).map((o) => (
                  <option key={o.code} value={o.code}>{o.name}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
        {years.length > 1 && (
          <label className="field">
            <span>Year</span>
            <select value={yr} onChange={(e) => set({ y: e.target.value })}>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </label>
        )}

        {ready && (
          <p className="source">
            {ready.unit}, {yr}. Rwanda: <strong>{fmt(national, unit)}</strong>.{" "}
            {ready.direction === "higher" ? "Higher is better." : "Lower is better."} Source: {ready.source}.
          </p>
        )}

        {selected && ready && (
          <div className="quick-card">
            <p className="eyebrow">{names[selected]?.province}</p>
            <h2>{names[selected]?.name}</h2>
            <p className="big-number">{fmt(values[selected], unit)}</p>
            {national !== undefined && (
              <p className={isBetter(values[selected] - national, ready.direction) ? "good" : "bad"}>
                {fmtGap(values[selected] - national, unit)}
              </p>
            )}
            <p className="muted">Rank {ranked.findIndex(([d]) => d === selected) + 1} of 30 (1 = best)</p>
            <div className="row">
              <Link to={`/place/${selected}`} className="button primary">Open profile</Link>
              <button type="button" onClick={() => set({ place: null })}>Clear</button>
            </div>
          </div>
        )}

        {scale && (
          <>
            <h2>Map colours</h2>
            <ul className="legend">
              {scale.legend.map((l) => (
                <li key={l.label}><span className="swatch" style={{ background: l.colour }} />{l.label}</li>
              ))}
            </ul>
            <p className="muted small">Light = better off, dark red = most in need (fifths of the 30 districts).</p>
          </>
        )}

        {ranked.length > 0 && scale && (
          <>
            <h2>All districts, best to worst</h2>
            <ol className="ranking">
              {ranked.map(([d, v]) => (
                <li key={d}>
                  <button type="button" className={d === selected ? "active" : undefined} onClick={() => set({ place: d })}>
                    <span className="rank-name">{names[d]?.name ?? d}</span>
                    <span className="bar-track">
                      <span className="bar" style={{ width: `${(v / Math.max(...Object.values(values))) * 100}%`, background: scale.colour(v) }} />
                    </span>
                    <span className="rank-value">{fmt(v, unit)}</span>
                  </button>
                </li>
              ))}
            </ol>
          </>
        )}
        {ready?.note && <p className="source">Note: {ready.note}</p>}
      </aside>
    </main>
  );
}
