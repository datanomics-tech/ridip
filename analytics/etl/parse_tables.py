"""Pull district columns out of NISR report tables that were extracted page by page with their row layout.

Each table is found by its title; the first row for each of the 30 districts after the title is used,
and the national row ('Rwanda', 'All Rwanda' or 'Total') gives the national value.
Cells are separated by ' | '. Lone '-' cells (PDF minus signs split from their numbers) are dropped
before counting columns, and values in brackets (small samples, DHS) are kept without the brackets.
"""
import re

DISTRICTS = ["Nyarugenge","Gasabo","Kicukiro","Nyanza","Gisagara","Nyaruguru","Huye","Nyamagabe","Ruhango","Muhanga","Kamonyi","Karongi","Rutsiro","Rubavu","Nyabihu","Ngororero","Rusizi","Nyamasheke","Rulindo","Gakenke","Musanze","Burera","Gicumbi","Rwamagana","Nyagatare","Gatsibo","Kayonza","Kirehe","Ngoma","Bugesera"]
NATIONAL = ("Rwanda", "All Rwanda", "Total")


def cells(line: str) -> list[str]:
    parts = [c.strip() for c in line.split("|")]
    return [parts[0]] + [c.strip("()").replace(",", "") for c in parts[1:] if c not in ("-", "")]


def table(text: str, title: str) -> dict:
    """{district or 'rwanda': [numbers...]} for the table whose title line starts with `title`."""
    start = text.index(title)
    nxt = re.search(r"\n(Table|Appendix [A-Z]\b)", text[start + len(title):])
    block = text[start: start + len(title) + (nxt.start() if nxt else len(text))]
    out = {}
    for line in block.split("\n"):
        c = cells(line)
        name = c[0]
        if name in DISTRICTS and name not in out:
            out[name] = c[1:]
        elif name in NATIONAL and "rwanda" not in out:
            out["rwanda"] = c[1:]
    missing = set(DISTRICTS) - set(out)
    if missing:
        raise ValueError(f"{title}: missing {sorted(missing)}")
    return out


def num(x: str) -> float:
    return float(x)
