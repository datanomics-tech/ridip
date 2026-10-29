# District Priority & Intervention Advisor (priority brief)

The priority brief turns a district's figures for one sector into a short, printable evidence note for planners. It is **rules-based**: no language model, no prediction and no causal claims. Each statement carries a rule id and the evidence it is built from, so anyone can recompute it from the same data.

- **In the app:** district profile → *Priority brief*, or `/brief/{district}?domain={sector}` (e.g. `/brief/gicumbi?domain=health`). It can be printed or saved as PDF, or downloaded as CSV.
- **API:** `GET /api/places/{code}/priority-brief?domain={sector}`. Unknown district or sector returns 404.
- **Code:** `priority_brief()` in `backend/app/analytics.py`. Rules version: `1.0`.
- **Tests:** `test_priority_brief_is_deterministic_traceable_and_not_causal`, `test_priority_brief_unknown_inputs_404`, `test_kigali_not_ranked_on_agriculture` in `backend/tests/test_method.py`.

Sectors: `agriculture`, `finance_poverty`, `employment`, `health`, `education`, `transport`.

## Purpose and limits

> Screening and discussion, not a final allocation decision.

The brief says *where to look first and why*; it does not say what to fund. It never uses causal words ("because", "caused by", "will reduce"). Every brief ends with the same analytical follow-up steps and caveats.

## Rules

| Rule id | When it fires | What it says |
| --- | --- | --- |
| `R0-not-ranked` | The district is not ranked on the sector (the three Kigali districts on agriculture). | States why, and makes no priority statement. |
| `R1-relative-need` | The district is ranked. | Rank *r* of *n* and its fifth (quintile = ⌈r ÷ (n/5)⌉: highest-need fifth … lowest-need fifth). Says the ranking is relative, not absolute. |
| `R2-driver` | Up to 3 indicators with oriented z-score **> 0.5**, highest first. | Value vs Rwanda, year, gap and whether that is worse or better; the z-score; and the uncertainty wording (below). Evidence: the indicator with source and URL. |
| `R4-target` | An indicator in the sector has a **verified** national target (currently stunting: 15% by 2029, MINECOFIN NST2 deck). | The target, baseline and the district's distance to it, stating it is a national target, not a district one. |
| `R5-insufficient` | The district is ranked but no indicator has z > 0.5. | "No single indicator stands out as a driver, so no area for investigation is suggested from this data alone." |

Uncertainty wording in `R2-driver`:

| Data available | Wording |
| --- | --- |
| Standard errors published and the approximate 95% flag says above/below | "The difference passes an approximate 95% check against published standard errors." |
| Standard errors published, flag says no clear difference | "Within published survey uncertainty, the difference from Rwanda is not clear." |
| No standard errors | "No standard error is published, so the difference is descriptive." |

Caveats always included: rank sensitivity (when leaving out one indicator moves the rank more than 5 places, with the range), the sector's source years, sampling error, and "comparisons are descriptive; they do not show causes or predict the effect of any programme".

Planning question: the sector's decision question (e.g. health: "Where should nutrition and community-health programmes be assessed first?") followed by "Should {district} be considered, given the evidence below?".

Follow-up steps (fixed):

1. Triangulate with administrative and sector data (ministry, district and sub-district statistics).
2. Consult district technical staff and practitioners on the barriers behind the indicators flagged.
3. Assess feasibility, cost and equity of options before any allocation decision.

## Response schema

```json
{
  "version": "1.0", "district": "Gicumbi", "code": "gicumbi", "province": "Northern",
  "sector": "Health", "track": "Track 3: Open Innovation · Health",
  "purpose": "Screening and discussion, not a final allocation decision.",
  "need": 44.8, "need_rank": 17, "need_of": 30, "level": "middle fifth", "rank_range": [8, 25],
  "statements": [{ "rule_id": "R2-driver", "text": "…", "evidence": [{
      "code": "health_stunting", "name": "Children under 5 who are stunted", "value": 38.8, "national": 26.8,
      "gap": 12.0, "unit": "% of children under 5", "year": 2025, "source": "NISR, RDHS 2025, Table D.4",
      "source_url": "https://…", "difference_flag": null, "value_type": "official" }] }],
  "planning_question": "…", "follow_up": ["…"], "caveats": ["…"], "nst2": "…",
  "group": { "name": "Group A", "peers": ["Burera", "…"] }
}
```

## Worked example: Gicumbi, health

`GET /api/places/gicumbi/priority-brief?domain=health`

- **R1:** Gicumbi ranks 17 of 30 on health need, in the middle fifth.
- **R2:** Stunting 38.8% vs 26.8% for Rwanda (RDHS 2025), 12.0 points worse, z = +1.68. Descriptive (no SE published).
- **R2:** Birth registration 93.1% vs 95.1%, 2.0 points worse, z = +0.85. Descriptive.
- **R4:** NST2 national target for stunting is 15% by 2029; Gicumbi is 23.8 points above it.
- **Caveat:** leaving out one indicator moves Gicumbi between rank 8 and 25, so the exact rank should be treated with care.

So the brief does not say Gicumbi is a top health priority overall (it is mid-table, and the rank is sensitive), but it does show that its stunting is the highest of all districts and far from the national target: a reason to look at nutrition there first, which the follow-up steps turn into checks rather than a decision.

Compare `/brief/gasabo?domain=agriculture`, which returns only `R0-not-ranked`.
