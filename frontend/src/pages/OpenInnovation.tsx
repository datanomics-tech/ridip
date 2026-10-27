import { useEffect, useState } from "react";
import { api } from "../api";
import TrackCard from "../TrackCard";
import { OPEN_INNOVATION, type IndicatorData, type Overview } from "../types";
import { HEADLINES } from "../tracks";

export default function OpenInnovation() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [headline, setHeadline] = useState<Record<string, IndicatorData>>({});
  useEffect(() => {
    api.overview().then(setOverview).catch(() => {});
    OPEN_INNOVATION.flatMap((d) => HEADLINES[d]).forEach((code) =>
      api.indicator(code).then((d) => setHeadline((h) => ({ ...h, [code]: d }))).catch(() => {}),
    );
  }, []);
  return (
    <main className="page">
      <p className="eyebrow">Track 3: Open Innovation</p>
      <h1>National priorities under NST2 and Vision 2050</h1>
      <p className="muted">
        Four sectors that shape whether districts can turn growth into jobs and wellbeing: employment, health,
        education and transport.
      </p>
      <section className="track-grid two">
        {OPEN_INNOVATION.map((d) => <TrackCard key={d} domain={d} overview={overview} headline={headline} />)}
      </section>
    </main>
  );
}
