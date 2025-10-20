import type { AgentItem } from '../types/catalog';

export const agents: AgentItem[] = [
  {
    id: 'ag1',
    name: 'Ana Souza',
    role: 'artista',
    bio: 'Artista visual com foco em instalações interativas e arte pública.',
    location: { city: 'Rio de Janeiro', country: 'Brasil' },
    avatar: 'https://picsum.photos/seed/ana/200/200',
    portfolio: [
      'https://picsum.photos/seed/ana1/600/400',
      'https://picsum.photos/seed/ana2/600/400',
      'https://picsum.photos/seed/ana3/600/400',
    ],
    projectIds: ['pr1'],
  },
  {
    id: 'ag2',
    name: 'Carlos Mendes',
    role: 'produtor',
    bio: 'Produtor cultural com experiência em festivais e circulação nacional.',
    location: { city: 'São Paulo', country: 'Brasil' },
    avatar: 'https://picsum.photos/seed/carlos/200/200',
    portfolio: [
      'https://picsum.photos/seed/carlos1/600/400',
      'https://picsum.photos/seed/carlos2/600/400',
    ],
    projectIds: ['pr2'],
  },
];