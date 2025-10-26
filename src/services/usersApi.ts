import axios from 'axios';

export interface UsuarioRecord {
  IdUsuario: number;
  Nome: string | null;
  Funcao?: string | null;
  Departamento?: string | null;
  Lotacao?: string | null;
  Perfil?: string | null;
  Permissao?: string | null;
  Email?: string | null;
  Login?: string | null;
  Senha?: string | null;
  DataCadastro?: string | null;
  Cadastrante?: string | null;
  Image?: string | null;
  DataUpdate?: string | null;
  TipoUpdate?: string | null;
  Observacao?: string | null;
}

export interface UsuarioCreatePayload {
  Nome: string;
  Funcao?: string;
  Departamento?: string;
  Lotacao?: string;
  Perfil?: string;
  Permissao?: string;
  Email?: string;
  Login?: string;
  Senha?: string;
  Cadastrante?: string;
  Image?: string;
  TipoUpdate?: string;
  Observacao?: string;
}

export interface UsuarioUpdatePayload {
  Nome?: string;
  Funcao?: string;
  Departamento?: string;
  Lotacao?: string;
  Perfil?: string;
  Permissao?: string;
  Email?: string;
  Login?: string;
  Senha?: string;
  Cadastrante?: string;
  Image?: string;
  TipoUpdate?: string;
  Observacao?: string;
}

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export const UsersApi = {
  async list(): Promise<UsuarioRecord[]> {
    const { data } = await api.get<UsuarioRecord[]>('/usuarios/');
    return data;
  },
  async create(payload: UsuarioCreatePayload): Promise<UsuarioRecord> {
    const { data } = await api.post<UsuarioRecord>('/usuarios/', payload);
    return data;
  },
  async update(id: number, payload: UsuarioUpdatePayload): Promise<UsuarioRecord> {
    const { data } = await api.put<UsuarioRecord>(`/usuarios/${id}`, payload);
    return data;
  },
  async remove(id: number): Promise<{ ok: boolean }> {
    const { data } = await api.delete<{ ok: boolean }>(`/usuarios/${id}`);
    return data;
  },
};