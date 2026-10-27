import { useEffect, useState, type FormEvent } from "react";
import { api } from "./api";
import { Link, navigate, useLocation } from "./router";
import type { IndicatorMeta } from "./types";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/explore", label: "Explore" },
  { to: "/agriculture", label: "Agriculture" },
  { to: "/finance-poverty", label: "Finance & poverty" },
  { to: "/open-innovation", label: "Open innovation" },
  { to: "/compare", label: "Compare" },
];

export default function Nav() {
  const { path } = useLocation();
  const [places, setPlaces] = useState<{ code: string; name: string }[]>([]);
  const [indicators, setIndicators] = useState<IndicatorMeta[]>([]);
  const [query, setQuery] = useState("");
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    api.districts().then((d) => setPlaces(d.features.map((f) => f.properties).sort((a, b) => a.name.localeCompare(b.name)))).catch(() => {});
    api.indicators().then(setIndicators).catch(() => {});
  }, []);

  const search = (e: FormEvent) => {
    e.preventDefault();
    const q = query.trim().toLowerCase();
    if (!q) return;
    const place = places.find((p) => p.name.toLowerCase() === q) ?? places.find((p) => p.name.toLowerCase().startsWith(q));
    if (place) return go(`/place/${place.code}`);
    const ind = indicators.find((i) => i.name.toLowerCase() === q) ?? indicators.find((i) => i.name.toLowerCase().includes(q));
    if (ind) return go(`/explore?i=${ind.code}`);
    setMissing(true);
  };
  const go = (to: string) => {
    setQuery("");
    setMissing(false);
    navigate(to);
  };

  return (
    <header className="topbar">
      <Link to="/" className="brand">RIDIP</Link>
      <nav aria-label="Main">
        {LINKS.map((l) => (
          <Link key={l.to} to={l.to} className={(l.to === "/" ? path === "/" : path.startsWith(l.to)) ? "active" : undefined}>
            {l.label}
          </Link>
        ))}
      </nav>
      <form className="search" onSubmit={search} role="search">
        <input
          list="search-options"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setMissing(false);
          }}
          placeholder="Search a district or indicator"
          aria-label="Search a district or indicator"
          aria-invalid={missing}
        />
        <datalist id="search-options">
          {places.map((p) => <option key={p.code} value={p.name} />)}
          {indicators.map((i) => <option key={i.code} value={i.name} />)}
        </datalist>
        {missing && <span className="search-miss" role="status">No match</span>}
      </form>
    </header>
  );
}
