import { useEffect, useState } from "react";
import { api } from "../api";
import { fmt } from "../format";
import { Link, navigate } from "../router";
import { DOMAIN_ORDER, type Profile } from "../types";

export default function Compare({ a, b }: { a: string | null; b: string | null }) {
  const [places, setPlaces] = useState<{ code: string; name: string }[]>([]);
  const [pa, setPa] = useState<Profile | null>(null);
  const [pb, setPb] = useState<Profile | null>(null);

  useEffect(() => {
    api.districts().then((d) => setPlaces(d.features.map((f) => f.properties).sort((x, y) => x.name.localeCompare(y.name)))).catch(() => {});
  }, []);
  useEffect(() => { a ? api.place(a).then(setPa).catch(() => setPa(null)) : setPa(null); }, [a]);
  useEffect(() => { b ? api.place(b).then(setPb).catch(() => setPb(null)) : setPb(null); }, [b]);

  const pick = (key: "a" | "b", value: string) => {
    const p = new URLSearchParams({ ...(a ? { a } : {}), ...(b ? { b } : {}) });
    p.set(key, value);
    navigate(`/compare?${p.toString()}`);
  };

  return (
    <main className="page">
      <h1>Compare two districts</h1>
      <div className="row compare-pick">
        {(["a", "b"] as const).map((k) => (
          <label key={k} className="field">
            <span>District {k.toUpperCase()}</span>
            <select value={(k === "a" ? a : b) ?? ""} onChange={(e) => pick(k, e.target.value)}>
              <option value="" disabled>Choose a district</option>
              {places.map((p) => <option key={p.code} value={p.code}>{p.name}</option>)}
            </select>
          </label>
        ))}
      </div>

      {pa && pb ? (
        <div className="table-wrap">
          <table className="compare">
            <thead>
              <tr><th>Indicator</th><th><Link to={`/place/${pa.code}`}>{pa.name}</Link></th><th><Link to={`/place/${pb.code}`}>{pb.name}</Link></th><th>Rwanda</th></tr>
            </thead>
            {DOMAIN_ORDER.map((d) => {
              const ta = pa.tracks[d], tb = pb.tracks[d];
              return (
                <tbody key={d}>
                  <tr className="section"><th colSpan={4}>{ta.title}: need score {ta.need === null ? "–" : Math.round(ta.need)} vs {tb.need === null ? "–" : Math.round(tb.need)}</th></tr>
                  {ta.indicators.map((ia, n) => {
                    const ib = tb.indicators[n];
                    const aBetter = ia.direction === "higher" ? ia.value > ib.value : ia.value < ib.value;
                    const tie = ia.value === ib.value;
                    return (
                      <tr key={ia.code}>
                        <td>{ia.name} <span className="muted small">({ia.year})</span></td>
                        <td className={!tie && aBetter ? "better" : undefined}>{fmt(ia.value, ia.unit)}</td>
                        <td className={!tie && !aBetter ? "better" : undefined}>{fmt(ib.value, ib.unit)}</td>
                        <td className="muted">{fmt(ia.national, ia.unit)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              );
            })}
          </table>
          <p className="muted small">Highlighted: the better of the two districts on each indicator.</p>
          <Link to={`/reports/new?place=${pa.code}&compare=${pb.code}`} className="button primary">Generate a report</Link>
        </div>
      ) : (
        <p className="muted">Choose two districts to see them side by side.</p>
      )}
    </main>
  );
}
