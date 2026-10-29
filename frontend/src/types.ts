import type { Feature, FeatureCollection, MultiPolygon } from "geojson";

export type DistrictProperties = { code: string; name: string; province: string };
export type DistrictFeature = Feature<MultiPolygon, DistrictProperties>;
export type DistrictCollection = FeatureCollection<MultiPolygon, DistrictProperties>;

export type Domain = "agriculture" | "finance_poverty" | "employment" | "health" | "education" | "transport";
// Track 1, Track 2, then the four Open Innovation sectors (Track 3)
export const DOMAIN_ORDER: Domain[] = ["agriculture", "finance_poverty", "employment", "health", "education", "transport"];
export const OPEN_INNOVATION: Domain[] = ["employment", "health", "education", "transport"];

export type DomainInfo = { title: string; track: string; question: string; decision: string; nst2: string };

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

export type Target = {
  value: number; baseline: number; year: number; level: string; label: string; source: string; source_url: string; distance: number;
};

export type ProfileIndicator = {
  code: string;
  name: string;
  unit: string;
  direction: "higher" | "lower";
  source: string;
  source_url: string | null;
  note: string | null;
  value_type: string;
  scored: boolean;
  excluded_reason: string | null;
  target: Target | null;
  year: number;
  value: number;
  se: number | null;
  national: number | null;
  gap: number | null;
  rank: number | null;
  rank_of: number;
  difference_flag: "above" | "below" | "no clear difference" | null;
  z: number | null;
  trend: Point[];
  national_trend: Point[];
};

export type ProfileTrack = DomainInfo & {
  years: number[];
  rank_range: [number, number] | null;
  rank_stable: boolean | null;
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
  tracks: Record<Domain, DomainInfo & { need: Record<string, number>; priority: { code: string; name: string; need: number; rank_stable: boolean }[] }>;
  groups: { id: number; name: string; label: string; need: Record<Domain, number | null>; members: { code: string; name: string }[] }[];
  group_of: Record<string, string>;
};

export type Evidence = {
  code: string; name: string; value: number; national: number | null; gap: number | null; unit: string; year: number;
  source: string; source_url: string | null; difference_flag: string | null; value_type: string;
};

export type Brief = {
  version: string; district: string; code: string; province: string; sector: string; track: string; purpose: string;
  need: number | null; need_rank: number | null; need_of: number; level: string; rank_range: [number, number] | null;
  statements: { rule_id: string; text: string; evidence: Evidence[] }[];
  planning_question: string; follow_up: string[]; caveats: string[]; nst2: string;
  group: { name: string; label: string; peers: string[] };
};

export type Method = {
  weighting: string; orientation: string; tie_policy: string; coverage: string; zero_variance: string; kigali_rule: string;
  difference_flag: string; stable_rule: string;
  excluded: { code: string; name: string; reason: string }[];
  source_years: Record<string, number[]>;
  sensitivity: Record<string, { indicators: number; min_top5_overlap: number; share_of_districts_stable: number;
    scenarios: { left_out: string; left_out_name: string; top5_overlap: number; max_move: number; mean_move: number }[] }>;
  targets: Record<string, Omit<Target, "distance">>;
};
