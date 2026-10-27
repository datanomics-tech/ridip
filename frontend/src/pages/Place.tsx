import { useEffect, useState } from "react";
import { api } from "../api";
import { needColour } from "../colours";
import { fmt, fmtGap, isBetter } from "../format";
import { Link, navigate } from "../router";
import Sparkline from "../Sparkline";
import { DOMAIN_ORDER, type Domain, type Profile, type ProfileIndicator, type ProfileTrack } from "../types";

type Tab = "overview" | Domain;

export default function Place({ code, tab }: { code: string; tab: string }) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProfile(null);
    api.place(code).then(setProfile).catch((e: Error) =>
      setError(e.message.includes("404") ? "We could not find that district." : "Data could not be loaded. Try again in a minute."),
    );
  }, [code]);

  const active: Tab = (DOMAIN_ORDER as string[]).includes(tab) && profile && tab in profile.tracks ? (tab as Domain) : "overview";
  const go = (t: Tab) => navigate(`/place/${code}${t === "overview" ? "" : `?tab=${t}`}`);

  if (error) return <main className="page"><p className="notice">{error}</p></main>;
  if (!profile) return <main className="page"><p className="notice">Loading district profile…</p></main>;

  return (
    <main className="page place">
      <nav className="crumbs" aria-label="Breadcrumb">
        <Link to="/">Rwanda</Link> / <span>{profile.province}</span> / <strong>{profile.name}</strong>
      </nav>
      <header className="place-head">
        <div>
          <h1>{profile.name}</h1>
          <p className="muted">
            {profile.province} · {profile.group.name}: {profile.group.label}
          </p>
        </div>
        <div className="row">
          <Link to={`/compare?a=${code}`} className="button">Compare with another district</Link>
          <Link to={`/reports/new?place=${code}`} className="button primary">Generate report</Link>
        </div>
      </header>

      <div className="tabs" role="tablist">
        {(["overview", ...DOMAIN_ORDER.filter((d) => d in profile.tracks)] as Tab[]).map((t) => (
          <button key={t} role="tab" aria-selected={active === t} className={active === t ? "active" : undefined} onClick={() => go(t)}>
            {t === "overview" ? "Overview" : profile.tracks[t].title}
          </button>
        ))}
      </div>

      {active === "overview" ? <Overview profile={profile} onOpen={go} /> : <TrackView track={profile.tracks[active]} />}
    </main>
  );
}

function Overview({ profile, onOpen }: { profile: Profile; onOpen: (t: Tab) => void }) {
  return (
    <>
      <section className="need-grid">
        {DOMAIN_ORDER.filter((d) => d in profile.tracks).map((d) => {
          const t = profile.tracks[d];
          return (
            <button key={d} type="button" className="need-card" onClick={() => onOpen(d)}>
              <span className="eyebrow">{t.track}</span>
              <span className="need-title">{t.title}</span>
              {t.need === null ? (
                <span className="muted">{t.note}</span>
              ) : (
                <>
                  <span className="need-score" style={{ color: t.need >= 60 ? "#B30000" : "#0B2545" }}>
                    {Math.round(t.need)}<small>/100 need</small>
                  </span>
                  <span className="need-bar"><span style={{ width: `${t.need}%`, background: needColour(t.need) }} /></span>
                  <span className="muted">Rank {t.need_rank} of {t.need_of} (1 = most in need)</span>
                </>
              )}
            </button>
          );
        })}
      </section>

      <section className="insights">
        <h2>Insights for {profile.name}</h2>
        <p className="muted small">Generated automatically from the indicators, each traceable to its source table.</p>
        <ul>
          {profile.insights.map((i, n) => (
            <li key={n} className={`insight insight-${i.level}`}>{i.text}</li>
          ))}
        </ul>
        {profile.group.peers.length > 0 && (
          <p>
            <strong>Similar districts ({profile.group.name}):</strong> {profile.group.peers.join(", ")}.
          </p>
        )}
      </section>
    </>
  );
}

function TrackView({ track }: { track: ProfileTrack }) {
  return (
    <>
      <section className="track-intro">
        <p><strong>{track.question}</strong></p>
        <p className="muted">{track.nst2}</p>
        {track.need !== null ? (
          <p>
            Need score <strong>{Math.round(track.need)}/100</strong>, rank {track.need_rank} of {track.need_of} (1 = most in need).
          </p>
        ) : (
          <p className="muted">{track.note}</p>
        )}
      </section>
      <section className="indicator-grid">
        {track.indicators.map((i) => <IndicatorCard key={i.code} i={i} />)}
      </section>
    </>
  );
}

function IndicatorCard({ i }: { i: ProfileIndicator }) {
  const better = isBetter(i.gap, i.direction);
  return (
    <article className="indicator-card">
      <h3>{i.name}</h3>
      <p className="big-number">{fmt(i.value, i.unit)}</p>
      <p className="muted small">{i.unit}, {i.year}{i.se !== null ? ` · ±${(1.96 * i.se).toFixed(1)} (95% CI)` : ""}</p>
      {i.national !== null && (
        <p className={better === null ? "" : better ? "good" : "bad"}>
          {fmtGap(i.gap, i.unit)} <span className="muted">({fmt(i.national, i.unit)})</span>
        </p>
      )}
      {i.significance && <p className="tag">{i.significance === "not significant" ? "Not significantly different from Rwanda" : `Statistically ${i.significance} Rwanda`}</p>}
      {i.rank !== null && <p className="muted small">Rank {i.rank} of {i.rank_of} (1 = best)</p>}
      <Sparkline district={i.trend} national={i.national_trend} label={`${i.name} over time`} />
      <p className="source">{i.source}{i.value_type === "derived" ? " (calculated by RIDIP)" : ""}</p>
      <Link to={`/explore?i=${i.code}`} className="small">See on the map →</Link>
    </article>
  );
}
