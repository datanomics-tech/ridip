import type { Feature, FeatureCollection, MultiPolygon } from "geojson";

export type DistrictProperties = {
  code: string;
  name: string;
  province: string;
};

export type DistrictFeature = Feature<MultiPolygon, DistrictProperties>;
export type DistrictCollection = FeatureCollection<MultiPolygon, DistrictProperties>;

export type Indicator = {
  code: string;
  name: string;
  unit: string;
  description: string | null;
  source: string;
  source_url: string | null;
  years: number[];
  national: Record<string, number>;
  districts: Record<string, Record<string, number>>;
};
