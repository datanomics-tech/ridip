import type { DistrictCollection, DomainInfo, Domain, IndicatorData, IndicatorMeta, Overview, Profile } from "./types";

const cache = new Map<string, Promise<unknown>>();

export function getJson<T>(url: string): Promise<T> {
  if (!cache.has(url)) {
    const request = fetch(url).then((res) => {
      if (!res.ok) throw new Error(`${url} returned ${res.status}`);
      return res.json();
    });
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
};
