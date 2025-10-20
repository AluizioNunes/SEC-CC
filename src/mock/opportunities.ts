import type { Opportunity } from '../types/catalog';

export const opportunities: Opportunity[] = [
  {
    id: 'op1',
    title: 'Edital de Fomento à Música 2025',
    category: 'edital',
    status: 'aberto',
    period: { start: '2025-11-01', end: '2025-12-15' },
    tags: ['música', 'produção', 'circulação'],
    highlight: true,
    description: 'Financiamento de projetos musicais com foco em circulação nacional e internacional.',
    requirements: ['CNPJ ou CPF', 'Projeto detalhado', 'Comprovante de residência'],
    timeline: [
      { label: 'Abertura', date: '2025-11-01' },
      { label: 'Encerramento', date: '2025-12-15' },
      { label: 'Resultado', date: '2026-01-10' },
    ],
    documents: [
      { name: 'Edital completo (PDF)', url: '#' },
      { name: 'Modelo de Projeto (DOCX)', url: '#' },
    ],
  },
  {
    id: 'op2',
    title: 'Prêmio de Literatura Contemporânea',
    category: 'premio',
    status: 'inscricoes',
    period: { start: '2025-10-20', end: '2025-11-30' },
    tags: ['literatura', 'premiação'],
    description: 'Reconhecimento de obras originais com premiação em dinheiro e publicação.',
    requirements: ['Obra inédita', 'Cadastro de autor', 'Termo de cessão'],
    timeline: [
      { label: 'Início das inscrições', date: '2025-10-20' },
      { label: 'Encerramento', date: '2025-11-30' },
      { label: 'Cerimônia', date: '2025-12-20' },
    ],
    documents: [
      { name: 'Regulamento (PDF)', url: '#' },
    ],
  },
  {
    id: 'op3',
    title: 'Oficina de Produção Cultural',
    category: 'oficina',
    status: 'breve',
    period: { start: '2026-01-15', end: '2026-01-20' },
    tags: ['formação', 'gestão cultural'],
    description: 'Oficina prática para produtores culturais com certificação.',
    requirements: ['CPF', 'Carta de motivação'],
    timeline: [
      { label: 'Inscrições', date: '2025-12-10' },
      { label: 'Início', date: '2026-01-15' },
    ],
    documents: [
      { name: 'Programa da Oficina (PDF)', url: '#' },
    ],
  },
];