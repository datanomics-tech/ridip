import type { Point } from "./types";

/** A small line chart: the district (solid) against Rwanda (dashed). */
export default function Sparkline({ district, national, label }: { district: Point[]; national: Point[]; label: string }) {
  const all = [...district, ...national];
  if (district.length < 2) return null;
  const years = all.map((p) => p.year);
  const values = all.map((p) => p.value);
  const [x0, x1] = [Math.min(...years), Math.max(...years)];
  const [y0, y1] = [Math.min(...values), Math.max(...values)];
  const W = 220, H = 64, P = 6;
  const x = (yr: number) => P + ((yr - x0) / (x1 - x0 || 1)) * (W - 2 * P);
  const y = (v: number) => H - P - ((v - y0) / (y1 - y0 || 1)) * (H - 2 * P);
  const path = (pts: Point[]) => pts.map((p, i) => `${i ? "L" : "M"}${x(p.year).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const inRange = national.filter((p) => p.year >= x0 && p.year <= x1);
  return (
    <figure className="spark">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
        {inRange.length > 1 && <path d={path(inRange)} className="spark-national" />}
        <path d={path(district)} className="spark-district" />
        {district.map((p) => (
          <circle key={p.year} cx={x(p.year)} cy={y(p.value)} r={2.2} className="spark-dot" />
        ))}
      </svg>
      <figcaption>
        <span>{x0}</span>
        <span className="spark-key">
          <i className="k-district" /> district <i className="k-national" /> Rwanda
        </span>
        <span>{x1}</span>
      </figcaption>
    </figure>
  );
}
