import type { Feature, FeatureCollection, MultiPolygon } from "geojson";

export type DistrictProperties = {
  code: string;
  name: string;
  province: string;
};

export type DistrictFeature = Feature<MultiPolygon, DistrictProperties>;
export type DistrictCollection = FeatureCollection<MultiPolygon, DistrictProperties>;
