import React from 'react';

interface MapEmbedProps {
  lat: number;
  lng: number;
  width?: number | string;
  height?: number | string;
  zoom?: number;
}

// Embed simples do OpenStreetMap sem dependências externas
const MapEmbed: React.FC<MapEmbedProps> = ({ lat, lng, width = '100%', height = 320, zoom = 14 }) => {
  const delta = 0.02; // bbox pequeno ao redor do ponto
  const left = lng - delta;
  const right = lng + delta;
  const top = lat + delta;
  const bottom = lat - delta;
  const bbox = `${left}%2C${bottom}%2C${right}%2C${top}`;
  const marker = `${lat}%2C${lng}`;
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${marker}`;

  return (
    <iframe
      title={`map-${lat}-${lng}`}
      width={typeof width === 'number' ? `${width}px` : width}
      height={typeof height === 'number' ? `${height}px` : `${height}`}
      frameBorder="0"
      scrolling="no"
      marginHeight={0}
      marginWidth={0}
      src={src}
      style={{ border: '1px solid #ddd', borderRadius: 8 }}
    />
  );
};

export default MapEmbed;