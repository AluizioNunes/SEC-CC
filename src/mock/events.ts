import type { EventItem } from '../types/catalog';

export const events: EventItem[] = [
  {
    id: 'ev1',
    title: 'Show de Jazz Internacional',
    type: 'show',
    dateRange: { start: '2025-11-25T20:00:00', end: '2025-11-25T22:00:00' },
    description: 'Apresentação com artistas convidados de diversos países.',
    tags: ['música', 'internacional'],
    location: { city: 'Manaus', country: 'Brasil', address: 'Teatro XYZ', lat: -3.131, lng: -60.023 },
  },
  {
    id: 'ev2',
    title: 'Exposição de Arte Contemporânea',
    type: 'exposicao',
    dateRange: { start: '2025-12-01', end: '2026-01-15' },
    description: 'Exposição com curadoria internacional e obras interativas.',
    tags: ['artes visuais', 'interativo'],
    location: { city: 'São Paulo', country: 'Brasil', address: 'Galeria ABC', lat: -23.551, lng: -46.633 },
  },
  {
    id: 'ev3',
    title: 'Festival de Teatro Popular',
    type: 'teatro',
    dateRange: { start: '2026-02-10', end: '2026-02-14' },
    description: 'Festival com peças autorais e oficinas de atuação.',
    tags: ['teatro', 'festival'],
    location: { city: 'Lisboa', country: 'Portugal', address: 'Centro Cultural DEF', lat: 38.7223, lng: -9.1393 },
  },
];