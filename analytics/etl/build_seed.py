"""Build RIDIP's seed tables from official NISR source files.

Inputs (downloaded from statistics.gov.rw into src/):
  sas2025_tables.xlsx        Seasonal Agricultural Survey 2025, Annual Tables
  lfs2025_tables.xlsx        Labour Force Survey 2025, Annual Tables (RWLFS_Annual_Tables_LFS2025.xlsx)
  eicv7_mir_tables.json      EICV7 Main Indicator Report, district annex tables (parsed by parse_mir.py)
  finscope2024_districts.json FinScope 2024, Figure 13 access strand by district (parsed by parse_finscope.py)
  eicv7_district_poverty.csv EICV7 Poverty Profile, Annex B (already in data/seed)

Outputs: indicators.csv and indicator_values.csv
"""
import csv, json, sys, warnings
from pathlib import Path
import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_tables import table  # noqa: E402

warnings.filterwarnings("ignore")
SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
DISTRICTS = ["Nyarugenge","Gasabo","Kicukiro","Nyanza","Gisagara","Nyaruguru","Huye","Nyamagabe","Ruhango","Muhanga","Kamonyi","Karongi","Rutsiro","Rubavu","Nyabihu","Ngororero","Rusizi","Nyamasheke","Rulindo","Gakenke","Musanze","Burera","Gicumbi","Rwamagana","Nyagatare","Gatsibo","Kayonza","Kirehe","Ngoma","Bugesera"]

URL = {
    "sas": "https://statistics.gov.rw/sites/default/files/documents/2025-12/SAS%202025_Annual%20Tables.xlsx",
    "lfs": "https://statistics.gov.rw/sites/default/files/documents/2026-05/RWLFS_Annual_Tables_LFS2025.xlsx",
    "mir": "https://www.statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Main%20Indicator%20Report.pdf",
    "pov": "https://www.statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf",
    "fin": "https://statistics.gov.rw/sites/default/files/documents/2024-09/Rwanda-Finscope-2024-Report_compressed.pdf",
    "dhs": "https://statistics.gov.rw/sites/default/files/documents/2026-08/2025%20RDHS%20Final%20Report.pdf",
    "edu": "https://statistics.gov.rw/sites/default/files/documents/2025-04/EICV7_Thematic%20Report%20Education_N.pdf",
    "util": "https://www.statistics.gov.rw/sites/default/files/documents/2025-05/EICV7_Thematic%20Report%20Amenities%20and%20Utilities%20%281%29.pdf",
}
indicators, values = [], []

def add_indicator(code, domain, name, unit, direction, source, url, note="", value_type="official"):
    indicators.append(dict(code=code, domain=domain, name=name, unit=unit, direction=direction,
                           source=source, source_url=url, note=note, value_type=value_type))

def add(code, area, year, value, se=None):
    if value is None or value == "" or value == ".":
        return
    values.append(dict(indicator_code=code, area_code=area.strip().lower(), year=year,
                       value=round(float(value), 2), se="" if se in (None, "") else round(float(se), 2)))

def sheet_rows(wb, name):
    return [list(r) for r in wb[name].iter_rows(values_only=True)]

def district_table(rows, col, label_col=1):
    """{area: value} for the 30 districts plus Rwanda (National/Total row) from a SAS table."""
    out = {}
    for r in rows:
        label = r[label_col].strip() if isinstance(r[label_col], str) else None
        if label in DISTRICTS:
            out[label] = r[col]
        elif label and label.lower() in ("national", "total"):
            out["rwanda"] = r[col]
    return out

# ---------- Agriculture: SAS 2025, Season A ----------
sas = openpyxl.load_workbook(SRC / "sas2025_tables.xlsx", read_only=True, data_only=True)
SAS = "NISR, Seasonal Agricultural Survey 2025 (Season A)"
ag = [
    ("ag_improved_seeds", "Table 33", 2, "Farmers using improved seeds", "% of farmers", "higher", "Table 33"),
    ("ag_inorganic_fertilizer", "Table 46", 2, "Farmers using inorganic fertilizer", "% of farmers", "higher", "Table 46"),
    ("ag_organic_fertilizer", "Table 43", 2, "Farmers using organic fertilizer", "% of farmers", "higher", "Table 43"),
    ("ag_maize_yield", "Table 19", 3, "Maize yield", "kg per hectare", "higher", "Table 19"),
    ("ag_bean_yield", "Table 19", 18, "Bean yield", "kg per hectare", "higher", "Table 19"),
]
for code, sheet, col, name, unit, direction, tab in ag:
    add_indicator(code, "agriculture", name, unit, direction, f"{SAS}, {tab}", URL["sas"])
    t = district_table(sheet_rows(sas, sheet), col)
    for area, v in t.items():
        add(code, area, 2025, v)

# Erosion: severe + moderate share of plots (Table 76)
add_indicator("ag_erosion", "agriculture", "Plots with severe or moderate erosion", "% of plots", "lower",
              f"{SAS}, Table 76", URL["sas"], "Sum of the 'severe' and 'moderate' erosion columns.", "derived")
rows = sheet_rows(sas, "Table 76")
sev, mod = district_table(rows, 2), district_table(rows, 3)
for area in sev:
    add("ag_erosion", area, 2025, (sev[area] or 0) + (mod[area] or 0))

# Irrigation: modern irrigated land (Table 11, ha) as % of agricultural land (Table 9, '000 ha)
add_indicator("ag_irrigated_land", "agriculture", "Agricultural land under modern irrigation", "% of agricultural land", "higher",
              f"{SAS}, Tables 9 and 11", URL["sas"],
              "Modern irrigated land (ha) divided by agricultural land (ha). A blank in Table 11 is read as no modern irrigation recorded.", "derived")
irr, land = district_table(sheet_rows(sas, "Table 11"), 2), district_table(sheet_rows(sas, "Table 9"), 3)
for area in land:
    add("ag_irrigated_land", area, 2025, 100 * (irr.get(area) or 0) / (land[area] * 1000))

# ---------- Employment: LFS annual tables, district sheets T21-T25 ----------
lfs = openpyxl.load_workbook(SRC / "lfs2025_tables.xlsx", read_only=True, data_only=True)
LFS = "NISR, Labour Force Survey Annual Tables 2025"
emp = [
    ("emp_unemployment", "LU1-Unemployment rate", "Unemployment rate", "% of labour force", "lower"),
    ("emp_youth_neet", "NEET rate", "Youth not in employment, education or training (NEET)", "% of youth", "lower"),
    ("emp_participation", "Labour force participation rate", "Labour force participation rate", "% of working-age population", "higher"),
    ("emp_employment_ratio", "Employment-to-population ratio", "Employment-to-population ratio", "% of working-age population", "higher"),
    ("emp_underutilization", "LU4", "Labour underutilization (LU4)", "% of extended labour force", "lower"),
    ("emp_median_earnings", "Median monthly earnings", "Median monthly earnings at main job", "Frw per month", "higher"),
]
for code, _, name, unit, direction in emp:
    add_indicator(code, "employment", name, unit, direction, f"{LFS}, Tables 1 and 21-25", URL["lfs"])

ALIASES = {"Nyahibu": "Nyabihu"}


def lfs_block(rows, start):
    years = rows[start + 1][1:]
    block = {}
    for r in rows[start + 2:]:
        if not r[0] or r[0] in DISTRICTS or r[0] in ALIASES or str(r[0]).startswith("Source"):
            break
        block[str(r[0])] = dict(zip(years, r[1:]))
    return block

def add_lfs(area, block):
    for code, key, *_ in emp:
        row = next((v for k, v in block.items() if key in k), None)
        if row is None:
            raise SystemExit(f"{area}: missing {key}")
        for year, v in row.items():
            if str(year).strip().isdigit() and isinstance(v, (int, float)):
                add(code, area, int(str(year).strip()), v)

ALIASES = {"Nyahibu": "Nyabihu"}  # spelling in the LFS 2025 table T23
found = set()
for sheet in [s for s in lfs.sheetnames if s.startswith(("T21", "T22", "T23", "T24", "T25"))]:
    rows = sheet_rows(lfs, sheet)
    for i, r in enumerate(rows):
        name = ALIASES.get(r[0], r[0])
        if name in DISTRICTS and rows[i + 1][0] == r[0]:
            add_lfs(name, lfs_block(rows, i))
            found.add(name)
rows = sheet_rows(lfs, "T1-LFIndicatorsRw")
add_lfs("rwanda", lfs_block(rows, 1))
assert found == set(DISTRICTS), set(DISTRICTS) - found

# ---------- Finance & poverty ----------
POV = "NISR, EICV7 Poverty Profile (Annex B); standard errors from EICV7 Main Indicators Report, Table A9.23"
add_indicator("poverty_rate", "finance_poverty", "Headcount poverty rate", "% of population", "lower", POV, URL["pov"],
              "2017 values are NISR's EICV5 estimates modelled on the EICV7 method.")
mir = json.load(open(SRC / "eicv7_mir_tables.json"))
se24 = {d: r[1] for d, r in mir["A9.23"]["rows"].items()}
for r in csv.DictReader(open(SRC / "eicv7_district_poverty.csv")):
    add("poverty_rate", r["district"], 2017, r["poverty_2017"])
    add("poverty_rate", r["district"], 2024, r["poverty_2024"], se24[r["district"]])
add("poverty_rate", "rwanda", 2017, 39.8)
add("poverty_rate", "rwanda", 2024, 27.4, mir["A9.23"]["national"][1])

MIR = "NISR, EICV7 Main Indicators Report (2023/24)"
eicv = [
    ("fin_smartphone", "A5.19", "Households owning a smartphone", "% of households", "higher"),
    ("fin_internet", "A5.15", "Households with internet access at home", "% of households", "higher"),
    ("fin_electricity", "A5.14", "Households using electricity for lighting", "% of households", "higher"),
]
for code, tab, name, unit, direction in eicv:
    add_indicator(code, "finance_poverty", name, unit, direction, f"{MIR}, Table {tab}", URL["mir"])
    t = mir[tab]
    assert t["n"] == 30, tab
    for d, r in t["rows"].items():
        add(code, d, 2024, r[0], r[1])
    add(code, "rwanda", 2024, t["national"][0], t["national"][1])

FIN = "NISR / AFR, FinScope Rwanda 2024, Figure 13 (financial access strand by district)"
fin_note = "District values are the rounded data labels of Figure 13; national values (2020 and 2024) are from Figure 5."
add_indicator("fin_banked", "finance_poverty", "Adults with a bank account or product", "% of adults", "higher", FIN, URL["fin"], fin_note)
add_indicator("fin_formal", "finance_poverty", "Adults formally included (bank or other formal)", "% of adults", "higher", FIN, URL["fin"], fin_note, "derived")
add_indicator("fin_excluded", "finance_poverty", "Adults financially excluded", "% of adults", "lower", FIN, URL["fin"], fin_note)
fs = json.load(open(SRC / "finscope2024_districts.json"))
assert set(fs) == set(DISTRICTS)
for d, r in fs.items():
    add("fin_banked", d, 2024, r["banked"])
    add("fin_formal", d, 2024, r["banked"] + r["other_formal"])
    add("fin_excluded", d, 2024, r["excluded"])
# National access strand, FinScope 2024 report, Figure 5 (2024 and 2020)
for year, banked, formal, excluded in [(2024, 22, 92, 4), (2020, 22, 77, 7)]:
    add("fin_banked", "rwanda", year, banked)
    add("fin_formal", "rwanda", year, formal)
    add("fin_excluded", "rwanda", year, excluded)

# ---------- Health: Rwanda DHS 2025, Appendix D district tables; EICV7 health insurance ----------
DHS = "NISR, Rwanda Demographic and Health Survey 2025, Appendix D"
dhs = (SRC / "dhs_annex.txt").read_text(encoding="utf-8")
health = [
    ("health_stunting", "Table | D.4 ", 1, "Children under 5 who are stunted", "% of children under 5", "lower", "Table D.4"),
    ("health_modern_contraception", "Table | D.3 ", 1, "Married women using a modern contraceptive method", "% of married women 15-49", "higher", "Table D.3"),
    ("health_birth_registration", "Table | D.1 ", 2, "Children under 5 with a registered birth", "% of children under 5", "higher", "Table D.1"),
    ("health_vitamin_a", "Table | D.6 ", 3, "Children given vitamin A in the last 6 months", "% of children 6-59 months", "higher", "Table D.6"),
    ("health_deworming", "Table | D.6 ", 5, "Children given deworming medication in the last 6 months", "% of children 12-59 months", "higher", "Table D.6"),
]
for code, title, col, name, unit, direction, tab in health:
    add_indicator(code, "health", name, unit, direction, f"{DHS}, {tab}", URL["dhs"])
    for area, row in table(dhs, title).items():
        add(code, area, 2025, row[col])
add_indicator("health_insurance", "health", "Population with health insurance", "% of population", "higher",
              f"{MIR}, Table A3.7", URL["mir"])
t = mir["A3.7"]
for d, r in t["rows"].items():
    add("health_insurance", d, 2024, r[0], r[1])
add("health_insurance", "rwanda", 2024, t["national"][0], t["national"][1])

# ---------- Education: EICV7 Thematic Report Education, Annex A ----------
EDU = "NISR, EICV7 Thematic Report: Education (2023/24), Annex"
edu = (SRC / "edu_annex.txt").read_text(encoding="utf-8")
education = [  # code, title, {year: column}, name, unit, direction, table
    ("edu_primary_attendance", "Table A.3:", {2024: 2}, "Net attendance rate, primary school", "% of children 7-12", "higher", "Table A.3"),
    ("edu_secondary_attendance", "Table A.5:", {2024: 2}, "Net attendance rate, secondary school", "% of youth 13-18", "higher", "Table A.5"),
    ("edu_primary_completion", "Table A.22:", {2024: 2}, "Primary school completion rate", "% of population 14-16", "higher", "Table A.22"),
    ("edu_primary_repetition", "Table A. 11:", {2024: 2}, "Repetition rate, primary school", "% of primary pupils", "lower", "Table A.11"),
    ("edu_out_of_school", "Table A.27:", {2024: 0}, "Out-of-school rate, upper secondary age", "% of youth 16-18", "lower", "Table A.27"),
    ("edu_literacy", "Table A. 16:", {2017: 2, 2024: 6}, "Literacy rate, population 15 and over", "% of population 15+", "higher", "Table A.16"),
    ("edu_computer_literacy", "Table A.19:", {2017: 2, 2024: 6}, "Computer literacy, youth 15-24", "% of youth 15-24", "higher", "Table A.19"),
]
for code, title, cols, name, unit, direction, tab in education:
    note = "2017 values are from EICV5 (2016/17), as published in the same table." if 2017 in cols else ""
    add_indicator(code, "education", name, unit, direction, f"{EDU}, {tab}", URL["edu"], note)
    for area, row in table(edu, title).items():
        for year, col in cols.items():
            add(code, area, year, row[col])

# ---------- Transport: EICV7 Thematic Report Utilities and Amenities ----------
UTIL = "NISR, EICV7 Thematic Report: Utilities and Amenities (2023/24)"
util = (SRC / "util_annex.txt").read_text(encoding="utf-8")
add_indicator("tr_road_access", "transport", "Households within 20 minutes' walk of an all-weather road", "% of households",
              "higher", f"{UTIL}, Table A.28", URL["util"])
for area, row in table(util, "Table A.28:").items():
    add("tr_road_access", area, 2024, row[0])
add_indicator("tr_stage_access", "transport", "Households within 20 minutes' walk of a public transport stage", "% of households",
              "higher", f"{UTIL}, Table A.31", URL["util"])
add_indicator("tr_stage_far", "transport", "Households an hour or more from a public transport stage", "% of households",
              "lower", f"{UTIL}, Table A.31", URL["util"], "Sum of the '60-119 minutes' and '120+ minutes' columns.", "derived")
for area, row in table(util, "Table A.31:").items():
    add("tr_stage_access", area, 2024, row[0])
    add("tr_stage_far", area, 2024, float(row[2]) + float(row[3]))
for code, title, name, tab in [("tr_bicycle", "Table B.11:", "Households owning a bicycle", "Table B.11"),
                               ("tr_motorcycle", "Table B.12:", "Households owning a motorcycle (private use)", "Table B.12")]:
    add_indicator(code, "transport", name, "% of households", "higher", f"{UTIL}, {tab}", URL["util"])
    for area, row in table(util, title).items():
        add(code, area, 2024, row[0], row[1])

# Finance: mobile phone ownership (mobile money access)
add_indicator("fin_mobile_phone", "finance_poverty", "Households owning a mobile phone", "% of households", "higher",
              f"{UTIL}, Table B.14", URL["util"])
for area, row in table(util, "Table B.14:").items():
    add("fin_mobile_phone", area, 2024, row[0], row[1])

# ---------- Checks and output ----------
codes = {i["code"] for i in indicators}
for code in codes:
    areas = {v["area_code"] for v in values if v["indicator_code"] == code}
    missing = {d.lower() for d in DISTRICTS} - areas
    assert not missing, f"{code}: missing {missing}"
OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "indicators.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(indicators[0])); w.writeheader(); w.writerows(indicators)
with open(OUT / "indicator_values.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(values[0])); w.writeheader(); w.writerows(values)
print(f"{len(indicators)} indicators, {len(values)} values")
for i in indicators:
    n = [v for v in values if v["indicator_code"] == i["code"]]
    print(f"  {i['domain']:16} {i['code']:24} years={sorted({v['year'] for v in n})} rows={len(n)}")
