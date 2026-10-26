import type { Feature, Geometry } from "geojson";
import type { Layer, LeafletMouseEvent, PathOptions } from "leaflet";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import { colourFor } from "./scale";
import type { DistrictCollection, DistrictProperties } from "./types";

type MapFeature = Feature<Geometry, DistrictProperties>;

type Props = {
  districts: DistrictCollection;
  values: Record<string, number>;
  selected: string | null;
  onSelect: (code: string) => void;
};

export default function DistrictMap({ districts, values, selected, onSelect }: Props) {
  const style = (feature?: MapFeature): PathOptions => {
    const code = feature?.properties.code ?? "";
    const isSelected = code === selected;
    return {
      color: isSelected ? "#0B2545" : "#FFFFFF",
      weight: isSelected ? 4 : 1.2,
      fillColor: colourFor(values[code]),
      fillOpacity: 0.85,
    };
  };

  const onEachFeature = (feature: MapFeature, layer: Layer) => {
    const value = values[feature.properties.code];
    const label = value === undefined ? "no data" : `${value.toFixed(1)}% poor`;
    layer.bindTooltip(`<strong>${feature.properties.name}</strong><br>${label}`, { sticky: true });
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
      <GeoJSON
        key={`${selected ?? "none"}-${Object.keys(values).length}`}
        data={districts}
        style={style}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
}
