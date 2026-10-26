# Seed data

Small, published tables that RIDIP loads into the database. These files are committed because they are public aggregates, not microdata.

## eicv7_district_poverty.csv

Headcount poverty rate (% of population) by district.

- `poverty_2024`: EICV7 (2023/24), actual.
- `poverty_2017`: EICV5 (2016/17), modelled to the EICV7 methodology so the two years are comparable.
- National: 39.8% (2017) and 27.4% (2024).

Source: NISR, *EICV7 Poverty Profile, Thematic Report*, Annex B, "Headcount Poverty Rate in 2024 (actual) and 2017 (modelled) by District".
https://www.statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf

Checked row by row against Annex B on 26 Oct 2026. The 2024 values also match the district poverty map in the EICV7 dissemination booklet.
