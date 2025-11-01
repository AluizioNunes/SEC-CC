import axios from 'axios';

export interface LoginPayload {
  username: string; // pode ser usuário (Login) ou e-mail (Email)
  password: string;
}

export interface LoginUserInfo {
  id: number | string;
  name: string | null;
  email: string | null;
  login: string | null;
  profile: string | null; // Perfil
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: LoginUserInfo;
}

// Detecta ambiente de desenvolvimento (Vite) e aponta direto para o FastAPI
const isDev = typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.DEV;
const port = typeof window !== 'undefined' ? window.location.port : '';
const isViteDevPort = port.startsWith('517');
const baseURL = (isDev || isViteDevPort) ? '/api' : '/api/v1';

export const authApi = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

export const AuthApi = {
  async login(payload: LoginPayload): Promise<LoginResponse> {
    const { data } = await authApi.post<LoginResponse>('/auth/login', payload);
    return data;
  },
};