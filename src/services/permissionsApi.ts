import axios from 'axios';

export type ActionsPermission = {
  view: boolean;
  create: boolean;
  edit: boolean;
  delete: boolean;
};

export type PermissionMatrixOut = {
  screens: {
    usuarios: ActionsPermission;
    perfil: ActionsPermission;
    permissoes: ActionsPermission;
  };
};

export interface UserPermissionsResponse {
  userId: number;
  profiles: { id: number | string; name: string }[];
  raw: { nome: string; modulo?: string | null; tipo?: string | null }[];
  matrix: PermissionMatrixOut;
}

const isDev = typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.DEV;
const port = typeof window !== 'undefined' ? window.location.port : '';
const isViteDevPort = port.startsWith('517');
const baseURL = (isDev || isViteDevPort) ? '/api' : '/api/v1';

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

export const PermissionsApi = {
  async getForUser(userId: number | string): Promise<UserPermissionsResponse> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('sec-token') : null;
    const { data } = await api.get<UserPermissionsResponse>(`/permissoes/usuarios/${userId}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
    return data;
  },
};