import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { AuthApi } from '../services/authApi';

export interface User {
  id: string;
  name: string;
  email: string;
  profile: 'public' | 'user' | 'admin';
  type?: 'PF' | 'PJ';
  status?: 'pending' | 'approved' | 'rejected' | 'suspended';
  city?: string;
  state?: string;
  loginTime?: string;
  onlineTime?: string;
}

interface AuthContextType {
  user: User | null;
  login: (identifier: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar se há usuário salvo no localStorage
    const savedUser = localStorage.getItem('sec-user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        localStorage.removeItem('sec-user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (identifier: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      if (!identifier || !password) {
        setLoading(false);
        return false;
      }

      const resp = await AuthApi.login({ username: identifier, password });

      // Converter resposta da API para o modelo de User utilizado pelo app
      const loggedUser: User = {
        id: String(resp.user?.id ?? ''),
        name: String(resp.user?.name ?? ''),
        email: String(resp.user?.email ?? ''),
        profile: (resp.user?.profile as User['profile']) ?? 'user',
        loginTime: new Date().toLocaleString('pt-BR'),
      };

      setUser(loggedUser);
      localStorage.setItem('sec-user', JSON.stringify(loggedUser));
      localStorage.setItem('sec-token', resp.access_token);
      localStorage.setItem('sec-refresh-token', resp.refresh_token);
      setLoading(false);
      return true;
    } catch (error) {
      console.error('Erro no login:', error);
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('sec-user');
    localStorage.removeItem('sec-token');
    localStorage.removeItem('sec-refresh-token');
    // Não usar navigate aqui - será tratado pelo componente que chamar logout
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
