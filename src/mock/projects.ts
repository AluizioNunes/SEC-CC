import type { ProjectItem } from '../types/catalog';

export const projects: ProjectItem[] = [
  {
    id: 'pr1',
    title: 'Instalação Interativa: Luz e Som',
    area: 'artes',
    phase: 'execucao',
    results: ['Workshop realizado', 'Parcerias locais firmadas'],
    agentIds: ['ag1'],
    spaceIds: ['sp2'],
    description: 'Instalação que explora sensações táteis com luz e som responsivo ao movimento.',
  },
  {
    id: 'pr2',
    title: 'Circuito Musical Amazônico',
    area: 'musica',
    phase: 'planejamento',
    results: [],
    agentIds: ['ag2'],
    spaceIds: ['sp1'],
    description: 'Projeto de circulação musical por espaços culturais da região amazônica.',
  },
];