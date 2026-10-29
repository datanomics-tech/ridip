"""Smoke test for a running RIDIP deployment.

Usage (from the repo root):
    python backend/scripts/smoke_test.py                         # https://ridip.onrender.com
    python backend/scripts/smoke_test.py http://localhost:8000   # local server

Uses only the Python standard library. The first request allows up to 90 s so a sleeping
free Render service has time to wake. Exits with code 1 if any check fails.
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://ridip.onrender.com").rstrip("/")


def get(path: str, timeout: float = 30):
    started = time.time()
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        body = r.read()
        return r.status, r.headers.get("content-type", ""), body, time.time() - started


def as_json(body: bytes):
    return json.loads(body.decode("utf-8"))


CHECKS = [
    ("/health", lambda b: as_json(b)["status"] == "ok"),
    ("/", lambda b: b"<div id=\"root\"" in b),
    ("/api/districts", lambda b: len(as_json(b)["features"]) == 30),
    ("/api/indicators", lambda b: len(as_json(b)) >= 39),
    ("/api/domains", lambda b: len(as_json(b)) == 6),
    ("/api/overview", lambda b: all(len(t["priority"]) == 5 for t in as_json(b)["tracks"].values())),
    ("/api/places/nyagatare", lambda b: as_json(b)["name"] == "Nyagatare"),
    ("/api/places/gicumbi/priority-brief?domain=health",
     lambda b: as_json(b)["statements"] and all(s["rule_id"] for s in as_json(b)["statements"])),
    ("/api/places/gasabo/priority-brief?domain=agriculture",
     lambda b: as_json(b)["statements"][0]["rule_id"] == "R0-not-ranked"),
    ("/api/method", lambda b: "tie_policy" in as_json(b) and len(as_json(b)["sensitivity"]) == 6),
    ("/api/places/nyagatare/report.csv", lambda b: b.startswith(b"district,sector,indicator")),
    ("/api/data.csv", lambda b: b.count(b"\n") > 1000),
    ("/place/nyagatare", lambda b: b"<div id=\"root\"" in b),   # SPA fallback for deep links
    ("/brief/gicumbi?domain=health", lambda b: b"<div id=\"root\"" in b),
]


def main() -> int:
    print(f"RIDIP smoke test against {BASE}  ({time.strftime('%Y-%m-%d %H:%M:%S %Z')})")
    failures = 0
    for n, (path, ok) in enumerate(CHECKS):
        try:
            status, _, body, secs = get(path, timeout=90 if n == 0 else 30)
            passed = status == 200 and bool(ok(body))
            detail = f"{status} in {secs:.2f}s"
        except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as e:
            passed, detail = False, f"error: {e}"
        failures += not passed
        print(f"  {'PASS' if passed else 'FAIL'}  {path}  ({detail})")
    try:
        urllib.request.urlopen(BASE + "/api/places/not-a-district", timeout=30)
        print("  FAIL  /api/places/not-a-district  (expected 404)")
        failures += 1
    except urllib.error.HTTPError as e:
        print(f"  {'PASS' if e.code == 404 else 'FAIL'}  /api/places/not-a-district  ({e.code})")
        failures += e.code != 404
    print(f"{len(CHECKS) + 1 - failures} of {len(CHECKS) + 1} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
