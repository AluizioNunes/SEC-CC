-- Initialize SEC schema and required tables
CREATE SCHEMA IF NOT EXISTS "SEC";

-- ===================== Tabela Usuarios =====================
CREATE TABLE IF NOT EXISTS "SEC"."Usuario" (
  "IdUsuario" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) NOT NULL,
  "Funcao" VARCHAR(255),
  "Departamento" VARCHAR(255),
  "Lotacao" VARCHAR(255),
  "Perfil" VARCHAR(100),
  "Permissao" VARCHAR(100),
  "Email" VARCHAR(255) UNIQUE,
  "Login" VARCHAR(100) UNIQUE,
  "Senha" VARCHAR(255),
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  "Cadastrante" VARCHAR(255),
  "Image" VARCHAR(1024),
  "DataUpdate" TIMESTAMPTZ,
  "TipoUpdate" VARCHAR(100),
  "Observacao" TEXT
);

-- ===================== Tabela Perfil =====================
CREATE TABLE IF NOT EXISTS "SEC"."Perfil" (
  "IdPerfil" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(100) UNIQUE NOT NULL,
  "Descricao" TEXT,
  "Ativo" BOOLEAN DEFAULT TRUE,
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela Permissoes =====================
CREATE TABLE IF NOT EXISTS "SEC"."Permissoes" (
  "IdPermissao" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(100) UNIQUE NOT NULL,
  "Descricao" TEXT,
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela Secretaria =====================
CREATE TABLE IF NOT EXISTS "SEC"."Secretaria" (
  "IdSecretaria" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) UNIQUE NOT NULL,
  "Sigla" VARCHAR(50),
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela Departamentos =====================
CREATE TABLE IF NOT EXISTS "SEC"."Departamentos" (
  "IdDepartamento" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) UNIQUE NOT NULL,
  "SecretariaId" BIGINT REFERENCES "SEC"."Secretaria"("IdSecretaria") ON DELETE SET NULL,
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela Lotacao =====================
CREATE TABLE IF NOT EXISTS "SEC"."Lotacao" (
  "IdLotacao" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) NOT NULL,
  "DepartamentoId" BIGINT REFERENCES "SEC"."Departamentos"("IdDepartamento") ON DELETE SET NULL,
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela Funcionarios =====================
CREATE TABLE IF NOT EXISTS "SEC"."Funcionarios" (
  "IdFuncionario" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) NOT NULL,
  "DepartamentoId" BIGINT REFERENCES "SEC"."Departamentos"("IdDepartamento") ON DELETE SET NULL,
  "LotacaoId" BIGINT REFERENCES "SEC"."Lotacao"("IdLotacao") ON DELETE SET NULL,
  "PerfilId" BIGINT REFERENCES "SEC"."Perfil"("IdPerfil") ON DELETE SET NULL,
  "Email" VARCHAR(255),
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela PF =====================
CREATE TABLE IF NOT EXISTS "SEC"."PF" (
  "IdPF" BIGSERIAL PRIMARY KEY,
  "Nome" VARCHAR(255) NOT NULL,
  "CPF" VARCHAR(14) UNIQUE,
  "DataNascimento" DATE,
  "Email" VARCHAR(255),
  "Telefone" VARCHAR(30),
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ===================== Tabela PJ =====================
CREATE TABLE IF NOT EXISTS "SEC"."PJ" (
  "IdPJ" BIGSERIAL PRIMARY KEY,
  "RazaoSocial" VARCHAR(255) NOT NULL,
  "CNPJ" VARCHAR(18) UNIQUE,
  "NomeFantasia" VARCHAR(255),
  "Email" VARCHAR(255),
  "Telefone" VARCHAR(30),
  "DataCadastro" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);