import re, json, sys
D = ["Nyarugenge","Gasabo","Kicukiro","Nyanza","Gisagara","Nyaruguru","Huye","Nyamagabe","Ruhango","Muhanga","Kamonyi","Karongi","Rutsiro","Rubavu","Nyabihu","Ngororero","Rusizi","Nyamasheke","Rulindo","Gakenke","Musanze","Burera","Gicumbi","Rwamagana","Nyagatare","Gatsibo","Kayonza","Kirehe","Ngoma","Bugesera"]
txt = open(sys.argv[1]).read()
parts = re.split(r'\n(?=Table A\d+\.\d+)', txt)
tables = {}
for p in parts:
    m = re.match(r'Table (A\d+\.\d+):?\s*(.*)', p)
    if not m: continue
    title = m.group(2).split('\n')[0]
    rows = {}
    nat = None
    for line in p.split('\n'):
        cells = [c.strip() for c in line.split('|')]
        if cells[0] in D and cells[0] not in rows:
            rows[cells[0]] = cells[1:]
        if cells[0] == 'Rwanda' and nat is None:
            nat = cells[1:]
    tables[m.group(1)] = {"title": title, "n": len(rows), "national": nat, "rows": rows}
json.dump(tables, open(sys.argv[2], 'w'), indent=1)
for k, v in tables.items():
    first = next(iter(v['rows'].values()), None)
    print(k, v['n'], v['title'][:70], '| nat', v['national'], '| first', first)
