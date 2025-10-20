import type { CourseItem } from '../types/catalog';

export const courses: CourseItem[] = [
  {
    id: 'cu1',
    title: 'Produção Cultural para Iniciantes',
    level: 'iniciante',
    mode: 'online',
    description: 'Curso introdutório cobrindo conceitos básicos de produção cultural.',
    syllabus: ['Introdução', 'Gestão de projetos', 'Captação de recursos', 'Comunicação'],
    enrollmentOpen: true,
  },
  {
    id: 'cu2',
    title: 'Curadoria de Arte Contemporânea',
    level: 'intermediario',
    mode: 'presencial',
    description: 'Curso focado em curadoria e montagem de exposições.',
    syllabus: ['História da arte', 'Curadoria', 'Montagem', 'Mediação'],
    enrollmentOpen: false,
  },
];