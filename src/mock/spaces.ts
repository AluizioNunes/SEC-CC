import type { SpaceItem } from '../types/catalog';

export const spaces: SpaceItem[] = [
  {
    id: 'sp1',
    name: 'Teatro XYZ',
    type: 'teatro',
    services: ['acessibilidade', 'estacionamento', 'wifi'],
    photos: [
      'https://picsum.photos/seed/teatroxyz1/800/400',
      'https://picsum.photos/seed/teatroxyz2/800/400',
      'https://picsum.photos/seed/teatroxyz3/800/400',
    ],
    hours: [
      { day: 'Seg-Sex', open: '10:00', close: '18:00' },
      { day: 'Sáb', open: '12:00', close: '20:00' },
    ],
    contact: { phone: '+55 92 99999-9999', email: 'contato@teatroxyz.com', website: 'https://teatroxyz.com' },
    location: { city: 'Manaus', country: 'Brasil', address: 'Av. Cultura, 100', lat: -3.131, lng: -60.023 },
    agendaEvents: ['ev1'],
  },
  {
    id: 'sp2',
    name: 'Galeria ABC',
    type: 'galeria',
    services: ['acessibilidade', 'wifi'],
    photos: [
      'https://picsum.photos/seed/galeriaabc1/800/400',
      'https://picsum.photos/seed/galeriaabc2/800/400',
    ],
    hours: [
      { day: 'Ter-Dom', open: '11:00', close: '19:00' },
    ],
    contact: { email: 'info@galeriaabc.com' },
    location: { city: 'São Paulo', country: 'Brasil', address: 'Rua das Artes, 20', lat: -23.551, lng: -46.633 },
    agendaEvents: ['ev2'],
  },
];