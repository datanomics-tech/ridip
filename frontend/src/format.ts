export function fmt(value: number | null | undefined, unit: string): string {
  if (value === null || value === undefined) return "–";
  if (unit.startsWith("%")) return `${value.toFixed(1)}%`;
  if (unit.includes("Frw")) return `${Math.round(value).toLocaleString("en-US")} Frw`;
  if (unit.includes("hectare")) return `${Math.round(value).toLocaleString("en-US")} kg/ha`;
  return value.toLocaleString("en-US", { maximumFractionDigits: 1 });
}

/** Gap to Rwanda in the indicator's own terms: "4.2 points above" or "1,200 Frw below". */
export function fmtGap(gap: number | null, unit: string): string {
  if (gap === null) return "";
  if (Math.abs(gap) < 0.05) return "same as Rwanda";
  const size = unit.startsWith("%") ? `${Math.abs(gap).toFixed(1)} points` : fmt(Math.abs(gap), unit);
  return `${size} ${gap > 0 ? "above" : "below"} Rwanda`;
}

/** True when the gap to Rwanda is in the good direction for this indicator. */
export function isBetter(gap: number | null, direction: "higher" | "lower"): boolean | null {
  if (gap === null || Math.abs(gap) < 0.05) return null;
  return direction === "higher" ? gap > 0 : gap < 0;
}
