import React, { createContext, useContext, useState, type ReactNode } from 'react';

export interface PessoaFisica {
  id: string;
  cpf: string;
  nome: string;
  dataNascimento: string;
  email: string;
  telefone: string;
  celular: string;
  endereco: {
    cep: string;
    logradouro: string;
    numero: string;
    complemento?: string;
    bairro: string;
    cidade: string;
    estado: string;
    pais: string;
  };
  profissao: string;
  estadoCivil: 'solteiro' | 'casado' | 'divorciado' | 'viuvo' | 'separado';
  nacionalidade: string;
  naturalidade: {
    cidade: string;
    estado: string;
    pais: string;
  };
  documentos: {
    rg: string;
    orgaoExpedidor: string;
    dataExpedicao: string;
    tituloEleitor?: string;
    carteiraTrabalho?: string;
    certificadoReservista?: string;
  };
  informacoesCulturais: {
    areaAtuacao: string[];
    experiencia: string;
    formacao: string;
    interesses: string[];
    disponibilidade: string;
  };
  situacao: 'ativo' | 'inativo' | 'pendente';
  dataCadastro: string;
  dataAtualizacao: string;
  observacoes?: string;
}

interface PessoaFisicaContextType {
  pessoasFisicas: PessoaFisica[];
  loading: boolean;
  error: string | null;
  criarPessoaFisica: (pessoa: Omit<PessoaFisica, 'id' | 'dataCadastro' | 'dataAtualizacao'>) => Promise<void>;
  atualizarPessoaFisica: (id: string, pessoa: Partial<PessoaFisica>) => Promise<void>;
  deletarPessoaFisica: (id: string) => Promise<void>;
  buscarPessoaFisica: (id: string) => PessoaFisica | undefined;
  buscarPessoasPorFiltro: (filtro: Partial<PessoaFisica>) => PessoaFisica[];
}

const PessoaFisicaContext = createContext<PessoaFisicaContextType | undefined>(undefined);

// Dados mock para desenvolvimento
const pessoasFisicasMock: PessoaFisica[] = [
  {
    id: '1',
    cpf: '123.456.789-00',
    nome: 'Maria Silva Santos',
    dataNascimento: '1985-03-15',
    email: 'maria.silva@email.com',
    telefone: '(11) 3456-7890',
    celular: '(11) 99876-5432',
    endereco: {
      cep: '01310-100',
      logradouro: 'Rua Augusta',
      numero: '1234',
      complemento: 'Sala 56',
      bairro: 'Consolação',
      cidade: 'São Paulo',
      estado: 'SP',
      pais: 'Brasil'
    },
    profissao: 'Artista Plástica',
    estadoCivil: 'casado',
    nacionalidade: 'Brasileira',
    naturalidade: {
      cidade: 'São Paulo',
      estado: 'SP',
      pais: 'Brasil'
    },
    documentos: {
      rg: '12.345.678-9',
      orgaoExpedidor: 'SSP-SP',
      dataExpedicao: '2005-06-15',
      tituloEleitor: '1234.5678.9012',
      carteiraTrabalho: '12345678-90'
    },
    informacoesCulturais: {
      areaAtuacao: ['Artes Visuais', 'Pintura', 'Escultura'],
      experiencia: '15 anos de experiência em artes plásticas, com participação em diversas exposições coletivas e individuais.',
      formacao: 'Bacharelado em Artes Visuais pela USP, Especialização em Pintura Contemporânea.',
      interesses: ['Arte Contemporânea', 'Arte Digital', 'Curadoria', 'Educação Artística'],
      disponibilidade: 'Meio período, finais de semana e feriados.'
    },
    situacao: 'ativo',
    dataCadastro: '2024-01-15',
    dataAtualizacao: '2024-01-15',
    observacoes: 'Artista premiada em diversos salões de arte regionais.'
  },
  {
    id: '2',
    cpf: '987.654.321-00',
    nome: 'João Oliveira Costa',
    dataNascimento: '1978-11-22',
    email: 'joao.costa@email.com',
    telefone: '(21) 2567-8901',
    celular: '(21) 98765-4321',
    endereco: {
      cep: '20040-020',
      logradouro: 'Rua da Carioca',
      numero: '567',
      bairro: 'Centro',
      cidade: 'Rio de Janeiro',
      estado: 'RJ',
      pais: 'Brasil'
    },
    profissao: 'Músico',
    estadoCivil: 'solteiro',
    nacionalidade: 'Brasileira',
    naturalidade: {
      cidade: 'Rio de Janeiro',
      estado: 'RJ',
      pais: 'Brasil'
    },
    documentos: {
      rg: '98.765.432-1',
      orgaoExpedidor: 'SSP-RJ',
      dataExpedicao: '1998-12-10',
      tituloEleitor: '5678.9012.3456'
    },
    informacoesCulturais: {
      areaAtuacao: ['Música', 'Composição', 'Arranjo'],
      experiencia: '20 anos como músico profissional, com experiência em bandas, orquestras e produções musicais.',
      formacao: 'Conservatório Brasileiro de Música, Curso de Composição e Arranjo.',
      interesses: ['Música Popular Brasileira', 'Jazz', 'Música Clássica', 'Produção Musical'],
      disponibilidade: 'Tempo integral, disponível para viagens.'
    },
    situacao: 'ativo',
    dataCadastro: '2024-02-10',
    dataAtualizacao: '2024-02-10'
  }
];

export const PessoaFisicaProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [pessoasFisicas, setPessoasFisicas] = useState<PessoaFisica[]>(pessoasFisicasMock);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const criarPessoaFisica = async (pessoaData: Omit<PessoaFisica, 'id' | 'dataCadastro' | 'dataAtualizacao'>) => {
    setLoading(true);
    setError(null);

    try {
      const novaPessoa: PessoaFisica = {
        ...pessoaData,
        id: Date.now().toString(),
        dataCadastro: new Date().toISOString().split('T')[0],
        dataAtualizacao: new Date().toISOString().split('T')[0]
      };

      setPessoasFisicas(prev => [...prev, novaPessoa]);
    } catch (err) {
      setError('Erro ao criar pessoa física');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const atualizarPessoaFisica = async (id: string, pessoaData: Partial<PessoaFisica>) => {
    setLoading(true);
    setError(null);

    try {
      setPessoasFisicas(prev => prev.map(pessoa =>
        pessoa.id === id
          ? { ...pessoa, ...pessoaData, dataAtualizacao: new Date().toISOString().split('T')[0] }
          : pessoa
      ));
    } catch (err) {
      setError('Erro ao atualizar pessoa física');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deletarPessoaFisica = async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      setPessoasFisicas(prev => prev.filter(pessoa => pessoa.id !== id));
    } catch (err) {
      setError('Erro ao deletar pessoa física');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const buscarPessoaFisica = (id: string): PessoaFisica | undefined => {
    return pessoasFisicas.find(pessoa => pessoa.id === id);
  };

  const buscarPessoasPorFiltro = (filtro: Partial<PessoaFisica>): PessoaFisica[] => {
    return pessoasFisicas.filter(pessoa => {
      return Object.entries(filtro).every(([key, value]) => {
        if (typeof value === 'string') {
          return pessoa[key as keyof PessoaFisica]?.toString().toLowerCase().includes(value.toLowerCase());
        }
        if (typeof value === 'object' && value !== null) {
          return JSON.stringify(pessoa[key as keyof PessoaFisica]).includes(JSON.stringify(value));
        }
        return pessoa[key as keyof PessoaFisica] === value;
      });
    });
  };

  const value: PessoaFisicaContextType = {
    pessoasFisicas,
    loading,
    error,
    criarPessoaFisica,
    atualizarPessoaFisica,
    deletarPessoaFisica,
    buscarPessoaFisica,
    buscarPessoasPorFiltro
  };

  return (
    <PessoaFisicaContext.Provider value={value}>
      {children}
    </PessoaFisicaContext.Provider>
  );
};

export const usePessoaFisica = () => {
  const context = useContext(PessoaFisicaContext);
  if (context === undefined) {
    throw new Error('usePessoaFisica must be used within a PessoaFisicaProvider');
  }
  return context;
};
