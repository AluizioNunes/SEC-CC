export type OpportunityCategory = 'edital' | 'premio' | 'oficina';
export type OpportunityStatus = 'aberto' | 'inscricoes' | 'breve' | 'encerrado';

export interface Opportunity {
  id: string;
  title: string;
  category: OpportunityCategory;
  status: OpportunityStatus;
  period: { start: string; end: string };
  tags: string[];
  highlight?: boolean;
  description: string;
  requirements: string[];
  timeline: { label: string; date: string }[];
  documents: { name: string; url?: string }[];
}

export type EventType = 'show' | 'exposicao' | 'teatro' | 'workshop';

export interface EventItem {
  id: string;
  title: string;
  type: EventType;
  dateRange: { start: string; end: string };
  description: string;
  tags: string[];
  location: { city: string; country: string; address?: string; lat: number; lng: number };
}

export type SpaceType = 'teatro' | 'galeria' | 'biblioteca' | 'centro_cultural';

export interface SpaceItem {
  id: string;
  name: string;
  type: SpaceType;
  services: string[];
  photos: string[];
  hours: { day: string; open: string; close: string }[];
  contact: { phone?: string; email?: string; website?: string };
  location: { city: string; country: string; address?: string; lat: number; lng: number };
  agendaEvents: string[]; // event ids
}

export type AgentRole = 'artista' | 'produtor' | 'pesquisador';

export interface AgentItem {
  id: string;
  name: string;
  role: AgentRole;
  bio: string;
  location: { city: string; country: string };
  avatar?: string;
  portfolio: string[]; // image urls
  projectIds: string[];
}

export type ProjectArea = 'musica' | 'artes' | 'literatura' | 'teatro' | 'cinema' | 'fotografia';
export type ProjectPhase = 'planejamento' | 'execucao' | 'concluido';

export interface ProjectItem {
  id: string;
  title: string;
  area: ProjectArea;
  phase: ProjectPhase;
  results: string[];
  agentIds: string[];
  spaceIds: string[];
  description: string;
}

export type CourseLevel = 'iniciante' | 'intermediario' | 'avancado';
export type CourseMode = 'online' | 'presencial';

export interface CourseItem {
  id: string;
  title: string;
  level: CourseLevel;
  mode: CourseMode;
  description: string;
  syllabus: string[];
  enrollmentOpen: boolean;
}