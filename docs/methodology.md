# Methodology

This note explains where RIDIP's numbers come from, how they were checked, and how the need scores, significance tests, district groups and insights are calculated.

## 1. Data

RIDIP uses **21 indicators**, each published by NISR for all 30 districts.

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
| | Population with health insurance | 2024 | EICV7 Main Indicators Report, Table A3.7 |
| | Households owning a smartphone | 2024 | EICV7 MIR, Table A5.19 |
| | Households with internet access at home | 2024 | EICV7 MIR, Table A5.15 |
| | Households using electricity for lighting | 2024 | EICV7 MIR, Table A5.14 |
| Employment | Unemployment rate (LU1) | districts 2024–2025, national 2017–2025 | LFS 2025 Annual Tables, Tables 1 and 21–25 |
| | Youth NEET rate; labour force participation; employment-to-population ratio; labour underutilisation (LU4); median monthly earnings | 2017–2025 | LFS 2025 Annual Tables, Tables 1 and 21–25 |

Season A of the 2025 agricultural survey is used because it is the main season for most crops. "Derived" indicators are simple calculations by RIDIP from the published tables:

- **Irrigated land** = modern irrigated land (ha, Table 11) ÷ agricultural land (ha, Table 9). A blank in Table 11 is read as no modern irrigation recorded.
- **Erosion** = the "severe" plus "moderate" columns of Table 76.
- **Formally included** = banked + other formal (non-bank).

## 2. Preparation and checks

The pipeline is in `analytics/etl/` and writes `data/seed/indicators.csv` and `data/seed/indicator_values.csv`.

1. **Spreadsheets (SAS, LFS)** are read cell by cell from NISR's published Excel files. One district name is spelled "Nyahibu" in LFS Table 23 and is matched to Nyabihu.
2. **PDF tables (EICV7)** are extracted with their row layout and parsed by district name. All 30 rows of every table are required.
3. **FinScope Figure 13** is a stacked bar chart. Its printed data labels were read with their positions. Each district's four segments must add up to 100% (±1 for rounding). As a cross-check, the chart is sorted by the "excluded" share, and the parsed values follow that order. Values are whole percentages, as printed.
4. **Poverty** values were checked row by row against Annex B, and the 2024 values against the EICV7 booklet's district map.
5. The loader (`backend/scripts/load_indicators.py`) refuses to load unless every indicator covers all 30 districts and every area code is a known district.
6. Automated tests check sample values against each source table.

## 3. Need score (0–100)

For each track and district:

1. Take each indicator's latest year with values for every district.
2. Standardise across districts (z-score) and orient it so that a **positive value always means worse than the average district**. For example, high poverty and low improved-seed use are both positive.
3. Average the oriented z-scores of the track's indicators, with equal weights.
4. Rank districts on this average. The need score is the percentile: **100 = most in need, 0 = least**.

The three City of Kigali districts are mainly urban, so they are **left out of the agriculture comparison**. Their agriculture values are still shown.

Each district profile lists the indicators that push its score up (main drivers: oriented z > 0.5) and its main strength (z < −0.5).

## 4. Comparison with Rwanda and statistical significance

The gap to Rwanda is district value − national value, for the same year.

Where NISR publishes standard errors (all EICV7 indicators), the difference is called **significant** at 95% confidence when it exceeds 1.96 × √(SE_district² + SE_Rwanda²). The district's 95% confidence interval (±1.96 × SE) is shown on its card. For indicators without published standard errors (SAS, LFS, FinScope), no significance claim is made.

## 5. District groups (k-means)

Districts are clustered with **k-means (k = 4)** on the oriented z-scores of all 21 indicators. Kigali districts are given neutral (zero) agriculture scores for this purpose. The starting centres are chosen deterministically (farthest-point), so the result is reproducible. Each group is named by the tracks where its average need score is highest.

## 6. Automated insights

Insights are generated from rules, not a language model. Each states a track's need level (high, moderate or low, by thirds of the ranking), its main drivers and strength with their values, and any percentage indicator that changed by 5 points or more over the available years. Each insight lists the indicators it is built from.

## 7. Limitations

- Survey estimates have sampling error. Only EICV7 indicators come with published standard errors.
- Indicators come from different years (2024 or 2025), so cross-track comparisons describe the latest picture available, not a single year.
- Need scores are **relative**: they rank districts against each other, with equal weights. A low score does not mean no need.
- The 2017 poverty values are NISR's modelled estimates on the EICV7 method, not the originally published EICV5 figures.
- FinScope district values are rounded to whole percentages.
- District averages hide variation between sectors and villages.
