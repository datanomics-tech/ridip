import { useEffect, useState } from "react";
import { api } from "../api";
import { needColour } from "../colours";
import { fmt, fmtGap, isBetter } from "../format";
import { Link, navigate } from "../router";
import Sparkline from "../Sparkline";
import { DOMAIN_ORDER, type Domain, type Profile, type ProfileIndicator, type ProfileTrack } from "../types";

type Tab = "overview" | Domain;

export const NEED_MEANING =
  "Need scores show relative need among districts on published indicators. They are not a measure of absolute deprivation, a probability, or a causal effect, and not an official NISR index.";

/** The sector in which the district ranks most in need (for the default priority brief). */
function topDomain(profile: Profile): Domain {
  const ranked = DOMAIN_ORDER.filter((d) => d in profile.tracks && profile.tracks[d].need !== null);
  return ranked.sort((a, b) => (profile.tracks[b].need ?? 0) - (profile.tracks[a].need ?? 0))[0] ?? "finance_poverty";
}

function RankLine({ t }: { t: ProfileTrack }) {
  if (t.need_rank === null) return null;
  return (
    <span className="muted small">
      Rank {t.need_rank} of {t.need_of} (1 = most in need)
      {t.rank_range && (
        <> · {t.rank_stable ? "stable" : "sensitive"}: {t.rank_range[0]}–{t.rank_range[1]} if one indicator is left out</>
      )}
    </span>
  );
}

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
          <Link to={`/compare?a=${code}`} className="button">Compare</Link>
          <Link to={`/reports/new?place=${code}`} className="button">Generate report</Link>
          <Link to={`/brief/${code}?domain=${active === "overview" ? topDomain(profile) : active}`} className="button primary">Priority brief</Link>
        </div>
      </header>

      <div className="tabs" role="tablist">
        {(["overview", ...DOMAIN_ORDER.filter((d) => d in profile.tracks)] as Tab[]).map((t) => (
          <button key={t} role="tab" aria-selected={active === t} className={active === t ? "active" : undefined} onClick={() => go(t)}>
            {t === "overview" ? "Overview" : profile.tracks[t].title}
          </button>
        ))}
      </div>

      {active === "overview" ? <Overview profile={profile} onOpen={go} /> : <TrackView track={profile.tracks[active]} code={code} domain={active} />}
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
                  <RankLine t={t} />
                  <span className="muted small">Data: {t.years.join(", ")}</span>
                </>
              )}
            </button>
          );
        })}
      </section>
      <p className="meaning small">{NEED_MEANING} Indicators come from surveys of 2024 and 2025, so sectors are not a synchronised snapshot.</p>

      <section className="insights">
        <h2>Insights for {profile.name}</h2>
        <p className="muted small">Generated by fixed, documented rules from the indicators (no AI model); each is traceable to its source table.</p>
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

function TrackView({ track, code, domain }: { track: ProfileTrack; code: string; domain: Domain }) {
  return (
    <>
      <section className="track-intro">
        <p><strong>{track.question}</strong></p>
        <p className="muted">{track.nst2}</p>
        {track.need !== null ? (
          <p>
            Need score <strong>{Math.round(track.need)}/100</strong>. <RankLine t={track} />
          </p>
        ) : (
          <p className="muted">{track.note}</p>
        )}
        <p className="meaning small">{NEED_MEANING}</p>
        <Link to={`/brief/${code}?domain=${domain}`} className="button primary">Priority brief for {track.title.toLowerCase()}</Link>
      </section>
      <section className="indicator-grid">
        {track.indicators.map((i) => <IndicatorCard key={i.code} i={i} />)}
      </section>
    </>
  );
}

export function FlagLine({ i }: { i: ProfileIndicator }) {
  if (i.national === null) return null;
  if (i.difference_flag === null)
    return <p className="tag neutral">No uncertainty estimate published: the difference is descriptive</p>;
  if (i.difference_flag === "no clear difference")
    return <p className="tag">Approximate 95% check: no clear difference from Rwanda</p>;
  return <p className="tag">Approximate 95% check: {i.difference_flag} Rwanda</p>;
}

function IndicatorCard({ i }: { i: ProfileIndicator }) {
  const better = isBetter(i.gap, i.direction);
  return (
    <article className="indicator-card">
      <h3>{i.name}</h3>
      <p className="big-number">{fmt(i.value, i.unit)}</p>
      <p className="muted small">{i.unit}, {i.year}{i.se !== null ? ` · ±${(1.96 * i.se).toFixed(1)} (approx. 95% interval)` : ""}</p>
      {i.national !== null && (
        <p className={better === null ? "" : better ? "good" : "bad"}>
          {fmtGap(i.gap, i.unit)} <span className="muted">({fmt(i.national, i.unit)}, {i.year})</span>
        </p>
      )}
      <FlagLine i={i} />
      {i.target && (
        <p className="target small">
          {i.target.label}: {fmt(i.target.value, i.unit)} by {i.target.year} ({i.target.level} target, not a district target).
          This district is {fmtGap(i.target.distance, i.unit).replace("Rwanda", "the target")}.
        </p>
      )}
      {i.rank !== null && <p className="muted small">Rank {i.rank} of {i.rank_of} (1 = best; ties ordered alphabetically)</p>}
      {!i.scored && <p className="tag neutral">Not used in the score: {i.excluded_reason}</p>}
      <Sparkline district={i.trend} national={i.national_trend} label={`${i.name} over time`} />
      {i.code === "poverty_rate" && <p className="muted small">2017 value modelled by NISR on the EICV7 method.</p>}
      <p className="source">
        {i.source_url ? <a href={i.source_url}>{i.source}</a> : i.source} · {i.year} ·{" "}
        {i.value_type === "derived" ? "derived (calculated by RIDIP)" : "official figure"}
        {i.note ? ` · ${i.note}` : ""}
      </p>
      <Link to={`/explore?i=${i.code}`} className="small">See on the map →</Link>
    </article>
  );
}
