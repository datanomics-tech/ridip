import type { Feature, Geometry } from "geojson";
import type { Layer, LeafletMouseEvent, PathOptions } from "leaflet";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import type { DistrictCollection, DistrictProperties } from "./types";

type MapFeature = Feature<Geometry, DistrictProperties>;

type Props = {
  districts: DistrictCollection;
  colour: (code: string) => string;
  tooltip: (code: string, name: string) => string;
  selected: string | null;
  onSelect: (code: string) => void;
  /** Changes whenever the colours change, so the map redraws. */
  version: string;
  height?: number;
};

export default function DistrictMap({ districts, colour, tooltip, selected, onSelect, version, height }: Props) {
  const style = (feature?: MapFeature): PathOptions => {
    const code = feature?.properties.code ?? "";
    const isSelected = code === selected;
    return {
      color: isSelected ? "#0B2545" : "#FFFFFF",
      weight: isSelected ? 4 : 1.2,
      fillColor: colour(code),
      fillOpacity: 0.85,
    };
  };

  const onEachFeature = (feature: MapFeature, layer: Layer) => {
    layer.bindTooltip(tooltip(feature.properties.code, feature.properties.name), { sticky: true });
    layer.on({
      click: (e: LeafletMouseEvent) => {
        onSelect(feature.properties.code);
        e.originalEvent.stopPropagation();
      },
    });
  };

  return (
    <MapContainer
      center={[-1.95, 29.9]}
      zoom={9}
      minZoom={8}
      className="map"
      style={height ? { height } : undefined}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON key={`${version}-${selected ?? "none"}`} data={districts} style={style} onEachFeature={onEachFeature} />
    </MapContainer>
  );
}
