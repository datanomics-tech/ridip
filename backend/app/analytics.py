"""Explainable analytics for RIDIP.

Three things are computed from the official indicator values, all in plain Python so every step
can be explained:

1. Need index (per district and track). Each indicator's latest district values are standardised
   (z-scores across the districts compared) and oriented so that a positive score always means "worse
   than the average district". A track's raw score is the mean of its indicators; the need index is the
   district's percentile among the districts compared (0 = least need, 100 = most). The indicators that
   push a district's score up are reported as its main drivers, so the score is never a black box.
   The three City of Kigali districts are mainly urban, so they are left out of the agriculture
   comparison (their agriculture values are still shown).
2. Approximate 95% difference flag. Where NISR publishes standard errors (EICV7), a district is
   flagged as above or below Rwanda when |district - Rwanda| > 1.96 x sqrt(SE_district^2 + SE_Rwanda^2).
   This ignores the covariance between a district and the national total (the district is part of
   it) and the full survey design, so it is an approximation, not a formal significance test.
   Where no standard error is published, differences are descriptive only.

Safeguards (tested in tests/test_method.py):
- Coverage: an indicator is scored only on its latest year with values for every district compared;
  otherwise it is excluded and the reason is reported by /api/method.
- Zero variance: an indicator with the same value in every district has no z-score and is excluded
  from the sector score (never divided by zero).
- Ties: districts with equal values or scores are ordered alphabetically, so ranks are repeatable.
- Sensitivity: each sector's ranking is recomputed leaving out one indicator at a time; the top-5
  overlap and each district's rank range are reported, and unstable ranks are flagged.
3. District typology. k-means clustering (k = 4, deterministic start) groups districts with similar
   profiles across all six sectors, so programmes can be designed for groups of similar districts.
"""
import math
from functools import lru_cache
from statistics import mean, pstdev

from sqlalchemy import text

from app.db import engine
from app.domains import DOMAINS, TARGETS
from app.indicators import clear_cache as clear_indicator_cache, load_all

K_CLUSTERS = 4
URBAN_PROVINCE = "City of Kigali"   # excluded from the agriculture comparison


def compared(domain: str) -> list[str]:
    """Districts compared within a track."""
    ds = districts()
    return [d for d in ds if not (domain == "agriculture" and ds[d]["province"] == URBAN_PROVINCE)]


@lru_cache(maxsize=1)
def districts() -> dict[str, dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT code, name, province FROM districts ORDER BY name")).mappings()
        return {r["code"]: dict(r) for r in rows}


_memo: dict = {}


def _per_version(name: str, data: tuple, build):
    """Cache a result for one version of the loaded data (a new load gives a new tuple object)."""
    key = (name, id(data))
    if key not in _memo:
        for k in [k for k in _memo if k[0] == name]:
            del _memo[k]
        _memo[key] = build(data)
    return _memo[key]


def _series() -> dict[str, dict[str, dict[int, tuple[float, float | None]]]]:
    """indicator -> area -> year -> (value, se)"""
    return _per_version("series", load_all(), _build_series)


def _build_series(data: tuple) -> dict:
    _, values = data
    out: dict = {}
    for v in values:
        out.setdefault(v["indicator_code"], {}).setdefault(v["area_code"], {})[v["year"]] = (v["value"], v["se"])
    return out


def _latest_full_year(series: dict, group: list[str]) -> int | None:
    """Latest year in which every district in the comparison group has a value (None if there is none)."""
    year_sets = [set(series.get(d, {})) for d in group]
    common = set.intersection(*year_sets) if year_sets else set()
    return max(common) if common else None


def _ranking(scores: dict[str, float], names: dict[str, str], descending: bool) -> list[str]:
    """Stable order: by score, ties broken alphabetically by district name."""
    return sorted(scores, key=lambda d: ((-scores[d] if descending else scores[d]), names[d]))


def model() -> dict:
    return _per_version("model", load_all(), _build_model)


def domains_present() -> list[str]:
    """Sectors that have at least one indicator loaded, in display order."""
    meta, _ = load_all()
    loaded = {m["domain"] for m in meta.values()}
    return [d for d in DOMAINS if d in loaded]


def _build_model(data: tuple) -> dict:
    meta, _ = data
    series = _per_version("series", data, _build_series)
    ds = districts()
    names = {d: ds[d]["name"] for d in ds}
    excluded: dict[str, str] = {}

    # Coverage: the latest year with values for every district compared
    latest, value = {}, {}
    for c in meta:
        group = compared(meta[c]["domain"])
        year = _latest_full_year(series.get(c, {}), group)
        if year is None:
            excluded[c] = "No year with values for every district compared"
            continue
        latest[c] = year
        value[c] = {d: series[c][d][year][0] for d in ds if year in series[c].get(d, {})}
    codes = [c for c in meta if c in latest]          # display order from the seed file

    # 1. Oriented z-scores within each sector's comparison group: positive = worse than average
    z: dict[str, dict[str, float]] = {}
    for c in codes:
        group = compared(meta[c]["domain"])
        vals = [value[c][d] for d in group]
        mu, sd = mean(vals), pstdev(vals)
        if sd == 0:
            excluded[c] = "Same value in every district (no variation to compare)"
            z[c] = {}
            continue
        sign = 1 if meta[c]["direction"] == "lower" else -1
        z[c] = {d: sign * (value[c][d] - mu) / sd for d in group}
    scored = [c for c in codes if c not in excluded]

    need, need_rank, raw_scores, sector_codes = {}, {}, {}, {}
    for dom in domains_present():
        group = compared(dom)
        dom_codes = [c for c in scored if meta[c]["domain"] == dom]
        if not dom_codes:
            continue
        sector_codes[dom] = dom_codes
        raw = {d: mean(z[c][d] for c in dom_codes) for d in group}
        raw_scores[dom] = raw
        order = _ranking(raw, names, descending=True)           # most in need first
        need_rank[dom] = {d: i + 1 for i, d in enumerate(order)}
        n = len(group)
        need[dom] = {d: round(100 * (n - need_rank[dom][d]) / (n - 1), 1) for d in group}

    rank = {}                                                   # 1 = best district on this indicator
    for c in codes:
        group = compared(meta[c]["domain"])
        best_first = _ranking({d: value[c][d] for d in group}, names, descending=meta[c]["direction"] == "higher")
        rank[c] = {d: i + 1 for i, d in enumerate(best_first)}

    sensitivity = _sensitivity(need_rank, sector_codes, z, names)

    # 3. k-means typology on the oriented z-scores of all scored indicators
    vectors = {d: [z[c].get(d, 0.0) for c in scored] for d in ds}   # Kigali: neutral on agriculture
    clusters = _kmeans(vectors, K_CLUSTERS)
    groups = _describe_clusters(clusters, need)

    return dict(codes=codes, scored=scored, excluded=excluded, latest=latest, value=value, z=z, need=need,
                need_rank=need_rank, rank=rank, sector_codes=sector_codes, sensitivity=sensitivity,
                clusters=clusters, groups=groups)


STABLE_MOVE = 5   # a district whose rank moves by more than this when one indicator is left out is "sensitive"


def _sensitivity(need_rank: dict, sector_codes: dict, z: dict, names: dict) -> dict:
    """Leave-one-indicator-out: recompute each sector's ranking without each indicator in turn."""
    out = {}
    for dom, codes in sector_codes.items():
        base = need_rank[dom]
        base_top5 = {d for d, r in base.items() if r <= 5}
        ranges = {d: [r, r] for d, r in base.items()}
        scenarios = []
        if len(codes) >= 2:
            for left_out in codes:
                keep = [c for c in codes if c != left_out]
                raw = {d: mean(z[c][d] for c in keep) for d in base}
                order = _ranking(raw, names, descending=True)
                new = {d: i + 1 for i, d in enumerate(order)}
                for d, r in new.items():
                    ranges[d][0] = min(ranges[d][0], r)
                    ranges[d][1] = max(ranges[d][1], r)
                moves = {d: abs(new[d] - base[d]) for d in base}
                top5 = {d for d, r in new.items() if r <= 5}
                scenarios.append(dict(left_out=left_out, top5_overlap=len(top5 & base_top5),
                                      max_move=max(moves.values()),
                                      mean_move=round(mean(moves.values()), 2)))
        out[dom] = dict(
            scenarios=scenarios,
            min_top5_overlap=min((s["top5_overlap"] for s in scenarios), default=5),
            rank_range={d: tuple(v) for d, v in ranges.items()},
            stable_share=round(sum(1 for v in ranges.values() if v[1] - v[0] <= STABLE_MOVE) / len(ranges), 2),
        )
    return out


def _kmeans(vectors: dict[str, list[float]], k: int, iterations: int = 50) -> dict[str, int]:
    """Plain k-means with a deterministic farthest-point start, so results are reproducible."""
    def dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    names = sorted(vectors)
    start = max(names, key=lambda d: sum(vectors[d]))            # district with the highest overall need
    centres = [vectors[start]]
    while len(centres) < k:
        far = max(names, key=lambda d: min(dist(vectors[d], c) for c in centres))
        centres.append(vectors[far])
    assign: dict[str, int] = {}
    for _ in range(iterations):
        new = {d: min(range(k), key=lambda i: dist(vectors[d], centres[i])) for d in names}
        if new == assign:
            break
        assign = new
        for i in range(k):
            members = [vectors[d] for d in names if assign[d] == i]
            if members:
                centres[i] = [mean(col) for col in zip(*members)]
    return assign


def _describe_clusters(clusters: dict[str, int], need: dict) -> list[dict]:
    """Name each cluster by the tracks where its districts' average need is highest."""
    groups = []
    for i in sorted(set(clusters.values())):
        members = sorted(d for d, c in clusters.items() if c == i)
        profile = {}
        for dom in need:
            vals = [need[dom][d] for d in members if d in need[dom]]
            profile[dom] = round(mean(vals), 1) if vals else None
        scored = sorted(((v, dom) for dom, v in profile.items() if v is not None), reverse=True)
        high = [DOMAINS[dom]["title"] for v, dom in scored if v >= 60]
        low = [dom for v, dom in scored if v < 40]
        if len(low) >= len(scored) - 1:
            top_v, top = scored[0]
            label = "Lower need overall" + (f", except {DOMAINS[top]['title'].lower()}" if top_v >= 50 else "")
        elif high:
            label = "Higher need: " + ", ".join(high)
        else:
            label = f"Moderate need, highest in {DOMAINS[scored[0][1]]['title'].lower()}"
        groups.append(dict(id=i, label=label, need=profile, members=members))
    groups.sort(key=lambda g: -sum(v for v in g["need"].values() if v is not None))
    for n, g in enumerate(groups):
        g["name"] = f"Group {'ABCDEFG'[n]}"
    return groups


def _difference_flag(code: str, area: str, year: int) -> str | None:
    """Approximate 95% difference flag (see module docstring). None when no standard error is published."""
    s = _series()[code]
    v, se = s[area][year]
    nat = s.get("rwanda", {}).get(year)
    if se is None or nat is None or nat[1] is None:
        return None
    diff, combined = v - nat[0], math.sqrt(se ** 2 + nat[1] ** 2)
    if abs(diff) <= 1.96 * combined:
        return "no clear difference"
    return "above" if diff > 0 else "below"


def _target(code: str, value: float) -> dict | None:
    t = TARGETS.get(code)
    if not t:
        return None
    return {**t, "distance": round(value - t["value"], 2)}


def _fmt(v: float, unit: str) -> str:
    if unit.startswith("%"):
        return f"{v:.1f}%"
    if "Frw" in unit:
        return f"{v:,.0f} Frw"
    if "hectare" in unit:
        return f"{v:,.0f} kg/ha"
    return f"{v:,.1f}"


def place_profile(code: str) -> dict | None:
    ds = districts()
    if code not in ds:
        return None
    meta, _ = load_all()
    m, series = model(), _series()
    tracks = {}
    for dom in domains_present():
        info = DOMAINS[dom]
        items = []
        for c in [c for c in m["codes"] if meta[c]["domain"] == dom]:
            year = m["latest"][c]
            v, se = series[c][code][year]
            nat = series[c].get("rwanda", {}).get(year)
            items.append(dict(
                code=c, name=meta[c]["name"], unit=meta[c]["unit"], direction=meta[c]["direction"],
                source=meta[c]["source"], source_url=meta[c]["source_url"], note=meta[c]["note"],
                value_type=meta[c]["value_type"], year=year, value=v, se=se,
                scored=c in m["scored"], excluded_reason=m["excluded"].get(c),
                national=nat[0] if nat else None,
                gap=round(v - nat[0], 2) if nat else None,
                rank=m["rank"][c].get(code),          # 1 = best district; None if not compared
                rank_of=len(m["rank"][c]),
                difference_flag=_difference_flag(c, code, year),
                target=_target(c, v),
                z=round(m["z"][c][code], 2) if code in m["z"][c] else None,
                trend=[{"year": y, "value": series[c][code][y][0]} for y in sorted(series[c][code])],
                national_trend=[{"year": y, "value": series[c]["rwanda"][y][0]} for y in sorted(series[c].get("rwanda", {}))],
            ))
        excluded = code not in m["need"].get(dom, {})
        sens = m["sensitivity"].get(dom, {})
        rng = sens.get("rank_range", {}).get(code)
        years = sorted({i["year"] for i in items})
        tracks[dom] = dict(**info, need=m["need"].get(dom, {}).get(code), need_rank=m["need_rank"].get(dom, {}).get(code),
                           need_of=len(m["need"].get(dom, {})), indicators=items, years=years,
                           rank_range=list(rng) if rng else None,
                           rank_stable=(rng[1] - rng[0] <= STABLE_MOVE) if rng else None,
                           note="Mainly urban district: not ranked on agriculture." if excluded else None)
    group = next(g for g in m["groups"] if code in g["members"])
    return dict(**ds[code], tracks=tracks, insights=_insights(ds[code]["name"], tracks),
                group=dict(name=group["name"], label=group["label"],
                           peers=[ds[d]["name"] for d in group["members"] if d != code]))


def _insights(name: str, tracks: dict) -> list[dict]:
    """Plain-language findings, each traceable to the indicators behind it."""
    out = []
    for dom, t in tracks.items():
        if t["need_rank"] is None:
            out.append(dict(track=dom, level="info", indicators=[], text=f"{t['title']}: {t['note']}"))
            continue
        drivers = sorted((i for i in t["indicators"] if i["z"] is not None and i["z"] > 0.5), key=lambda i: -i["z"])[:2]
        strengths = sorted((i for i in t["indicators"] if i["z"] is not None and i["z"] < -0.5), key=lambda i: i["z"])[:1]
        third = t["need_of"] / 3
        level = "high" if t["need_rank"] <= third else "moderate" if t["need_rank"] <= 2 * third else "low"
        text_ = f"{t['title']}: {level} relative need, ranked {t['need_rank']} of {t['need_of']} (1 = most in need)."
        reasons = [f"{i['name']} {_fmt(i['value'], i['unit'])} vs {_fmt(i['national'], i['unit'])} nationally"
                   for i in drivers if i["national"] is not None]
        if reasons:
            text_ += " Main drivers: " + "; ".join(reasons) + "."
        if strengths and strengths[0]["national"] is not None:
            s = strengths[0]
            text_ += f" Strength: {s['name']} {_fmt(s['value'], s['unit'])} vs {_fmt(s['national'], s['unit'])}."
        out.append(dict(track=dom, level=level, text=text_, indicators=[i["code"] for i in drivers + strengths]))
        for i in t["indicators"]:
            if len(i["trend"]) >= 2:
                first, last = i["trend"][0], i["trend"][-1]
                change = last["value"] - first["value"]
                if i["unit"].startswith("%") and abs(change) >= 5:
                    better = (change < 0) == (i["direction"] == "lower")
                    caveat = " (2017 value modelled by NISR on the EICV7 method)" if i["code"] == "poverty_rate" else ""
                    out.append(dict(track=dom, level="trend", indicators=[i["code"]],
                                    text=f"{i['name']} {'improved' if better else 'worsened'} from "
                                         f"{_fmt(first['value'], i['unit'])} ({first['year']}) to "
                                         f"{_fmt(last['value'], i['unit'])} ({last['year']}){caveat}."))
    return out


def overview() -> dict:
    m, ds = model(), districts()
    tracks = {}
    for dom in domains_present():
        info = DOMAINS[dom]
        if dom not in m["need_rank"]:
            continue
        order = sorted(m["need_rank"][dom], key=lambda d: m["need_rank"][dom][d])
        rr = m["sensitivity"][dom]["rank_range"]
        tracks[dom] = dict(**info, need=m["need"][dom],
                           priority=[dict(code=d, name=ds[d]["name"], need=m["need"][dom][d],
                                          rank_stable=rr[d][1] - rr[d][0] <= STABLE_MOVE) for d in order[:5]])
    return dict(tracks=tracks, groups=[{**g, "members": [dict(code=d, name=ds[d]["name"]) for d in g["members"]]} for g in m["groups"]],
                group_of={d: next(g["name"] for g in m["groups"] if d in g["members"]) for d in ds})


def clear_cache() -> None:
    districts.cache_clear()
    _memo.clear()
    clear_indicator_cache()


# ---------------------------------------------------------------------------------------------
# District priority brief: deterministic rules, no prediction, no causal claims.
# Each statement carries a rule id and the evidence (indicator, value, benchmark, year, source)
# it is computed from, so it can be recomputed from the same seed data.
# ---------------------------------------------------------------------------------------------
BRIEF_VERSION = "1.0"
DRIVER_Z = 0.5

FOLLOW_UP = [
    "Triangulate with administrative and sector data (ministry, district and sub-district statistics).",
    "Consult district technical staff and practitioners on the barriers behind the indicators flagged.",
    "Assess feasibility, cost and equity of options before any allocation decision.",
]


def _evidence(i: dict) -> dict:
    return {k: i[k] for k in ("code", "name", "value", "national", "gap", "unit", "year", "source", "source_url",
                              "difference_flag", "value_type")}


def priority_brief(code: str, domain: str) -> dict | None:
    profile = place_profile(code)
    if profile is None or domain not in profile["tracks"]:
        return None
    t = profile["tracks"][domain]
    name, sector = profile["name"], t["title"]
    statements, caveats = [], []

    if t["need_rank"] is None:
        statements.append(dict(rule_id="R0-not-ranked", evidence=[],
                               text=f"{name}: {t['note']} No priority statement is made for {sector.lower()}."))
        level = "not ranked"
    else:
        n, r = t["need_of"], t["need_rank"]
        quintile = math.ceil(r / (n / 5))
        level = {1: "highest-need fifth", 2: "second fifth", 3: "middle fifth", 4: "fourth fifth", 5: "lowest-need fifth"}[quintile]
        statements.append(dict(rule_id="R1-relative-need", evidence=[],
                               text=f"{name} ranks {r} of {n} districts on {sector.lower()} need (1 = most in need), "
                                    f"in the {level}. This is a relative ranking among districts, not an absolute "
                                    "measure of deprivation."))
        drivers = sorted((i for i in t["indicators"] if i["z"] is not None and i["z"] > DRIVER_Z),
                         key=lambda i: -i["z"])[:3]
        for i in drivers:
            gap_txt = ""
            if i["national"] is not None:
                worse = "worse" if (i["gap"] > 0) == (i["direction"] == "lower") else "better"
                gap_txt = (f" against {_fmt(i['national'], i['unit'])} for Rwanda ({i['year']}), "
                           f"{_gap_words(i['gap'], i['unit'])} ({worse})")
            if i["difference_flag"] in ("above", "below"):
                unc = " The difference passes an approximate 95% check against published standard errors."
            elif i["difference_flag"] == "no clear difference":
                unc = " Within published survey uncertainty, the difference from Rwanda is not clear."
            else:
                unc = " No standard error is published, so the difference is descriptive."
            statements.append(dict(rule_id="R2-driver", evidence=[_evidence(i)],
                                   text=f"{i['name']} is {_fmt(i['value'], i['unit'])}{gap_txt}. It is among the "
                                        f"indicators that raise the need rating (oriented z = {i['z']:+.2f}).{unc}"))
        for i in t["indicators"]:
            if i.get("target"):
                tg = i["target"]
                statements.append(dict(rule_id="R4-target", evidence=[_evidence(i)],
                                       text=f"{tg['label']}: {i['name'].lower()} {_fmt(tg['value'], i['unit'])} by "
                                            f"{tg['year']} (baseline {_fmt(tg['baseline'], i['unit'])}). {name} is at "
                                            f"{_fmt(i['value'], i['unit'])}, {_gap_words(tg['distance'], i['unit'])} the "
                                            "target value. This is a national target, not one assigned to the district."))
        if not drivers:
            statements.append(dict(rule_id="R5-insufficient", evidence=[],
                                   text="No single indicator stands out as a driver here, so no area for "
                                        "investigation is suggested from this data alone."))
        if t["rank_stable"] is False:
            lo, hi = t["rank_range"]
            caveats.append(f"Rank sensitivity: leaving out any one indicator moves {name} between rank {lo} and "
                           f"{hi}. Treat the exact rank with care.")

    years = ", ".join(str(y) for y in t["years"])
    caveats += [
        f"Source years in this sector: {years}. Indicators from different surveys are not a synchronised snapshot.",
        "District figures are survey estimates with sampling error; check published intervals before deciding.",
        "Comparisons are descriptive. They do not show causes, and they do not predict the effect of any programme.",
    ]
    return dict(version=BRIEF_VERSION, district=name, code=code, province=profile["province"], sector=sector,
                track=t["track"], purpose="Screening and discussion, not a final allocation decision.",
                need=t["need"], need_rank=t["need_rank"], need_of=t["need_of"], level=level,
                rank_range=t["rank_range"], statements=statements,
                planning_question=f"{t['decision']} Should {name} be considered, given the evidence below?",
                follow_up=FOLLOW_UP, caveats=caveats, nst2=t["nst2"],
                group=profile["group"])


def _gap_words(gap: float, unit: str) -> str:
    if abs(gap) < 0.05:
        return "the same as"
    size = f"{abs(gap):.1f} percentage points" if unit.startswith("%") else _fmt(abs(gap), unit)
    return f"{size} {'above' if gap > 0 else 'below'}"


def method_info() -> dict:
    """What the scoring does, what it excluded, and how stable the rankings are."""
    m, ds = model(), districts()
    meta, _ = load_all()
    sens = {}
    for dom, sv in m["sensitivity"].items():
        sens[dom] = dict(
            indicators=len(m["sector_codes"][dom]),
            min_top5_overlap=sv["min_top5_overlap"],
            share_of_districts_stable=sv["stable_share"],
            scenarios=[{**s, "left_out_name": meta[s["left_out"]]["name"]} for s in sv["scenarios"]],
        )
    years = {}
    for c in m["codes"]:
        years.setdefault(meta[c]["domain"], set()).add(m["latest"][c])
    return dict(
        weighting="Equal weights within each sector (an analytical choice, not an official NISR index).",
        orientation="Indicators where lower is better keep their sign; where higher is better they are reversed, "
                    "so a positive z-score always means more need.",
        tie_policy="Districts with equal values or equal scores are ordered alphabetically by name.",
        coverage="Each indicator uses its latest year with values for every district compared.",
        zero_variance="Indicators with no variation across districts are excluded from scores.",
        kigali_rule="The three City of Kigali districts are not ranked on agriculture.",
        difference_flag="Approximate 95% flag: |district - Rwanda| > 1.96 x sqrt(SE_d^2 + SE_RW^2). Ignores "
                        "district-national covariance and the full survey design. Only where standard errors are published.",
        stable_rule=f"A district's rank is called stable when leaving out any one indicator moves it by {STABLE_MOVE} places or fewer.",
        excluded=[dict(code=c, name=meta[c]["name"], reason=r) for c, r in m["excluded"].items()],
        source_years={d: sorted(v) for d, v in years.items()},
        sensitivity=sens,
        targets=TARGETS,
    )
