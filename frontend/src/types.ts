import type { Feature, FeatureCollection, MultiPolygon } from "geojson";

export type DistrictProperties = { code: string; name: string; province: string };
export type DistrictFeature = Feature<MultiPolygon, DistrictProperties>;
export type DistrictCollection = FeatureCollection<MultiPolygon, DistrictProperties>;

export type Domain = "finance_poverty" | "agriculture" | "employment";
export const DOMAIN_ORDER: Domain[] = ["agriculture", "finance_poverty", "employment"];   // track 1, 2, 3

export type DomainInfo = { title: string; track: string; question: string; nst2: string };

export type IndicatorMeta = {
  code: string;
  domain: Domain;
  name: string;
  unit: string;
  direction: "higher" | "lower";
  source: string;
  source_url: string | null;
  note: string | null;
  value_type: string;
  years: number[];
};

export type IndicatorData = IndicatorMeta & {
  national: Record<string, number>;
  districts: Record<string, Record<string, number>>;
  se: Record<string, Record<string, number>>;
};

export type Point = { year: number; value: number };

export type ProfileIndicator = {
  code: string;
  name: string;
  unit: string;
  direction: "higher" | "lower";
  source: string;
  value_type: string;
  year: number;
  value: number;
  se: number | null;
  national: number | null;
  gap: number | null;
  rank: number | null;
  rank_of: number;
  significance: string | null;
  z: number | null;
  trend: Point[];
  national_trend: Point[];
};

export type ProfileTrack = DomainInfo & {
  need: number | null;
  need_rank: number | null;
  need_of: number;
  note: string | null;
  indicators: ProfileIndicator[];
};

export type Insight = { track: Domain; level: string; text: string; indicators: string[] };

export type Profile = {
  code: string;
  name: string;
  province: string;
  tracks: Record<Domain, ProfileTrack>;
  insights: Insight[];
  group: { name: string; label: string; peers: string[] };
};

export type Overview = {
  tracks: Record<Domain, DomainInfo & { need: Record<string, number>; priority: { code: string; name: string; need: number }[] }>;
  groups: { id: number; name: string; label: string; need: Record<Domain, number | null>; members: { code: string; name: string }[] }[];
  group_of: Record<string, string>;
};
