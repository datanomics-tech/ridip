# Seed data

Published district tables that RIDIP loads into the database. They are committed because they are public aggregates, not microdata.

| File | Contents |
| --- | --- |
| `indicators.csv` | One row per indicator: code, track (`domain`), name, unit, whether higher or lower is better, source, source URL, notes, and whether it is official or derived |
| `indicator_values.csv` | One row per indicator, area and year: value and standard error (where NISR publishes one). Area `rwanda` is the national value |
| `eicv7_district_poverty.csv` | EICV7 Poverty Profile, Annex B, as transcribed (the original Stage 4 input) |

Load with `python -m scripts.load_indicators` from `backend/`.

## How they are built

`analytics/etl/build_seed.py` builds both CSVs from the official files. Download these into `analytics/etl/src/` (not committed):

| File | Download |
| --- | --- |
| `sas2025_tables.xlsx` | https://statistics.gov.rw/sites/default/files/documents/2025-12/SAS%202025_Annual%20Tables.xlsx |
| `lfs2025_tables.xlsx` | https://statistics.gov.rw/sites/default/files/documents/2026-05/RWLFS_Annual_Tables_LFS2025.xlsx |

The EICV7 and FinScope tables come from PDFs. Their parsed forms are committed next to the scripts:

- `eicv7_mir_tables.json`: district annex tables of the EICV7 Main Indicators Report, parsed by `parse_mir.py`.
- `finscope2024_districts.json`: FinScope 2024 Figure 13, rebuilt from the chart's data labels (`finscope2024_fig13_items.txt`) by `parse_finscope.py`.
- `dhs_annex.txt`, `edu_annex.txt`, `util_annex.txt`: the district annex pages of the RDHS 2025 Final Report (Appendix D), the EICV7 Education report and the EICV7 Utilities and Amenities report, extracted with their row layout; read by `parse_tables.py`.

Then run, from the repository root:

```bash
cp data/seed/eicv7_district_poverty.csv analytics/etl/eicv7_mir_tables.json analytics/etl/finscope2024_districts.json analytics/etl/*_annex.txt analytics/etl/src/
python analytics/etl/build_seed.py analytics/etl/src data/seed
```

Checks applied: every indicator must cover all 30 districts; FinScope segments must add up to 100% (±1). Details: [docs/methodology.md](../../docs/methodology.md).
