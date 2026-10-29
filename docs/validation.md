# Validation record

Evidence that the final build works, for the NISR 2026 Big Data Hackathon submission. Logs are in [`docs/validation/`](validation/).

| Check | When | Where | Result | Evidence |
| --- | --- | --- | --- | --- |
| Backend tests (`pytest -v`) | 29 Oct 2026 | Local, PostgreSQL 16 + PostGIS with the seed data | **22 passed** | [validation/pytest.log](validation/pytest.log) |
| Frontend type check and production build (`npm run build`) | 29 Oct 2026 | Local | Built, no type errors | [validation/build.log](validation/build.log) |
| Smoke test (`python backend/scripts/smoke_test.py http://localhost:8000`) | 29 Oct 2026 | Local server running the production build | **15 of 15** checks passed | [validation/smoke-local.log](validation/smoke-local.log) |
| Smoke test against the live site (`python backend/scripts/smoke_test.py`) | After deploy | https://ridip.onrender.com | _to be filled in after deploy_ | `validation/smoke-live.log` |
| Responsive layout at 360, 768 and 1366 px | 29 Oct 2026 | Headless Chromium, 7 pages (home, profile, brief, about, explore, compare, report) | No horizontal page scroll at any width (one overflow on the report page at 360 px was found and fixed by wrapping its tables) | [screenshots](images/validation/) |
| Accessibility spot checks | 29 Oct 2026 | Same run | Every select and input has a label; one `h1` per page; no images without `alt`; no JavaScript errors in the console; visible focus outline on links, buttons and fields | — |

## What the tests cover

| Area | Tests |
| --- | --- |
| Database and boundaries | `test_db.py`, `test_districts.py` (30 districts, valid geometry) |
| Source values | `test_indicators.py`: sample values match EICV7 Annex B, FinScope, SAS, LFS, RDHS tables |
| Profiles, overview and downloads | `test_places.py`: six sector tabs, Kigali not ranked on agriculture, priorities and groups, CSV headers, 404s |
| Method safeguards | `test_method.py`: orientation, reversed "higher is better", coverage exclusion, zero variance, alphabetical ties, Kigali rule, sensitivity per sector, difference flag only with standard errors |
| Priority brief | `test_method.py`: deterministic, every statement has a rule id, evidence has a source, no causal words, unknown inputs return 404 |

## Smoke test checks

`/health`, home page, `/api/districts` (30), `/api/indicators` (≥ 39), `/api/domains` (6), `/api/overview` (5 priorities per sector), a district profile, two priority briefs (Gicumbi health; Gasabo agriculture returns `R0-not-ranked`), `/api/method`, the profile CSV, the full data CSV, two deep links served by the single-page app, and a 404 for an unknown district.

The first request allows 90 seconds, because the free Render service sleeps after 15 minutes idle.

## Screenshots

| Width | Page |
| --- | --- |
| 360 px (phone) | [Home](images/validation/home-360.png) · [Explore](images/validation/explore-360.png) · [Report](images/validation/report-360.png) |
| 768 px (tablet) | [District profile](images/validation/place-768.png) |
| 1366 px (laptop) | [Priority brief](images/validation/brief-1366.png) · [About / method](images/validation/about-1366.png) |
