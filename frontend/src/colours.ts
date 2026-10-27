// Map colours always mean "how much need": light = better-off districts, dark red = most in need.
// Classes are quintiles of the 30 district values, so every map uses the full colour range.
export const NEED_COLOURS = ["#FEF0D9", "#FDCC8A", "#FC8D59", "#E34A33", "#B30000"];
export const NO_DATA = "#C8CDD3";

export type Scale = { colour: (v: number | undefined) => string; legend: { colour: string; label: string }[] };

export function needScale(
  values: number[],
  direction: "higher" | "lower",
  label: (v: number) => string,
): Scale {
  const sorted = [...values].sort((a, b) => a - b);
  const q = (p: number) => sorted[Math.min(sorted.length - 1, Math.floor(p * sorted.length))];
  const breaks = [q(0.2), q(0.4), q(0.6), q(0.8)];
  const classOf = (v: number) => {
    const i = breaks.findIndex((b) => v < b);
    return i === -1 ? 4 : i;
  };
  // For "higher is better" indicators, low values are the most in need.
  const colourIndex = (cls: number) => (direction === "lower" ? cls : 4 - cls);
  const colour = (v: number | undefined) => (v === undefined ? NO_DATA : NEED_COLOURS[colourIndex(classOf(v))]);
  const edges = [sorted[0], ...breaks, sorted[sorted.length - 1]];
  const legend = edges.slice(0, 5).map((lo, i) => ({
    colour: NEED_COLOURS[colourIndex(i)],
    label: `${label(lo)} – ${label(edges[i + 1])}`,
  }));
  if (direction === "higher") legend.reverse();
  return { colour, legend };
}

export function needColour(score: number | null | undefined): string {
  if (score === null || score === undefined) return NO_DATA;
  return NEED_COLOURS[Math.min(4, Math.floor(score / 20))];
}
