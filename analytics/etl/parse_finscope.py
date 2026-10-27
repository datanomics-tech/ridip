"""Rebuild FinScope 2024 Figure 13 ("Financial Access Strand by districts", %) from its printed data labels.

Each district row has labels for Banked, Other formal (non-bank), Informal only and Excluded, left to right.
Two one-digit labels for small segments are sometimes printed touching (e.g. "21" = 2 and 1), so a
two-character label at the end of a bar is split only when that makes the row add up to 100 (+/-1, rounding).
"""
import sys, json, itertools
items = [s.strip().split(',') for s in open(sys.argv[1]).read().split(';')]
items = [(int(a), int(b), c, int(d)) for a, b, c, d in items]
names = {y: c for x, y, c, w in items if c.isalpha()}
nums = [(x, y, c, w) for x, y, c, w in items if not c.isalpha()]

def candidates(row):
    """All readings of a row: each ambiguous two-digit tail label may be one number or two."""
    options = []
    for x, _, c, w in row:
        parts = c.split()
        opts = [[(x, int(p)) for p in parts]]
        if len(parts) == 1 and len(c) == 2 and x > 430:
            opts.append([(x, int(c[0])), (x + w / 2, int(c[1]))])
        options.append(opts)
    for combo in itertools.product(*options):
        yield [v for part in combo for v in part]

out = {}
for y, name in sorted(names.items()):
    row = sorted(n for n in nums if abs(n[1] - y) <= 4)
    chosen = None
    for vals in candidates(row):
        v = [p for _, p in vals]
        if len(v) == 4:
            b, o, i, e = v
        elif len(v) == 3:  # one small segment has no label: decide by position of the last label
            b, o = v[0], v[1]
            i, e = (0, v[2]) if vals[2][0] >= 470 else (v[2], 0)
        else:
            continue
        if 99 <= b + o + i + e <= 101:
            chosen = dict(banked=b, other_formal=o, informal_only=i, excluded=e, total=b + o + i + e)
            break
    if not chosen:
        raise SystemExit(f"{name}: no reading adds to 100: {row}")
    out[name] = chosen
for k, r in out.items():
    print(f"{k:12} {r}")
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(len(out), 'districts; totals:', sorted({r['total'] for r in out.values()}))
