import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

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
  login: (email: string, password: string) => Promise<boolean>;
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

  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      // Simulação de login - em produção seria uma chamada para API
      if (email && password) {
        let mockUser: User;

        if (email.includes('admin') || email.includes('sec')) {
          mockUser = {
            id: '1',
            name: 'Zezinho Correa',
            email: email,
            profile: 'admin',
            city: 'Manaus',
            state: 'AM',
            loginTime: new Date().toLocaleString('pt-BR'),
            onlineTime: '2h 15min'
          };
        } else {
          mockUser = {
            id: '2',
            name: email.split('@')[0],
            email: email,
            profile: 'user',
            type: email.includes('pj') ? 'PJ' : 'PF',
            status: 'approved',
            city: 'Manaus',
            state: 'AM',
            loginTime: new Date().toLocaleString('pt-BR'),
            onlineTime: '45min'
          };
        }

        setUser(mockUser);
        localStorage.setItem('sec-user', JSON.stringify(mockUser));
        setLoading(false);
        return true;
      }
      setLoading(false);
      return false;
    } catch (error) {
      console.error('Erro no login:', error);
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('sec-user');
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
