# Final improvements checklist

Tracks every item in *RIDIP Hackathon Final Improvements and Implementation Plan* and where the evidence is. Status: ✅ done · 🔲 to do by the team.

## 1. Correct misleading labels

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 1.1 | Need score explained as **relative** need, not absolute deprivation, probability, causal effect or an official index | ✅ | Shown on Home, district overview, every sector tab, report, brief, About (`NEED_MEANING` in `pages/Place.tsx`); [methodology](methodology.md) top note |
| 1.2 | "Statistically significant" replaced by **approximate 95% difference flag** with its formula and caveat | ✅ | `_difference_flag()` in `analytics.py`; indicator cards, report column "Approx. 95% flag", CSV column `approx_95_difference_flag`; [methodology §4](methodology.md) |
| 1.3 | "Uncertainty unavailable — descriptive" where no standard error is published | ✅ | Indicator cards, brief table, report "Descriptive"; `test_difference_flag_only_with_standard_errors` |
| 1.4 | Targets labelled as **national**, not district | ✅ | Card target line, brief rule `R4-target`, About "Verified national targets" |
| 1.5 | Mixed source years made visible | ✅ | Profile overview "data years", Home note, brief caveat, About "Source years", Explore year/source tag, Compare unit and year per row |
| 1.6 | Provenance on every figure (source, link, year, official/derived, note) | ✅ | Indicator cards, brief evidence table, report source column, CSV `source_url` |
| 1.7 | Insights say "fixed, documented rules (no AI model)"; poverty trend notes 2017 is modelled | ✅ | `pages/Place.tsx`, insight text in `analytics.py` |

## 2. Method safeguards and tests

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 2.1 | Orientation (worse never lowers need) | ✅ | 2 tests in `test_method.py` |
| 2.2 | Coverage rule with stated exclusion reason | ✅ | `test_missing_district_value_excludes_indicator_with_reason` |
| 2.3 | Tie policy (alphabetical, repeatable) | ✅ | `test_ties_are_ordered_alphabetically_and_repeatably`; tie note on cards |
| 2.4 | Zero-variance indicators excluded | ✅ | `test_zero_variance_indicator_is_excluded_not_divided_by_zero` |
| 2.5 | Kigali rule | ✅ | `test_kigali_not_ranked_on_agriculture` (method and places) |
| 2.6 | Leave-one-indicator-out sensitivity | ✅ | `_sensitivity()`; `GET /api/method`; About table; rank ranges and "rank sensitive" tags; [methodology](methodology.md) table |
| 2.7 | Irrigation blanks verified as zeros | ✅ | Table 11 non-blank sum = national 30,290.1 ha; [methodology §4c](methodology.md) |

## 3. District Priority & Intervention Advisor

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 3.1 | `GET /api/places/{code}/priority-brief?domain=` | ✅ | `main.py`, smoke test |
| 3.2 | Rule ids and evidence on every statement | ✅ | R0, R1, R2, R4, R5; `test_priority_brief_is_deterministic_traceable_and_not_causal` |
| 3.3 | No causal claims; "screening, not allocation" purpose | ✅ | Same test checks banned causal words; purpose line and caveats |
| 3.4 | Insufficient-evidence rule | ✅ | `R5-insufficient`; `R0-not-ranked` for Kigali agriculture |
| 3.5 | Brief page with sector selector, print/PDF and CSV | ✅ | `/brief/{code}?domain=`; [screenshot](images/validation/brief-1366.png) |
| 3.6 | Linked from profile, each sector tab and the report builder | ✅ | `pages/Place.tsx`, `pages/Report.tsx` |
| 3.7 | Documentation | ✅ | [priority-advisor.md](priority-advisor.md) |

## 4. Target panel (verified targets only)

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 4.1 | Stunting 33% → 15% by 2029 verified from the MINECOFIN NST2 deck | ✅ | `TARGETS` in `domains.py` with source URL |
| 4.2 | Unverified targets removed or labelled as press figures (electricity, productivity +50%, irrigation +85%) | ✅ | `domains.py` sector text; [methodology §4b](methodology.md); README "What the data shows" |
| 4.3 | Target shown on card, brief and About | ✅ | Indicator card target line, `R4-target`, About |

## 5. UI / UX

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 5.1 | Cold-start message while the free server wakes; automatic retries | ✅ | `ServerBanner.tsx`, `fetchWithWake` in `api.ts` |
| 5.2 | Home primary action "Start with a district" | ✅ | `pages/Home.tsx`; [screenshot](images/validation/home-360.png) |
| 5.3 | Legend, year and source visible on the map | ✅ | Explore legend + year/source tag |
| 5.4 | Responsive at 360 / 768 / 1366 px | ✅ | [validation.md](validation.md); report table overflow at 360 px fixed |
| 5.5 | Accessibility checks | ✅ | Labels, one `h1`, `alt`, focus outlines, `role="status"` on banner; [validation.md](validation.md) |

## 6. QA

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 6.1 | Test log (22 passed) | ✅ | [validation/pytest.log](validation/pytest.log) |
| 6.2 | Build log | ✅ | [validation/build.log](validation/build.log) |
| 6.3 | Smoke test script and local run (15/15) | ✅ | `backend/scripts/smoke_test.py`, [validation/smoke-local.log](validation/smoke-local.log) |
| 6.4 | Live smoke test after deploy | 🔲 | Run `python backend/scripts/smoke_test.py > docs/validation/smoke-live.log` after Render redeploys; update [validation.md](validation.md) |
| 6.5 | `docs/validation.md` | ✅ | [validation.md](validation.md) |

## 7. Documentation

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 7.1 | README: new features, limitations, video placeholder | ✅ (video link 🔲) | [README](../README.md) |
| 7.2 | Methodology: tie policy, flag caveat, sensitivity, targets, irrigation blanks | ✅ | [methodology.md](methodology.md) |
| 7.3 | Priority advisor doc | ✅ | [priority-advisor.md](priority-advisor.md) |
| 7.4 | AI-use disclosure updated | ✅ | [ai-use.md](ai-use.md) |
| 7.5 | Project guide updated (endpoints, tests, pages) | ✅ | [project-guide.md](project-guide.md) |
| 7.6 | Demo script: priority brief segment | ✅ | Demo video script (Word) |

## 8. Final sign-off (team)

| # | Item | Status |
| --- | --- | --- |
| 8.1 | Branch `feature/final-improvements` merged to `main`; Render redeployed | 🔲 |
| 8.2 | Live smoke test passes (6.4) | 🔲 |
| 8.3 | Demo video recorded, uploaded, link added to README | 🔲 |
| 8.4 | Repository public; README links work | 🔲 |
| 8.5 | Eligibility confirmed (team composition per the competition rules) | 🔲 |
| 8.6 | Submitted before 30 Oct 2026, 11:59 PM: GitHub link, live app link, documentation | 🔲 |
