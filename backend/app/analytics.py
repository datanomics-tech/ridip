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
2. Statistical comparison with Rwanda. Where NISR publishes standard errors (EICV7), a district is
   flagged as significantly above or below the national value when the difference is larger than
   1.96 times the combined standard error (95% confidence).
3. District typology. k-means clustering (k = 4, deterministic start) groups districts with similar
   profiles across all three tracks, so programmes can be designed for groups of similar districts.
"""
import math
from functools import lru_cache
from statistics import mean, pstdev

from sqlalchemy import text

from app.db import engine
from app.domains import DOMAINS
from app.indicators import load_all

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


@lru_cache(maxsize=1)
def _series() -> dict[str, dict[str, dict[int, tuple[float, float | None]]]]:
    """indicator -> area -> year -> (value, se)"""
    _, values = load_all()
    out: dict = {}
    for v in values:
        out.setdefault(v["indicator_code"], {}).setdefault(v["area_code"], {})[v["year"]] = (v["value"], v["se"])
    return out


def _latest_year(code: str) -> int:
    """Latest year in which every district has a value."""
    series = _series()[code]
    years = set.intersection(*(set(series[d]) for d in districts()))
    return max(years)


@lru_cache(maxsize=1)
def model() -> dict:
    meta, _ = load_all()
    series = _series()
    codes = list(meta)                     # display order from the seed file
    ds = list(districts())

    latest = {c: _latest_year(c) for c in codes}
    value = {c: {d: series[c][d][latest[c]][0] for d in ds} for c in codes}

    # 1. Oriented z-scores within each track's comparison group: positive = worse than average
    z = {}
    for c in codes:
        group = compared(meta[c]["domain"])
        vals = [value[c][d] for d in group]
        mu, sd = mean(vals), pstdev(vals) or 1.0
        sign = 1 if meta[c]["direction"] == "lower" else -1
        z[c] = {d: sign * (value[c][d] - mu) / sd for d in group}

    need, need_rank, rank = {}, {}, {}
    for dom in DOMAINS:
        group = compared(dom)
        dom_codes = [c for c in codes if meta[c]["domain"] == dom]
        raw = {d: mean(z[c][d] for c in dom_codes) for d in group}
        order = sorted(group, key=lambda d: -raw[d])           # most in need first
        need_rank[dom] = {d: i + 1 for i, d in enumerate(order)}
        n = len(group)
        need[dom] = {d: round(100 * (n - need_rank[dom][d]) / (n - 1), 1) for d in group}
    for c in codes:                                             # 1 = best district on this indicator
        group = compared(meta[c]["domain"])
        best_first = sorted(group, key=lambda d: value[c][d], reverse=meta[c]["direction"] == "higher")
        rank[c] = {d: i + 1 for i, d in enumerate(best_first)}

    # 3. k-means typology on the oriented z-scores of all indicators
    vectors = {d: [z[c].get(d, 0.0) for c in codes] for d in ds}   # Kigali: neutral on agriculture
    clusters = _kmeans(vectors, K_CLUSTERS)
    groups = _describe_clusters(clusters, need)

    return dict(codes=codes, latest=latest, value=value, z=z, need=need, need_rank=need_rank,
                rank=rank, clusters=clusters, groups=groups)


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
        for dom in DOMAINS:
            vals = [need[dom][d] for d in members if d in need[dom]]
            profile[dom] = round(mean(vals), 1) if vals else None
        scored = sorted(((v, dom) for dom, v in profile.items() if v is not None), reverse=True)
        high = [DOMAINS[dom]["title"] for v, dom in scored if v >= 60]
        if not high and all(v < 40 for v, _ in scored):
            label = "Lower need: urban, well served"
        elif not high:
            label = f"Moderate need, mostly {DOMAINS[scored[0][1]]['title'].lower()}"
        else:
            label = "Higher need: " + " and ".join(high)
        groups.append(dict(id=i, label=label, need=profile, members=members))
    groups.sort(key=lambda g: -sum(v for v in g["need"].values() if v is not None))
    for n, g in enumerate(groups):
        g["name"] = f"Group {'ABCDEFG'[n]}"
    return groups


def _significance(code: str, area: str, year: int) -> str | None:
    s = _series()[code]
    v, se = s[area][year]
    nat = s.get("rwanda", {}).get(year)
    if se is None or nat is None or nat[1] is None:
        return None
    diff, combined = v - nat[0], math.sqrt(se ** 2 + nat[1] ** 2)
    if abs(diff) <= 1.96 * combined:
        return "not significant"
    return "significantly above" if diff > 0 else "significantly below"


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
    for dom, info in DOMAINS.items():
        items = []
        for c in [c for c in m["codes"] if meta[c]["domain"] == dom]:
            year = m["latest"][c]
            v, se = series[c][code][year]
            nat = series[c].get("rwanda", {}).get(year)
            items.append(dict(
                code=c, name=meta[c]["name"], unit=meta[c]["unit"], direction=meta[c]["direction"],
                source=meta[c]["source"], value_type=meta[c]["value_type"], year=year, value=v, se=se,
                national=nat[0] if nat else None,
                gap=round(v - nat[0], 2) if nat else None,
                rank=m["rank"][c].get(code),          # 1 = best district; None if not compared
                rank_of=len(m["rank"][c]),
                significance=_significance(c, code, year),
                z=round(m["z"][c][code], 2) if code in m["z"][c] else None,
                trend=[{"year": y, "value": series[c][code][y][0]} for y in sorted(series[c][code])],
                national_trend=[{"year": y, "value": series[c]["rwanda"][y][0]} for y in sorted(series[c].get("rwanda", {}))],
            ))
        excluded = code not in m["need"][dom]
        tracks[dom] = dict(**info, need=m["need"][dom].get(code), need_rank=m["need_rank"][dom].get(code),
                           need_of=len(m["need"][dom]), indicators=items,
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
        text_ = f"{t['title']}: {level} need, ranked {t['need_rank']} of {t['need_of']} (1 = most in need)."
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
                    out.append(dict(track=dom, level="trend", indicators=[i["code"]],
                                    text=f"{i['name']} {'improved' if better else 'worsened'} from "
                                         f"{_fmt(first['value'], i['unit'])} ({first['year']}) to "
                                         f"{_fmt(last['value'], i['unit'])} ({last['year']})."))
    return out


def overview() -> dict:
    m, ds = model(), districts()
    tracks = {}
    for dom, info in DOMAINS.items():
        order = sorted(m["need_rank"][dom], key=lambda d: m["need_rank"][dom][d])
        tracks[dom] = dict(**info, need=m["need"][dom], priority=[dict(code=d, name=ds[d]["name"], need=m["need"][dom][d]) for d in order[:5]])
    return dict(tracks=tracks, groups=[{**g, "members": [dict(code=d, name=ds[d]["name"]) for d in g["members"]]} for g in m["groups"]],
                group_of={d: next(g["name"] for g in m["groups"] if d in g["members"]) for d in ds})


def clear_cache() -> None:
    for f in (districts, model, _series, load_all):
        f.cache_clear()
