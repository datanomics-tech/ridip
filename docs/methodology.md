# Methodology

This note explains where RIDIP's numbers come from, how they were checked, and how the need scores, the approximate difference flag, district groups, insights and priority briefs are calculated.

> **What a need score means.** Need scores show *relative* need among districts on published indicators. They are not a measure of absolute deprivation, a probability, or a causal effect, and they are not an official NISR index.

## 1. Data

RIDIP uses **39 indicators** in six sectors, each published by NISR for all 30 districts.

| Track | Indicator | Years | Source |
| --- | --- | --- | --- |
| Agriculture | Farmers using improved seeds | 2025 | SAS 2025 (Season A), Table 33 |
| | Farmers using inorganic fertilizer | 2025 | SAS 2025, Table 46 |
| | Farmers using organic fertilizer | 2025 | SAS 2025, Table 43 |
| | Agricultural land under modern irrigation (derived) | 2025 | SAS 2025, Tables 9 and 11 |
| | Plots with severe or moderate erosion (derived) | 2025 | SAS 2025, Table 76 |
| | Maize yield, bean yield | 2025 | SAS 2025, Table 19 |
| Finance & poverty | Headcount poverty rate | 2017 (modelled), 2024 | EICV7 Poverty Profile, Annex B; standard errors from EICV7 Main Indicators Report, Table A9.23 |
| | Adults banked; formally included (derived); financially excluded | 2024 (national also 2020) | FinScope Rwanda 2024, Figures 5 and 13 |
| | Households owning a mobile phone | 2024 | EICV7 Utilities and Amenities report, Table B.14 |
| | Households owning a smartphone | 2024 | EICV7 MIR, Table A5.19 |
| | Households with internet access at home | 2024 | EICV7 MIR, Table A5.15 |
| | Households using electricity for lighting | 2024 | EICV7 MIR, Table A5.14 |
| Employment | Unemployment rate (LU1) | districts 2024–2025, national 2017–2025 | LFS 2025 Annual Tables, Tables 1 and 21–25 |
| | Youth NEET rate; labour force participation; employment-to-population ratio; labour underutilisation (LU4); median monthly earnings | 2017–2025 | LFS 2025 Annual Tables, Tables 1 and 21–25 |
| Health | Children under 5 who are stunted | 2025 | Rwanda DHS 2025, Table D.4 |
| | Married women using a modern contraceptive method | 2025 | RDHS 2025, Table D.3 |
| | Children under 5 with a registered birth | 2025 | RDHS 2025, Table D.1 |
| | Children given vitamin A (6 months); deworming (6 months) | 2025 | RDHS 2025, Table D.6 |
| | Population with health insurance | 2024 | EICV7 Main Indicators Report, Table A3.7 |
| Education | Net attendance rate, primary; secondary | 2024 | EICV7 Education report, Tables A.3 and A.5 |
| | Primary completion; primary repetition | 2024 | EICV7 Education report, Tables A.22 and A.11 |
| | Out-of-school rate, upper secondary age | 2024 | EICV7 Education report, Table A.27 |
| | Literacy rate (15+); computer literacy (15–24) | 2017 (EICV5), 2024 | EICV7 Education report, Tables A.16 and A.19 |
| Transport | Households within 20 minutes' walk of an all-weather road | 2024 | EICV7 Utilities and Amenities report, Table A.28 |
| | Households within 20 minutes / an hour or more (derived) from a public transport stage | 2024 | EICV7 Utilities and Amenities report, Table A.31 |
| | Households owning a bicycle; a motorcycle | 2024 | EICV7 Utilities and Amenities report, Tables B.11 and B.12 |

Season A of the 2025 agricultural survey is used because it is the main season for most crops. "Derived" indicators are simple calculations by RIDIP from the published tables:

- **Irrigated land** = modern irrigated land (ha, Table 11) ÷ agricultural land (ha, Table 9). A blank in Table 11 is read as no modern irrigation recorded.
- **Erosion** = the "severe" plus "moderate" columns of Table 76.
- **Formally included** = banked + other formal (non-bank).
- **An hour or more from a transport stage** = the "60–119 minutes" plus "120+ minutes" columns of Table A.31.

## 2. Preparation and checks

The pipeline is in `analytics/etl/` and writes `data/seed/indicators.csv` and `data/seed/indicator_values.csv`.

1. **Spreadsheets (SAS, LFS)** are read cell by cell from NISR's published Excel files. One district name is spelled "Nyahibu" in LFS Table 23 and is matched to Nyabihu.
2. **PDF tables (EICV7 reports, DHS 2025)** are extracted with their row layout and parsed by district name (`parse_mir.py`, `parse_tables.py`; the extracted text is committed as `*_annex.txt`). All 30 rows of every table are required, and the column used is checked against the national row. In DHS tables, values in brackets (based on few cases) are kept and their brackets removed.
3. **FinScope Figure 13** is a stacked bar chart. Its printed data labels were read with their positions. Each district's four segments must add up to 100% (±1 for rounding). As a cross-check, the chart is sorted by the "excluded" share, and the parsed values follow that order. Values are whole percentages, as printed.
4. **Poverty** values were checked row by row against Annex B, and the 2024 values against the EICV7 booklet's district map.
5. The loader (`backend/scripts/load_indicators.py`) refuses to load unless every indicator covers all 30 districts and every area code is a known district.
6. Automated tests check sample values against each source table.

## 3. Need score (0–100)

For each sector and district:

1. Take each indicator's latest year with values for every district.
2. Standardise across districts (z-score) and orient it so that a **positive value always means worse than the average district**. For example, high poverty and low improved-seed use are both positive.
3. Average the oriented z-scores of the sector's indicators, with equal weights.
4. Rank districts on this average. The need score is the percentile: **100 = most in need, 0 = least**.

The three City of Kigali districts are mainly urban, so they are **left out of the agriculture comparison**. Their agriculture values are still shown.

Each district profile lists the indicators that push its score up (main drivers: oriented z > 0.5) and its main strength (z < −0.5).

### Safeguards (tested in `backend/tests/test_method.py`)

| Rule | What RIDIP does | Test |
| --- | --- | --- |
| Orientation | "Lower is better" indicators keep their sign; "higher is better" are reversed, so a worse value never lowers need. | `test_orientation_worse_value_never_lowers_need`, `test_higher_is_better_indicator_is_reversed` |
| Coverage | An indicator is scored only on its latest year with a value for **every** district compared; otherwise it is excluded with a stated reason. | `test_missing_district_value_excludes_indicator_with_reason` |
| Zero variance | An indicator with the same value everywhere is excluded (no division by zero). | `test_zero_variance_indicator_is_excluded_not_divided_by_zero` |
| Ties | Equal values or equal scores are ordered **alphabetically by district name**, so rankings are repeatable. Profiles say when a rank is shared. | `test_ties_are_ordered_alphabetically_and_repeatably` |
| Kigali | The three City of Kigali districts are not ranked on agriculture (ranked out of 27). | `test_kigali_not_ranked_on_agriculture` |
| Weighting | Equal weights within each sector. This is an analytical choice, not an official NISR index. | — |

With the current data no indicator is excluded by the coverage or zero-variance rules (`GET /api/method` lists any exclusions).

### Mixed source years

Sectors combine different surveys: agriculture SAS 2025, finance and poverty EICV7/FinScope 2024, employment LFS 2025, health RDHS 2025 and EICV7 2024, education and transport EICV7 2024. Every figure in the app shows its own year and source; the sectors are not a synchronised snapshot of one year.

### Sensitivity analysis (leave one indicator out)

Each sector was re-ranked with each indicator left out in turn. Results (also live at `GET /api/method` and on the About page):

| Sector | Indicators | Worst top-5 overlap | Districts whose rank never moves > 5 places | Most influential indicator (largest move) |
| --- | --- | --- | --- | --- |
| Agriculture | 7 | 3 of 5 | 26% | Farmers using organic fertilizer (10 places) |
| Finance & poverty | 8 | 3 of 5 | 90% | Headcount poverty rate (6) |
| Employment | 6 | 3 of 5 | 80% | Unemployment rate (6) |
| Health | 6 | 4 of 5 | 30% | Modern contraceptive use (15) |
| Education | 7 | 4 of 5 | 67% | Primary net attendance (6) |
| Transport | 5 | 4 of 5 | 67% | An hour or more from a transport stage (7) |

**Reading:** finance/poverty and employment rankings are robust. Health and agriculture rankings in the middle of the table depend on individual indicators, so they should be read as broad groupings rather than exact positions. The app shows each district's rank range and tags ranks that move more than 5 places as "rank sensitive".

## 4. Comparison with Rwanda: approximate 95% difference flag

The gap to Rwanda is district value − national value, for the same year.

Where NISR publishes standard errors (EICV7 Main Indicators Report and Utilities tables), RIDIP shows an **approximate 95% difference flag**: "above Rwanda" or "below Rwanda" when |district − Rwanda| > 1.96 × √(SE_district² + SE_Rwanda²), otherwise "no clear difference". This is an approximation: it ignores the covariance between a district and the national estimate (which includes that district) and the full survey design, so it is labelled as approximate and not as a formal significance test. The district's approximate 95% interval (±1.96 × SE) is shown on its card.

For indicators without published standard errors (SAS, LFS, FinScope, DHS district tables, EICV7 Education annex), the app says "uncertainty unavailable — descriptive comparison" and makes no difference claim.

## 4b. Targets

Only targets confirmed in an official document are shown as numbers, and they are labelled as **national** targets (not district targets):

| Indicator | Target | Source |
| --- | --- | --- |
| Children under 5 who are stunted | 33% → 15% by 2029 | MINECOFIN, NST2 2024–2029 presentation (January 2025), Social Transformation priority 2 |

Checked and **not** shown as numeric targets: electricity (NST2 states "access to electricity in all cells", not a household %), agricultural productivity +50% and irrigated land +85% (found only in press coverage; mentioned as press figures in sector text).

## 4c. Irrigation blanks

SAS 2025 Table 11 leaves five districts blank (Karongi, Rubavu, Nyabihu, Ngororero, Burera). The non-blank districts sum exactly to the national total of 30,290.1 ha, so the blanks are genuine zeros (no modern irrigation recorded), not missing data.

## 5. District groups (k-means)

Districts are clustered with **k-means (k = 4)** on the oriented z-scores of all 39 indicators. Kigali districts are given neutral (zero) agriculture scores for this purpose. The starting centres are chosen deterministically (farthest-point), so the result is reproducible. Each group is named by the sectors where its average need score is highest.

## 6. Automated insights and priority briefs

Insights are generated from rules, not a language model. Each states a track's need level (high, moderate or low, by thirds of the ranking), its main drivers and strength with their values, and any percentage indicator that changed by 5 points or more over the available years. Each insight lists the indicators it is built from.

The rules-based **District Priority & Intervention Advisor** (priority brief) is documented in [priority-advisor.md](priority-advisor.md).

## 7. Limitations

- Survey estimates have sampling error. Only some EICV7 tables publish standard errors, and the difference flag is approximate.
- Need scores and briefs are descriptive: they do not show causes or predict the effect of a programme.
- Health and agriculture ranks are sensitive to single indicators (see the sensitivity table).
- Indicators come from different years (2024 or 2025; poverty trend 2017 modelled), so cross-track comparisons describe the latest picture available, not a single year.
- Equal weights mean, for example, that a district with high stunting but good vitamin A and deworming coverage can score as moderate need on health. The drivers listed with each score make this visible.
- Need scores are **relative**: they rank districts against each other, with equal weights. A low score does not mean no need.
- The 2017 poverty values are NISR's modelled estimates on the EICV7 method, not the originally published EICV5 figures.
- FinScope district values are rounded to whole percentages.
- District averages hide variation between sectors and villages.
