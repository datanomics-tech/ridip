// Five poverty classes, light (low) to dark (high).
export const BREAKS = [10, 20, 30, 40];
export const CLASS_COLOURS = ["#FEF0D9", "#FDCC8A", "#FC8D59", "#E34A33", "#B30000"];
export const NO_DATA = "#C8CDD3";

export function colourFor(value: number | undefined): string {
  if (value === undefined) return NO_DATA;
  const index = BREAKS.findIndex((limit) => value < limit);
  return CLASS_COLOURS[index === -1 ? BREAKS.length : index];
}

export const LEGEND = CLASS_COLOURS.map((colour, i) => ({
  colour,
  label:
    i === 0 ? `Below ${BREAKS[0]}%`
    : i === BREAKS.length ? `${BREAKS[i - 1]}% or more`
    : `${BREAKS[i - 1]}–${BREAKS[i]}%`,
}));
