import type { Feature, Geometry } from "geojson";
import type { Layer, LeafletMouseEvent, PathOptions } from "leaflet";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import type { DistrictCollection, DistrictProperties } from "./types";

type MapFeature = Feature<Geometry, DistrictProperties>;

// One colour per province, so the five provinces are easy to tell apart.
export const PROVINCE_COLOURS: Record<string, string> = {
  "City of Kigali": "#0B2545",
  Eastern: "#1565C0",
  Northern: "#00838F",
  Southern: "#2E7D32",
  Western: "#6A1B9A",
};

type Props = {
  districts: DistrictCollection;
  selected: string | null;
  onSelect: (code: string) => void;
};

export default function DistrictMap({ districts, selected, onSelect }: Props) {
  const style = (feature?: MapFeature): PathOptions => {
    const isSelected = feature?.properties.code === selected;
    return {
      color: isSelected ? "#FAD201" : "#FFFFFF",
      weight: isSelected ? 4 : 1.2,
      fillColor: PROVINCE_COLOURS[feature?.properties.province ?? ""] ?? "#888888",
      fillOpacity: isSelected ? 0.85 : 0.55,
    };
  };

  const onEachFeature = (feature: MapFeature, layer: Layer) => {
    layer.bindTooltip(`${feature.properties.name} (${feature.properties.province})`, { sticky: true });
    layer.on({
      click: (e: LeafletMouseEvent) => {
        onSelect(feature.properties.code);
        e.originalEvent.stopPropagation();
      },
    });
  };

  return (
    <MapContainer center={[-1.95, 29.9]} zoom={9} minZoom={8} className="map" scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON key={selected ?? "none"} data={districts} style={style} onEachFeature={onEachFeature} />
    </MapContainer>
  );
}
