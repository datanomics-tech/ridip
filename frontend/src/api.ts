import type { Brief, DistrictCollection, DomainInfo, Domain, IndicatorData, IndicatorMeta, Method, Overview, Profile } from "./types";

const cache = new Map<string, Promise<unknown>>();

// The free server sleeps after 15 minutes without visitors and takes up to a minute to wake.
// Requests that fail while it wakes (network error, 502/503/504) are retried, and a banner explains the wait.
type Status = "ok" | "waking" | "down";
let status: Status = "ok";
let waiting = 0;                       // requests currently slow or retrying
const statusListeners = new Set<(s: Status) => void>();
function setStatus(s: Status) {
  status = s;
  statusListeners.forEach((l) => l(s));
}
export function onServerStatus(listener: (s: Status) => void): () => void {
  statusListeners.add(listener);
  listener(status);
  return () => { statusListeners.delete(listener); };
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function fetchWithWake(url: string): Promise<unknown> {
  let marked = false;
  const mark = () => {
    if (!marked) { marked = true; waiting++; setStatus("waking"); }
  };
  const timer = setTimeout(mark, 3000);
  try {
    for (let attempt = 0; attempt < 10; attempt++) {
      let res: Response | null = null;
      try {
        res = await fetch(url);
      } catch {
        res = null;                       // network error while the server wakes
      }
      if (res && res.ok) return await res.json();
      if (res && ![502, 503, 504].includes(res.status)) throw new Error(`${url} returned ${res.status}`);
      mark();
      await sleep(6000);
    }
    setStatus("down");
    throw new Error(`${url} could not be reached`);
  } finally {
    clearTimeout(timer);
    if (marked) {
      waiting--;
      if (waiting === 0 && status === "waking") setStatus("ok");
    }
  }
}

export function getJson<T>(url: string): Promise<T> {
  if (!cache.has(url)) {
    const request = fetchWithWake(url);
    request.catch(() => cache.delete(url));
    cache.set(url, request);
  }
  return cache.get(url) as Promise<T>;
}

export const api = {
  districts: () => getJson<DistrictCollection>("/api/districts"),
  domains: () => getJson<Record<Domain, DomainInfo>>("/api/domains"),
  indicators: () => getJson<IndicatorMeta[]>("/api/indicators"),
  indicator: (code: string) => getJson<IndicatorData>(`/api/indicators/${code}`),
  overview: () => getJson<Overview>("/api/overview"),
  place: (code: string) => getJson<Profile>(`/api/places/${code}`),
  brief: (code: string, domain: Domain) => getJson<Brief>(`/api/places/${code}/priority-brief?domain=${domain}`),
  method: () => getJson<Method>("/api/method"),
};
