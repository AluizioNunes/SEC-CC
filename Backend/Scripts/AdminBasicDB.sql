-- =====================================================
-- SCRIPT DE CRIAÇÃO DO SISTEMA ADMINISTRATIVO
-- Database: SEC | Schema: SEC
-- PostgreSQL 17.6
-- =====================================================

-- Criar Database (execute separadamente se necessário)
-- CREATE DATABASE SEC WITH ENCODING 'UTF8';

-- Reset schema para inicialização limpa (primeira execução)
DROP SCHEMA IF EXISTS public CASCADE;
DROP SCHEMA IF EXISTS "SEC" CASCADE;
-- Create schema owned by the current user to avoid psql variable issues
CREATE SCHEMA IF NOT EXISTS "SEC";
-- Use session-level search_path; avoid ALTER ROLE to keep script idempotent
SET search_path TO "SEC";

-- Removed quick-fix Usuario block to avoid duplicate definitions and variable dependencies

-- Enable pgcrypto for bcrypt hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- Ensure uuid-ossp exists in the SEC schema for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA "SEC";

-- Remover o banco padrão 'postgres' (fora de transação)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'postgres' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS postgres;

-- =====================================================
-- FUNÇÕES DE VALIDAÇÃO
-- =====================================================

-- Função para validar CPF
CREATE OR REPLACE FUNCTION "SEC".validar_cpf(cpf VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    cpf_limpo VARCHAR(11);
    soma INTEGER;
    resto INTEGER;
    digito1 INTEGER;
    digito2 INTEGER;
    i INTEGER;
BEGIN
    -- Remove caracteres não numéricos
    cpf_limpo := REGEXP_REPLACE(cpf, '[^0-9]', '', 'g');
    
    -- Verifica se tem 11 dígitos
    IF LENGTH(cpf_limpo) != 11 THEN
        RETURN FALSE;
    END IF;
    
    -- Verifica se todos os dígitos são iguais
    IF cpf_limpo IN ('00000000000', '11111111111', '22222222222', '33333333333',
                     '44444444444', '55555555555', '66666666666', '77777777777',
                     '88888888888', '99999999999') THEN
        RETURN FALSE;
    END IF;
    
    -- Calcula primeiro dígito verificador
    soma := 0;
    FOR i IN 1..9 LOOP
        soma := soma + (SUBSTRING(cpf_limpo, i, 1)::INTEGER * (11 - i));
    END LOOP;
    resto := soma % 11;
    IF resto < 2 THEN
        digito1 := 0;
    ELSE
        digito1 := 11 - resto;
    END IF;
    
    -- Calcula segundo dígito verificador
    soma := 0;
    FOR i IN 1..10 LOOP
        soma := soma + (SUBSTRING(cpf_limpo, i, 1)::INTEGER * (12 - i));
    END LOOP;
    resto := soma % 11;
    IF resto < 2 THEN
        digito2 := 0;
    ELSE
        digito2 := 11 - resto;
    END IF;
    
    -- Verifica se os dígitos calculados conferem
    IF digito1 = SUBSTRING(cpf_limpo, 10, 1)::INTEGER AND 
       digito2 = SUBSTRING(cpf_limpo, 11, 1)::INTEGER THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para formatar CPF
CREATE OR REPLACE FUNCTION "SEC".formatar_cpf(cpf VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    cpf_limpo VARCHAR(11);
BEGIN
    cpf_limpo := REGEXP_REPLACE(cpf, '[^0-9]', '', 'g');
    IF LENGTH(cpf_limpo) = 11 THEN
        RETURN SUBSTRING(cpf_limpo, 1, 3) || '.' || 
               SUBSTRING(cpf_limpo, 4, 3) || '.' || 
               SUBSTRING(cpf_limpo, 7, 3) || '-' || 
               SUBSTRING(cpf_limpo, 10, 2);
    END IF;
    RETURN cpf;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para validar telefone brasileiro
CREATE OR REPLACE FUNCTION "SEC".validar_telefone_br(telefone VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    telefone_limpo VARCHAR;
    ddd VARCHAR(2);
    ddds_validos VARCHAR[] := ARRAY['11','12','13','14','15','16','17','18','19',
                                    '21','22','24','27','28',
                                    '31','32','33','34','35','37','38',
                                    '41','42','43','44','45','46',
                                    '47','48','49',
                                    '51','53','54','55',
                                    '61','62','63','64','65','66','67','68','69',
                                    '71','73','74','75','77','79',
                                    '81','82','83','84','85','86','87','88','89',
                                    '91','92','93','94','95','96','97','98','99'];
BEGIN
    -- Remove caracteres não numéricos
    telefone_limpo := REGEXP_REPLACE(telefone, '[^0-9]', '', 'g');
    
    -- Remove código do país se presente
    IF LEFT(telefone_limpo, 2) = '55' THEN
        telefone_limpo := SUBSTRING(telefone_limpo, 3);
    END IF;
    
    -- Verifica se tem 10 ou 11 dígitos (celular com 9)
    IF LENGTH(telefone_limpo) NOT IN (10, 11) THEN
        RETURN FALSE;
    END IF;
    
    -- Extrai DDD
    ddd := LEFT(telefone_limpo, 2);
    
    -- Valida DDD
    IF NOT (ddd = ANY(ddds_validos)) THEN
        RETURN FALSE;
    END IF;
    
    -- Valida celular (deve começar com 9 se tiver 11 dígitos)
    IF LENGTH(telefone_limpo) = 11 AND SUBSTRING(telefone_limpo, 3, 1) != '9' THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para validar telefone (brasileiro ou internacional)
CREATE OR REPLACE FUNCTION "SEC".validar_telefone(telefone VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    telefone_limpo VARCHAR;
BEGIN
    IF telefone IS NULL OR TRIM(telefone) = '' THEN
        RETURN TRUE; -- Campo pode ser nulo/vazio
    END IF;
    
    telefone_limpo := REGEXP_REPLACE(telefone, '[^0-9]', '', 'g');
    
    -- Se começa com 55 (Brasil), valida como brasileiro
    IF LEFT(telefone_limpo, 2) = '55' THEN
        RETURN "SEC".validar_telefone_br(telefone);
    END IF;
    
    -- Para números internacionais, apenas verifica comprimento mínimo
    IF LENGTH(telefone_limpo) >= 8 AND LENGTH(telefone_limpo) <= 15 THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para validar CNPJ
CREATE OR REPLACE FUNCTION "SEC".validar_cnpj(cnpj VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    cnpj_limpo VARCHAR(14);
    soma INTEGER;
    resto INTEGER;
    digito1 INTEGER;
    digito2 INTEGER;
    multiplicadores1 INTEGER[] := ARRAY[5,4,3,2,9,8,7,6,5,4,3,2];
    multiplicadores2 INTEGER[] := ARRAY[6,5,4,3,2,9,8,7,6,5,4,3,2];
    i INTEGER;
BEGIN
    -- Remove caracteres não numéricos
    cnpj_limpo := REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g');
    
    -- Verifica se tem 14 dígitos
    IF LENGTH(cnpj_limpo) != 14 THEN
        RETURN FALSE;
    END IF;
    
    -- Verifica se todos os dígitos são iguais
    IF cnpj_limpo IN ('00000000000000', '11111111111111', '22222222222222', '33333333333333',
                      '44444444444444', '55555555555555', '66666666666666', '77777777777777',
                      '88888888888888', '99999999999999') THEN
        RETURN FALSE;
    END IF;
    
    -- Calcula primeiro dígito verificador
    soma := 0;
    FOR i IN 1..12 LOOP
        soma := soma + (SUBSTRING(cnpj_limpo, i, 1)::INTEGER * multiplicadores1[i]);
    END LOOP;
    resto := soma % 11;
    IF resto < 2 THEN
        digito1 := 0;
    ELSE
        digito1 := 11 - resto;
    END IF;
    
    -- Calcula segundo dígito verificador
    soma := 0;
    FOR i IN 1..13 LOOP
        soma := soma + (SUBSTRING(cnpj_limpo, i, 1)::INTEGER * multiplicadores2[i]);
    END LOOP;
    resto := soma % 11;
    IF resto < 2 THEN
        digito2 := 0;
    ELSE
        digito2 := 11 - resto;
    END IF;
    
    -- Verifica se os dígitos calculados conferem
    IF digito1 = SUBSTRING(cnpj_limpo, 13, 1)::INTEGER AND 
       digito2 = SUBSTRING(cnpj_limpo, 14, 1)::INTEGER THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para formatar CNPJ
CREATE OR REPLACE FUNCTION "SEC".formatar_cnpj(cnpj VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    cnpj_limpo VARCHAR(14);
BEGIN
    cnpj_limpo := REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g');
    IF LENGTH(cnpj_limpo) = 14 THEN
        RETURN SUBSTRING(cnpj_limpo, 1, 2) || '.' || 
               SUBSTRING(cnpj_limpo, 3, 3) || '.' || 
               SUBSTRING(cnpj_limpo, 6, 3) || '/' || 
               SUBSTRING(cnpj_limpo, 9, 4) || '-' || 
               SUBSTRING(cnpj_limpo, 13, 2);
    END IF;
    RETURN cnpj;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para validar CEP
CREATE OR REPLACE FUNCTION "SEC".validar_cep(cep VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    cep_limpo VARCHAR(8);
BEGIN
    IF cep IS NULL OR TRIM(cep) = '' THEN
        RETURN TRUE; -- Campo pode ser nulo/vazio
    END IF;
    
    -- Remove caracteres não numéricos
    cep_limpo := REGEXP_REPLACE(cep, '[^0-9]', '', 'g');
    
    -- Verifica se tem 8 dígitos
    IF LENGTH(cep_limpo) != 8 THEN
        RETURN FALSE;
    END IF;
    
    -- Verifica se não são todos zeros
    IF cep_limpo = '00000000' THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para formatar CEP
CREATE OR REPLACE FUNCTION "SEC".formatar_cep(cep VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    cep_limpo VARCHAR(8);
BEGIN
    cep_limpo := REGEXP_REPLACE(cep, '[^0-9]', '', 'g');
    IF LENGTH(cep_limpo) = 8 THEN
        RETURN SUBSTRING(cep_limpo, 1, 2) || '.' || 
               SUBSTRING(cep_limpo, 3, 3) || '-' || 
               SUBSTRING(cep_limpo, 6, 3);
    END IF;
    RETURN cep;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Função para formatar telefone brasileiro
CREATE OR REPLACE FUNCTION SEC.formatar_telefone_br(telefone VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    telefone_limpo VARCHAR;
BEGIN
    telefone_limpo := REGEXP_REPLACE(telefone, '[^0-9]', '', 'g');
    
    -- Remove código 55 se presente
    IF LEFT(telefone_limpo, 2) = '55' THEN
        telefone_limpo := SUBSTRING(telefone_limpo, 3);
    END IF;
    
    -- Formato: +55 (XX) 9XXXX-XXXX ou +55 (XX) XXXX-XXXX
    IF LENGTH(telefone_limpo) = 11 THEN
        RETURN '+55 (' || SUBSTRING(telefone_limpo, 1, 2) || ') ' ||
               SUBSTRING(telefone_limpo, 3, 5) || '-' ||
               SUBSTRING(telefone_limpo, 8, 4);
    ELSIF LENGTH(telefone_limpo) = 10 THEN
        RETURN '+55 (' || SUBSTRING(telefone_limpo, 1, 2) || ') ' ||
               SUBSTRING(telefone_limpo, 3, 4) || '-' ||
               SUBSTRING(telefone_limpo, 7, 4);
    END IF;
    
    RETURN telefone;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================
-- TABELA: Empresa
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."Empresa" (
    IdEmpresa SERIAL PRIMARY KEY,
    RazaoSocial VARCHAR(200) NOT NULL,
    NomeFantasia VARCHAR(200) NOT NULL,
    CNPJ VARCHAR(18) UNIQUE,
    InscricaoEstadual VARCHAR(20),
    InscricaoMunicipal VARCHAR(20),
    Telefone VARCHAR(20),
    Email VARCHAR(100),
    Website VARCHAR(200),
    CEP VARCHAR(10),
    Logradouro VARCHAR(200),
    Numero VARCHAR(10),
    Complemento VARCHAR(100),
    Bairro VARCHAR(100),
    Cidade VARCHAR(100),
    Estado VARCHAR(2),
    Pais VARCHAR(50) DEFAULT 'BRASIL',
    Ativo BOOLEAN DEFAULT TRUE,
    Observacoes TEXT,
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CadastranteUpdate VARCHAR(200),
    DataUpdate TIMESTAMP,
    CadastranteDelete VARCHAR(200),
    DataDelete TIMESTAMP,
    DeletadoLogico BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CONSTRAINT chk_cnpj_valido CHECK (CNPJ IS NULL OR "SEC".validar_cnpj(CNPJ)),
    CONSTRAINT chk_cep_valido CHECK (CEP IS NULL OR "SEC".validar_cep(CEP))
);

-- Índices para Empresa
CREATE INDEX idx_empresa_cnpj ON "SEC"."Empresa"(CNPJ);
CREATE INDEX idx_empresa_nomefantasia ON "SEC"."Empresa"(NomeFantasia);
CREATE INDEX idx_empresa_ativo ON "SEC"."Empresa"(Ativo);

-- =====================================================
-- TABELA: Departamento
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."Departamento" (
    IdDepartamento SERIAL PRIMARY KEY,
    Sigla VARCHAR(10) NOT NULL UNIQUE,
    Departamento VARCHAR(100) NOT NULL,
    Descricao TEXT,
    IdEmpresa INTEGER REFERENCES "SEC"."Empresa"(IdEmpresa),
    Ativo BOOLEAN DEFAULT TRUE,
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CadastranteUpdate VARCHAR(200),
    DataUpdate TIMESTAMP,
    CadastranteDelete VARCHAR(200),
    DataDelete TIMESTAMP,
    DeletadoLogico BOOLEAN DEFAULT FALSE
);

-- Índices para Departamento
CREATE INDEX idx_departamento_sigla ON "SEC"."Departamento"(Sigla);
CREATE INDEX idx_departamento_empresa ON "SEC"."Departamento"(IdEmpresa);

-- TABELA: Perfil
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."Perfil" (
    IdPerfil SERIAL PRIMARY KEY,
    NomePerfil VARCHAR(100) NOT NULL UNIQUE,
    Descricao TEXT,
    NivelAcesso INTEGER DEFAULT 1 CHECK (NivelAcesso BETWEEN 1 AND 10),
    Ativo BOOLEAN DEFAULT TRUE,
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CadastranteUpdate VARCHAR(200),
    DataUpdate TIMESTAMP,
    CadastranteDelete VARCHAR(200),
    DataDelete TIMESTAMP,
    DeletadoLogico BOOLEAN DEFAULT FALSE
);

-- Índices para Perfil
CREATE INDEX idx_perfil_nome ON "SEC"."Perfil"(NomePerfil);

-- =====================================================
-- TABELA: Permissao
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."Permissao" (
    IdPermissao SERIAL PRIMARY KEY,
    NomePermissao VARCHAR(100) NOT NULL UNIQUE,
    Descricao TEXT,
    Modulo VARCHAR(50),
    TipoPermissao VARCHAR(20) CHECK (TipoPermissao IN ('CREATE', 'READ', 'UPDATE', 'DELETE', 'EXECUTE', 'ADMIN')),
    Ativo BOOLEAN DEFAULT TRUE,
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CadastranteUpdate VARCHAR(200),
    DataUpdate TIMESTAMP,
    CadastranteDelete VARCHAR(200),
    DataDelete TIMESTAMP,
    DeletadoLogico BOOLEAN DEFAULT FALSE
);

-- Índices para Permissao
CREATE INDEX idx_permissao_nome ON "SEC"."Permissao"(NomePermissao);
CREATE INDEX idx_permissao_modulo ON "SEC"."Permissao"(Modulo);

-- =====================================================
-- TABELA: Usuario
-- =====================================================
-- Garantir definição consistente: descartar tabela pré-existente simplificada
DROP TABLE IF EXISTS "SEC"."Usuario" CASCADE;
CREATE TABLE IF NOT EXISTS "SEC"."Usuario" (
    IdUsuario SERIAL PRIMARY KEY,
    Nome VARCHAR(200) NOT NULL,
    CPF VARCHAR(14) UNIQUE,
    Celular VARCHAR(25),
    Whatsapp VARCHAR(25),
    Email VARCHAR(100) UNIQUE NOT NULL,
    Instagram VARCHAR(100),
    Facebook VARCHAR(100),
    Linkedin VARCHAR(100),
    OutrosSociais TEXT,
    IdEmpresa INTEGER REFERENCES "SEC"."Empresa"(IdEmpresa),
    IdDepartamento INTEGER REFERENCES "SEC"."Departamento"(IdDepartamento),
    Usuario VARCHAR(100) UNIQUE NOT NULL,
    Senha VARCHAR(255) NOT NULL,
    TipoAutenticacao VARCHAR(20) DEFAULT 'LOCAL' CHECK (TipoAutenticacao IN ('LOCAL', 'GOOGLE', 'MICROSOFT', 'INSTAGRAM', 'FACEBOOK', 'OUTROS')),
    IdPerfilPrincipal INTEGER REFERENCES "SEC"."Perfil"(IdPerfil),
    Perfil VARCHAR(100),
    Permissao TEXT,
    Imagem VARCHAR(500),
    Ativo BOOLEAN DEFAULT TRUE,
    PrimeiroAcesso BOOLEAN DEFAULT TRUE,
    UltimoLogin TIMESTAMP,
    TentativasLogin INTEGER DEFAULT 0,
    Bloqueado BOOLEAN DEFAULT FALSE,
    DataBloqueio TIMESTAMP,
    MotivoBlockeio TEXT,
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CadastranteUpdate VARCHAR(200),
    DataUpdate TIMESTAMP,
    CadastranteDelete VARCHAR(200),
    DataDelete TIMESTAMP,
    DeletadoLogico BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CONSTRAINT chk_cpf_valido CHECK (CPF IS NULL OR "SEC".validar_cpf(CPF)),
    CONSTRAINT chk_celular_valido CHECK (Celular IS NULL OR "SEC".validar_telefone(Celular)),
    CONSTRAINT chk_whatsapp_valido CHECK (Whatsapp IS NULL OR "SEC".validar_telefone(Whatsapp))
);

-- Índices para Usuario
CREATE INDEX idx_usuario_cpf ON "SEC"."Usuario"(CPF);
CREATE INDEX idx_usuario_email ON "SEC"."Usuario"(Email);
CREATE INDEX idx_usuario_usuario ON "SEC"."Usuario"(Usuario);
CREATE INDEX idx_usuario_empresa ON "SEC"."Usuario"(IdEmpresa);
CREATE INDEX idx_usuario_departamento ON "SEC"."Usuario"(IdDepartamento);
CREATE INDEX idx_usuario_ativo ON "SEC"."Usuario"(Ativo);

-- =====================================================
-- TABELA: PerfilPermissao (Relacionamento N:N)
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."PerfilPermissao" (
    IdPerfilPermissao SERIAL PRIMARY KEY,
    IdPerfil INTEGER NOT NULL REFERENCES "SEC"."Perfil"(IdPerfil),
    IdPermissao INTEGER NOT NULL REFERENCES "SEC"."Permissao"(IdPermissao),
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(IdPerfil, IdPermissao)
);

CREATE INDEX idx_perfilpermissao_perfil ON "SEC"."PerfilPermissao"(IdPerfil);
CREATE INDEX idx_perfilpermissao_permissao ON "SEC"."PerfilPermissao"(IdPermissao);

-- =====================================================
-- TABELA: UsuarioPerfil (Relacionamento N:N - Usuário pode ter múltiplos perfis)
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."UsuarioPerfil" (
    IdUsuarioPerfil SERIAL PRIMARY KEY,
    IdUsuario INTEGER NOT NULL REFERENCES "SEC"."Usuario"(IdUsuario),
    IdPerfil INTEGER NOT NULL REFERENCES "SEC"."Perfil"(IdPerfil),
    Cadastrante VARCHAR(200) NOT NULL,
    DataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(IdUsuario, IdPerfil)
);

CREATE INDEX idx_usuarioperfil_usuario ON "SEC"."UsuarioPerfil"(IdUsuario);
CREATE INDEX idx_usuarioperfil_perfil ON "SEC"."UsuarioPerfil"(IdPerfil);

-- =====================================================
-- TABELA DE AUDITORIA COMPLETA
-- =====================================================
CREATE TABLE IF NOT EXISTS "SEC"."AuditoriaGeral" (
    IdAuditoria BIGSERIAL PRIMARY KEY,
    NomeTabela VARCHAR(100) NOT NULL,
    IdRegistro INTEGER NOT NULL,
    TipoOperacao VARCHAR(10) NOT NULL CHECK (TipoOperacao IN ('INSERT', 'UPDATE', 'DELETE')),
    Usuario VARCHAR(200) NOT NULL,
    DataOperacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DadosAntigos JSONB,
    DadosNovos JSONB,
    CamposAlterados TEXT[],
    EnderecoIP VARCHAR(45),
    UserAgent TEXT
);

CREATE INDEX idx_auditoria_tabela ON "SEC"."AuditoriaGeral"(NomeTabela);
CREATE INDEX idx_auditoria_registro ON "SEC"."AuditoriaGeral"(IdRegistro);
CREATE INDEX idx_auditoria_operacao ON "SEC"."AuditoriaGeral"(TipoOperacao);
CREATE INDEX idx_auditoria_data ON "SEC"."AuditoriaGeral"(DataOperacao);

-- =====================================================
-- TRIGGERS DE AUDITORIA E FORMATAÇÃO
-- =====================================================

-- Trigger para formatar CPF antes de inserir/atualizar
CREATE OR REPLACE FUNCTION "SEC".trg_formatar_cpf()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CPF IS NOT NULL THEN
        NEW.CPF := "SEC".formatar_cpf(NEW.CPF);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_formatar_cpf
BEFORE INSERT OR UPDATE ON "SEC"."Usuario"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_formatar_cpf();

-- Trigger para formatar CNPJ antes de inserir/atualizar
CREATE OR REPLACE FUNCTION "SEC".trg_formatar_cnpj()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CNPJ IS NOT NULL THEN
        NEW.CNPJ := "SEC".formatar_cnpj(NEW.CNPJ);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_empresa_formatar_cnpj
BEFORE INSERT OR UPDATE ON "SEC"."Empresa"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_formatar_cnpj();

-- Trigger para formatar CEP antes de inserir/atualizar
CREATE OR REPLACE FUNCTION "SEC".trg_formatar_cep()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CEP IS NOT NULL THEN
        NEW.CEP := "SEC".formatar_cep(NEW.CEP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_empresa_formatar_cep
BEFORE INSERT OR UPDATE ON "SEC"."Empresa"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_formatar_cep();

-- Trigger para converter campos para MAIÚSCULO (EMPRESA)
CREATE OR REPLACE FUNCTION "SEC".trg_empresa_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.RazaoSocial := UPPER(TRIM(NEW.RazaoSocial));
    NEW.NomeFantasia := UPPER(TRIM(NEW.NomeFantasia));
    IF NEW.InscricaoEstadual IS NOT NULL THEN
        NEW.InscricaoEstadual := UPPER(TRIM(NEW.InscricaoEstadual));
    END IF;
    IF NEW.InscricaoMunicipal IS NOT NULL THEN
        NEW.InscricaoMunicipal := UPPER(TRIM(NEW.InscricaoMunicipal));
    END IF;
    IF NEW.Website IS NOT NULL THEN
        NEW.Website := LOWER(TRIM(NEW.Website));
    END IF;
    IF NEW.Logradouro IS NOT NULL THEN
        NEW.Logradouro := UPPER(TRIM(NEW.Logradouro));
    END IF;
    IF NEW.Numero IS NOT NULL THEN
        NEW.Numero := UPPER(TRIM(NEW.Numero));
    END IF;
    IF NEW.Complemento IS NOT NULL THEN
        NEW.Complemento := UPPER(TRIM(NEW.Complemento));
    END IF;
    IF NEW.Bairro IS NOT NULL THEN
        NEW.Bairro := UPPER(TRIM(NEW.Bairro));
    END IF;
    IF NEW.Cidade IS NOT NULL THEN
        NEW.Cidade := UPPER(TRIM(NEW.Cidade));
    END IF;
    IF NEW.Estado IS NOT NULL THEN
        NEW.Estado := UPPER(TRIM(NEW.Estado));
    END IF;
    IF NEW.Pais IS NOT NULL THEN
        NEW.Pais := UPPER(TRIM(NEW.Pais));
    END IF;
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    IF NEW.CadastranteUpdate IS NOT NULL THEN
        NEW.CadastranteUpdate := UPPER(TRIM(NEW.CadastranteUpdate));
    END IF;
    IF NEW.CadastranteDelete IS NOT NULL THEN
        NEW.CadastranteDelete := UPPER(TRIM(NEW.CadastranteDelete));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_empresa_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."Empresa"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_empresa_maiusculo();

-- Trigger para formatar telefones antes de inserir/atualizar
CREATE OR REPLACE FUNCTION "SEC".trg_formatar_telefones()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.Celular IS NOT NULL AND LEFT(REGEXP_REPLACE(NEW.Celular, '[^0-9]', '', 'g'), 2) = '55' THEN
        NEW.Celular := "SEC".formatar_telefone_br(NEW.Celular);
    END IF;
    IF NEW.Whatsapp IS NOT NULL AND LEFT(REGEXP_REPLACE(NEW.Whatsapp, '[^0-9]', '', 'g'), 2) = '55' THEN
        NEW.Whatsapp := "SEC".formatar_telefone_br(NEW.Whatsapp);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_formatar_telefones
BEFORE INSERT OR UPDATE ON "SEC"."Usuario"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_formatar_telefones();

-- Trigger para converter campos para MAIÚSCULO/minúsculo (USUARIO)
CREATE OR REPLACE FUNCTION "SEC".trg_usuario_case()
RETURNS TRIGGER AS $$
BEGIN
    -- Campos em MAIÚSCULO
    NEW.Nome := UPPER(TRIM(NEW.Nome));
    
    -- Email em minúsculo
    NEW.Email := LOWER(TRIM(NEW.Email));
    NEW.Usuario := LOWER(TRIM(NEW.Usuario));
    
    -- Redes sociais mantêm case original (apenas trim)
    IF NEW.Instagram IS NOT NULL THEN
        NEW.Instagram := TRIM(NEW.Instagram);
    END IF;
    IF NEW.Facebook IS NOT NULL THEN
        NEW.Facebook := TRIM(NEW.Facebook);
    END IF;
    IF NEW.Linkedin IS NOT NULL THEN
        NEW.Linkedin := TRIM(NEW.Linkedin);
    END IF;
    IF NEW.OutrosSociais IS NOT NULL THEN
        NEW.OutrosSociais := TRIM(NEW.OutrosSociais);
    END IF;
    
    -- Senha mantém case original (não altera)
    -- NEW.Senha não é modificada
    
    -- Campos administrativos em MAIÚSCULO
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    IF NEW.CadastranteUpdate IS NOT NULL THEN
        NEW.CadastranteUpdate := UPPER(TRIM(NEW.CadastranteUpdate));
    END IF;
    IF NEW.CadastranteDelete IS NOT NULL THEN
        NEW.CadastranteDelete := UPPER(TRIM(NEW.CadastranteDelete));
    END IF;
    IF NEW.MotivoBlockeio IS NOT NULL THEN
        NEW.MotivoBlockeio := UPPER(TRIM(NEW.MotivoBlockeio));
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_case
BEFORE INSERT OR UPDATE ON "SEC"."Usuario"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_usuario_case();

-- Trigger para atualizar campos de auditoria no UPDATE
CREATE OR REPLACE FUNCTION "SEC".trg_atualizar_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    NEW.DataUpdate := CURRENT_TIMESTAMP;
    -- CadastranteUpdate deve ser setado pela aplicação
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para converter campos para MAIÚSCULO (DEPARTAMENTO)
CREATE OR REPLACE FUNCTION "SEC".trg_departamento_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.Sigla := UPPER(TRIM(NEW.Sigla));
    NEW.Departamento := UPPER(TRIM(NEW.Departamento));
    IF NEW.Descricao IS NOT NULL THEN
        NEW.Descricao := UPPER(TRIM(NEW.Descricao));
    END IF;
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    IF NEW.CadastranteUpdate IS NOT NULL THEN
        NEW.CadastranteUpdate := UPPER(TRIM(NEW.CadastranteUpdate));
    END IF;
    IF NEW.CadastranteDelete IS NOT NULL THEN
        NEW.CadastranteDelete := UPPER(TRIM(NEW.CadastranteDelete));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_departamento_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."Departamento"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_departamento_maiusculo();

-- Trigger para converter campos para MAIÚSCULO (PERFIL)
CREATE OR REPLACE FUNCTION "SEC".trg_perfil_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.NomePerfil := UPPER(TRIM(NEW.NomePerfil));
    IF NEW.Descricao IS NOT NULL THEN
        NEW.Descricao := UPPER(TRIM(NEW.Descricao));
    END IF;
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    IF NEW.CadastranteUpdate IS NOT NULL THEN
        NEW.CadastranteUpdate := UPPER(TRIM(NEW.CadastranteUpdate));
    END IF;
    IF NEW.CadastranteDelete IS NOT NULL THEN
        NEW.CadastranteDelete := UPPER(TRIM(NEW.CadastranteDelete));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_perfil_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."Perfil"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_perfil_maiusculo();

-- Trigger para converter campos para MAIÚSCULO (PERMISSAO)
CREATE OR REPLACE FUNCTION "SEC".trg_permissao_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.NomePermissao := UPPER(TRIM(NEW.NomePermissao));
    IF NEW.Descricao IS NOT NULL THEN
        NEW.Descricao := UPPER(TRIM(NEW.Descricao));
    END IF;
    IF NEW.Modulo IS NOT NULL THEN
        NEW.Modulo := UPPER(TRIM(NEW.Modulo));
    END IF;
    NEW.TipoPermissao := UPPER(TRIM(NEW.TipoPermissao));
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    IF NEW.CadastranteUpdate IS NOT NULL THEN
        NEW.CadastranteUpdate := UPPER(TRIM(NEW.CadastranteUpdate));
    END IF;
    IF NEW.CadastranteDelete IS NOT NULL THEN
        NEW.CadastranteDelete := UPPER(TRIM(NEW.CadastranteDelete));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_permissao_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."Permissao"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_permissao_maiusculo();

-- Trigger para converter campos para MAIÚSCULO (PERFILPERMISSAO)
CREATE OR REPLACE FUNCTION "SEC".trg_perfilpermissao_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_perfilpermissao_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."PerfilPermissao"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_perfilpermissao_maiusculo();

-- Trigger para converter campos para MAIÚSCULO (USUARIOPERFIL)
CREATE OR REPLACE FUNCTION "SEC".trg_usuarioperfil_maiusculo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.Cadastrante := UPPER(TRIM(NEW.Cadastrante));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuarioperfil_maiusculo
BEFORE INSERT OR UPDATE ON "SEC"."UsuarioPerfil"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_usuarioperfil_maiusculo();

-- Aplicar trigger de auditoria em todas as tabelas
CREATE TRIGGER trg_empresa_auditoria
BEFORE UPDATE ON "SEC"."Empresa"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_atualizar_auditoria();

CREATE TRIGGER trg_departamento_auditoria
BEFORE UPDATE ON "SEC"."Departamento"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_atualizar_auditoria();

CREATE TRIGGER trg_perfil_auditoria
BEFORE UPDATE ON "SEC"."Perfil"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_atualizar_auditoria();

CREATE TRIGGER trg_permissao_auditoria
BEFORE UPDATE ON "SEC"."Permissao"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_atualizar_auditoria();

CREATE TRIGGER trg_usuario_auditoria
BEFORE UPDATE ON "SEC"."Usuario"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_atualizar_auditoria();

-- Trigger para registrar todas as operações na tabela de auditoria
CREATE OR REPLACE FUNCTION "SEC".trg_registrar_auditoria()
RETURNS TRIGGER AS $$
DECLARE
    v_usuario VARCHAR(200);
    v_campos_alterados TEXT[];
    v_key TEXT;
    v_old_value TEXT;
    v_new_value TEXT;
    v_src JSONB;
    v_id_key TEXT;
    v_id_registro INTEGER;
BEGIN
    -- Determina o usuário que fez a operação
    IF TG_OP = 'INSERT' THEN
        v_usuario := NEW.Cadastrante;
    ELSIF TG_OP = 'UPDATE' THEN
        v_usuario := NEW.CadastranteUpdate;
    ELSE
        v_usuario := OLD.CadastranteDelete;
    END IF;

    -- Para UPDATE, identifica campos alterados
    IF TG_OP = 'UPDATE' THEN
        v_campos_alterados := ARRAY[]::TEXT[];
        FOR v_key IN SELECT jsonb_object_keys(to_jsonb(NEW))
        LOOP
            v_old_value := (to_jsonb(OLD) ->> v_key);
            v_new_value := (to_jsonb(NEW) ->> v_key);
            IF v_old_value IS DISTINCT FROM v_new_value THEN
                v_campos_alterados := array_append(v_campos_alterados, v_key);
            END IF;
        END LOOP;
    END IF;

    -- Determina a chave do registro: primeiro campo cujo nome começa com 'id'
    v_src := CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
    SELECT key INTO v_id_key
    FROM jsonb_object_keys(v_src) AS t(key)
    WHERE LOWER(key) LIKE 'id%'
    ORDER BY key
    LIMIT 1;
    IF v_id_key IS NULL THEN
        v_id_registro := NULL;
    ELSE
        v_id_registro := (v_src ->> v_id_key)::INTEGER;
    END IF;

    -- Insere registro de auditoria
    INSERT INTO "SEC"."AuditoriaGeral" (
        NomeTabela,
        IdRegistro,
        TipoOperacao,
        Usuario,
        DadosAntigos,
        DadosNovos,
        CamposAlterados
    ) VALUES (
        TG_TABLE_NAME,
        v_id_registro,
        TG_OP,
        v_usuario,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        v_campos_alterados
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de auditoria geral em todas as tabelas
CREATE TRIGGER trg_empresa_auditoria_geral
AFTER INSERT OR UPDATE OR DELETE ON "SEC"."Empresa"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_registrar_auditoria();

CREATE TRIGGER trg_departamento_auditoria_geral
AFTER INSERT OR UPDATE OR DELETE ON "SEC"."Departamento"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_registrar_auditoria();

CREATE TRIGGER trg_perfil_auditoria_geral
AFTER INSERT OR UPDATE OR DELETE ON "SEC"."Perfil"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_registrar_auditoria();

CREATE TRIGGER trg_permissao_auditoria_geral
AFTER INSERT OR UPDATE OR DELETE ON "SEC"."Permissao"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_registrar_auditoria();

CREATE TRIGGER trg_usuario_auditoria_geral
AFTER INSERT OR UPDATE OR DELETE ON "SEC"."Usuario"
FOR EACH ROW
EXECUTE FUNCTION "SEC".trg_registrar_auditoria();

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View completa de usuários com informações relacionadas
CREATE OR REPLACE VIEW "SEC".vw_usuarios_completo AS
SELECT 
    u.IdUsuario,
    u.Nome,
    u.CPF,
    u.Celular,
    u.Whatsapp,
    u.Email,
    u.Usuario,
    u.Instagram,
    u.Facebook,
    u.Linkedin,
    u.OutrosSociais,
    e.NomeFantasia AS Empresa,
    CONCAT(d.Sigla, ' - ', d.Departamento) AS Departamento,
    p.NomePerfil AS PerfilPrincipal,
    u.TipoAutenticacao,
    u.Imagem,
    u.Ativo,
    u.PrimeiroAcesso,
    u.UltimoLogin,
    u.Bloqueado,
    u.Cadastrante,
    u.DataCadastro,
    u.CadastranteUpdate,
    u.DataUpdate
FROM "SEC"."Usuario" u
LEFT JOIN "SEC"."Empresa" e ON u.IdEmpresa = e.IdEmpresa
LEFT JOIN "SEC"."Departamento" d ON u.IdDepartamento = d.IdDepartamento
LEFT JOIN "SEC"."Perfil" p ON u.IdPerfilPrincipal = p.IdPerfil
WHERE u.DeletadoLogico = FALSE;

-- View de departamentos com empresa
CREATE OR REPLACE VIEW "SEC".vw_departamentos_empresa AS
SELECT 
    d.IdDepartamento,
    d.Sigla,
    d.Departamento,
    CONCAT(d.Sigla, ' - ', d.Departamento) AS DepartamentoCompleto,
    d.Descricao,
    e.NomeFantasia AS Empresa,
    d.Ativo,
    d.Cadastrante,
    d.DataCadastro
FROM "SEC"."Departamento" d
LEFT JOIN "SEC"."Empresa" e ON d.IdEmpresa = e.IdEmpresa
WHERE d.DeletadoLogico = FALSE;

-- Compat: view SEC.Usuarios removida. Utilize diretamente a tabela SEC.Usuario.

-- =====================================================
-- DADOS INICIAIS (SEED)
-- =====================================================

-- Inserir Empresa padrão
INSERT INTO "SEC"."Empresa" (RazaoSocial, NomeFantasia, CNPJ, Telefone, Email, Ativo, Cadastrante)
VALUES ('SISTEMA ADMINISTRATIVO LTDA', 'Sistema Admin', '00.000.000/0001-91', '+55 (11) 99999-9999', 'contato@sistema.com.br', TRUE, 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Inserir Departamentos padrão
INSERT INTO "SEC"."Departamento" (Sigla, Departamento, Descricao, IdEmpresa, Cadastrante)
VALUES 
    ('TI', 'Tecnologia da Informação', 'Departamento de TI', 1, 'SYSTEM'),
    ('ADM', 'Administração', 'Departamento Administrativo', 1, 'SYSTEM'),
    ('FIN', 'Financeiro', 'Departamento Financeiro', 1, 'SYSTEM'),
    ('RH', 'Recursos Humanos', 'Departamento de RH', 1, 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Inserir Perfis padrão
INSERT INTO "SEC"."Perfil" (NomePerfil, Descricao, NivelAcesso, Cadastrante)
VALUES 
    ('ADMINISTRADOR', 'Acesso total ao sistema com permissões administrativas completas', 10, 'SYSTEM'),
    ('COLABORADOR', 'Acesso padrão para colaboradores da empresa', 5, 'SYSTEM'),
    ('ARTISTA', 'Acesso específico para artistas e criadores de conteúdo', 4, 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Inserir Permissões padrão
INSERT INTO "SEC"."Permissao" (NomePermissao, Descricao, Modulo, TipoPermissao, Cadastrante)
VALUES 
    ('ADMIN_TOTAL', 'Acesso administrativo total', 'Sistema', 'ADMIN', 'SYSTEM'),
    ('USUARIO_CREATE', 'Criar usuários', 'Usuarios', 'CREATE', 'SYSTEM'),
    ('USUARIO_READ', 'Visualizar usuários', 'Usuarios', 'READ', 'SYSTEM'),
    ('USUARIO_UPDATE', 'Editar usuários', 'Usuarios', 'UPDATE', 'SYSTEM'),
    ('USUARIO_DELETE', 'Excluir usuários', 'Usuarios', 'DELETE', 'SYSTEM'),
    ('EMPRESA_CREATE', 'Criar empresas', 'Empresas', 'CREATE', 'SYSTEM'),
    ('EMPRESA_READ', 'Visualizar empresas', 'Empresas', 'READ', 'SYSTEM'),
    ('EMPRESA_UPDATE', 'Editar empresas', 'Empresas', 'UPDATE', 'SYSTEM'),
    ('EMPRESA_DELETE', 'Excluir empresas', 'Empresas', 'DELETE', 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Associar permissões ao perfil Administrador
INSERT INTO "SEC"."PerfilPermissao" (IdPerfil, IdPermissao, Cadastrante)
SELECT 1, IdPermissao, 'SYSTEM'
FROM "SEC"."Permissao"
ON CONFLICT DO NOTHING;

-- Inserir usuário administrador padrão
-- Senha: changeme123 (bcrypt $2b$, rounds=12)
-- Inserir usuário administrador padrão parametrizado via .env
WITH admin_perfil AS (
    SELECT IdPerfil FROM "SEC"."Perfil" WHERE NomePerfil = 'ADMINISTRADOR' LIMIT 1
), empresa AS (
    SELECT IdEmpresa FROM "SEC"."Empresa" ORDER BY IdEmpresa LIMIT 1
), departamento AS (
    SELECT IdDepartamento FROM "SEC"."Departamento" ORDER BY IdDepartamento LIMIT 1
)
INSERT INTO "SEC"."Usuario" (
    Nome, 
    Email, 
    Usuario, 
    Senha,
    IdEmpresa,
    IdDepartamento,
    IdPerfilPrincipal,
    Perfil,
    Ativo,
    PrimeiroAcesso,
    Cadastrante
)
SELECT
    'ADMIN',
    'admin@sistema.com.br',
    'admin',
    crypt('123456', gen_salt('bf', 12)),
    (SELECT IdEmpresa FROM empresa),
    (SELECT IdDepartamento FROM departamento),
    (SELECT IdPerfil FROM admin_perfil),
    'ADMINISTRADOR',
    TRUE,
    TRUE,
    'SYSTEM'
ON CONFLICT DO NOTHING;

-- ======================== PERFIS E PERMISSÕES PÚBLICAS ========================
-- Criar perfil VISITANTE (acesso apenas a conteúdos públicos)
INSERT INTO "SEC"."Perfil" (NomePerfil, Descricao, NivelAcesso, Cadastrante)
VALUES ('VISITANTE', 'Acesso público sem autenticação', 1, 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Criar permissões públicas de leitura
INSERT INTO "SEC"."Permissao" (NomePermissao, Descricao, Modulo, TipoPermissao, Cadastrante)
VALUES 
  ('AGENDAS_READ_PUBLIC', 'Ler agendas culturais públicas', 'Agendas', 'READ', 'SYSTEM'),
  ('ARTISTAS_READ_PUBLIC', 'Ler banco de artistas público', 'Artistas', 'READ', 'SYSTEM'),
  ('PUBLIC_INFO_READ', 'Ler informações públicas gerais', 'Publico', 'READ', 'SYSTEM')
ON CONFLICT DO NOTHING;

-- Associar permissões públicas ao perfil VISITANTE
WITH visitante AS (
  SELECT IdPerfil FROM "SEC"."Perfil" WHERE NomePerfil = 'VISITANTE' LIMIT 1
), perms AS (
  SELECT IdPermissao FROM "SEC"."Permissao" WHERE NomePermissao IN ('AGENDAS_READ_PUBLIC','ARTISTAS_READ_PUBLIC','PUBLIC_INFO_READ')
)
INSERT INTO "SEC"."PerfilPermissao" (IdPerfil, IdPermissao, Cadastrante)
SELECT (SELECT IdPerfil FROM visitante), IdPermissao, 'SYSTEM'
FROM perms
ON CONFLICT DO NOTHING;

-- ======================== USUÁRIOS PADRÃO ========================
-- Usuário ARTISTA01 (perfil ARTISTA)
WITH artista_perfil AS (
  SELECT IdPerfil FROM "SEC"."Perfil" WHERE NomePerfil = 'ARTISTA' LIMIT 1
), empresa AS (
  SELECT IdEmpresa FROM "SEC"."Empresa" ORDER BY IdEmpresa LIMIT 1
), departamento AS (
  SELECT IdDepartamento FROM "SEC"."Departamento" ORDER BY IdDepartamento LIMIT 1
)
INSERT INTO "SEC"."Usuario" (
  Nome, Email, Usuario, Senha,
  IdEmpresa, IdDepartamento,
  IdPerfilPrincipal, Perfil,
  Ativo, PrimeiroAcesso, Cadastrante
)
SELECT 
  'ARTISTA 01', 'artista01@example.com', 'ARTISTA01', crypt('changeme123', gen_salt('bf', 12)),
  (SELECT IdEmpresa FROM empresa), (SELECT IdDepartamento FROM departamento),
  (SELECT IdPerfil FROM artista_perfil), 'ARTISTA',
  TRUE, TRUE, 'SYSTEM'
ON CONFLICT DO NOTHING;

-- Usuário SERVIDOR01 (perfil COLABORADOR)
WITH colaborador_perfil AS (
  SELECT IdPerfil FROM "SEC"."Perfil" WHERE NomePerfil = 'COLABORADOR' LIMIT 1
), empresa AS (
  SELECT IdEmpresa FROM "SEC"."Empresa" ORDER BY IdEmpresa LIMIT 1
), departamento AS (
  SELECT IdDepartamento FROM "SEC"."Departamento" ORDER BY IdDepartamento LIMIT 1
)
INSERT INTO "SEC"."Usuario" (
  Nome, Email, Usuario, Senha,
  IdEmpresa, IdDepartamento,
  IdPerfilPrincipal, Perfil,
  Ativo, PrimeiroAcesso, Cadastrante
)
SELECT 
  'SERVIDOR 01', 'servidor01@example.com', 'SERVIDOR01', crypt('changeme123', gen_salt('bf', 12)),
  (SELECT IdEmpresa FROM empresa), (SELECT IdDepartamento FROM departamento),
  (SELECT IdPerfil FROM colaborador_perfil), 'COLABORADOR',
  TRUE, TRUE, 'SYSTEM'
ON CONFLICT DO NOTHING;

-- Associar perfil ao usuário administrador usando seleção por username
INSERT INTO "SEC"."UsuarioPerfil" (IdUsuario, IdPerfil, Cadastrante)
SELECT u.IdUsuario, p.IdPerfil, 'SYSTEM'
FROM "SEC"."Usuario" u
JOIN "SEC"."Perfil" p ON p.NomePerfil = 'ADMINISTRADOR'
WHERE u.Usuario = 'admin'
ON CONFLICT DO NOTHING;

-- Associar perfil principal para todos os usuários com IdPerfilPrincipal definido
INSERT INTO "SEC"."UsuarioPerfil" (IdUsuario, IdPerfil, Cadastrante)
SELECT u.IdUsuario, u.IdPerfilPrincipal, 'SYSTEM'
FROM "SEC"."Usuario" u
WHERE u.IdPerfilPrincipal IS NOT NULL
ON CONFLICT DO NOTHING;

-- =====================================================
-- PROCEDURES ÚTEIS
-- =====================================================

-- Procedure para realizar soft delete
CREATE OR REPLACE PROCEDURE "SEC".soft_delete(
    p_tabela VARCHAR,
    p_id INTEGER,
    p_usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := FORMAT(
        'UPDATE "SEC".%I SET DeletadoLogico = TRUE, CadastranteDelete = %L, DataDelete = CURRENT_TIMESTAMP WHERE %I = %s',
        p_tabela,
        p_usuario,
        LOWER('id' || p_tabela),
        p_id
    );
    EXECUTE v_sql;
    
    RAISE NOTICE 'Registro % da tabela % marcado como deletado por %', p_id, p_tabela, p_usuario;
END;
$$;

-- Procedure para restaurar registro deletado logicamente
CREATE OR REPLACE PROCEDURE "SEC".restaurar_registro(
    p_tabela VARCHAR,
    p_id INTEGER,
    p_usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_sql TEXT;
BEGIN
    v_sql := FORMAT(
        'UPDATE "SEC".%I SET DeletadoLogico = FALSE, CadastranteUpdate = %L, DataUpdate = CURRENT_TIMESTAMP WHERE %I = %s',
        p_tabela,
        p_usuario,
        LOWER('id' || p_tabela),
        p_id
    );
    EXECUTE v_sql;
    
    RAISE NOTICE 'Registro % da tabela % restaurado por %', p_id, p_tabela, p_usuario;
END;
$$;

-- Procedure para listar histórico de alterações de um registro
CREATE OR REPLACE FUNCTION "SEC".obter_historico_registro(
    p_tabela VARCHAR,
    p_id INTEGER
)
RETURNS TABLE (
    IdAuditoria BIGINT,
    TipoOperacao VARCHAR,
    Usuario VARCHAR,
    DataOperacao TIMESTAMP,
    CamposAlterados TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.IdAuditoria,
        a.TipoOperacao,
        a.Usuario,
        a.DataOperacao,
        a.CamposAlterados
    FROM "SEC"."AuditoriaGeral" a
    WHERE a.NomeTabela = p_tabela
    AND a.IdRegistro = p_id
    ORDER BY a.DataOperacao DESC;
END;
$$;

-- Função para obter permissões de um usuário
CREATE OR REPLACE FUNCTION "SEC".obter_permissoes_usuario(p_idusuario INTEGER)
RETURNS TABLE (
    NomePermissao VARCHAR,
    Descricao TEXT,
    Modulo VARCHAR,
    TipoPermissao VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        pm.NomePermissao,
        pm.Descricao,
        pm.Modulo,
        pm.TipoPermissao
    FROM "SEC"."Usuario" u
    INNER JOIN "SEC"."UsuarioPerfil" up ON u.IdUsuario = up.IdUsuario
    INNER JOIN "SEC"."Perfil" pf ON up.IdPerfil = pf.IdPerfil
    INNER JOIN "SEC"."PerfilPermissao" pp ON pf.IdPerfil = pp.IdPerfil
    INNER JOIN "SEC"."Permissao" pm ON pp.IdPermissao = pm.IdPermissao
    WHERE u.IdUsuario = p_idusuario
    AND u.Ativo = TRUE
    AND u.DeletadoLogico = FALSE
    AND pf.Ativo = TRUE
    AND pm.Ativo = TRUE
    ORDER BY pm.Modulo, pm.TipoPermissao;
END;
$$;

-- Função para verificar se usuário tem permissão específica
CREATE OR REPLACE FUNCTION "SEC".usuario_tem_permissao(
    p_idusuario INTEGER,
    p_nomepermissao VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_tem_permissao BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM "SEC"."Usuario" u
        INNER JOIN "SEC"."UsuarioPerfil" up ON u.IdUsuario = up.IdUsuario
        INNER JOIN "SEC"."Perfil" pf ON up.IdPerfil = pf.IdPerfil
        INNER JOIN "SEC"."PerfilPermissao" pp ON pf.IdPerfil = pp.IdPerfil
        INNER JOIN "SEC"."Permissao" pm ON pp.IdPermissao = pm.IdPermissao
        WHERE u.IdUsuario = p_idusuario
        AND pm.NomePermissao = p_nomepermissao
        AND u.Ativo = TRUE
        AND u.DeletadoLogico = FALSE
        AND pf.Ativo = TRUE
        AND pm.Ativo = TRUE
    ) INTO v_tem_permissao;
    
    RETURN v_tem_permissao;
END;
$$;

-- Procedure para registrar login de usuário
CREATE OR REPLACE PROCEDURE "SEC".registrar_login(
    p_usuario VARCHAR,
    p_sucesso BOOLEAN DEFAULT TRUE
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_sucesso THEN
        UPDATE "SEC"."Usuario"
        SET 
            UltimoLogin = CURRENT_TIMESTAMP,
            TentativasLogin = 0,
            PrimeiroAcesso = FALSE
        WHERE Usuario = p_usuario OR Email = p_usuario;
    ELSE
        UPDATE "SEC"."Usuario"
        SET TentativasLogin = TentativasLogin + 1
        WHERE Usuario = p_usuario OR Email = p_usuario;
        
        -- Bloquear usuário após 5 tentativas falhas
        UPDATE SEC.Usuario
        SET 
            Bloqueado = TRUE,
            DataBloqueio = CURRENT_TIMESTAMP,
            MotivoBlockeio = 'Bloqueado automaticamente por múltiplas tentativas de login'
        WHERE (Usuario = p_usuario OR Email = p_usuario)
        AND TentativasLogin >= 5
        AND Bloqueado = FALSE;
    END IF;
END;
$$;

-- Procedure para desbloquear usuário
CREATE OR REPLACE PROCEDURE "SEC".desbloquear_usuario(
    p_idusuario INTEGER,
    p_usuario_admin VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE "SEC"."Usuario"
    SET 
        Bloqueado = FALSE,
        DataBloqueio = NULL,
        MotivoBlockeio = NULL,
        TentativasLogin = 0,
        CadastranteUpdate = p_usuario_admin,
        DataUpdate = CURRENT_TIMESTAMP
    WHERE IdUsuario = p_idusuario;
    
    RAISE NOTICE 'Usuário % desbloqueado por %', p_idusuario, p_usuario_admin;
END;
$$;

-- =====================================================
-- COMENTÁRIOS NAS TABELAS E COLUNAS
-- =====================================================

COMMENT ON SCHEMA "SEC" IS 'Schema para Sistema de Segurança e Controle Administrativo';

COMMENT ON TABLE "SEC"."Empresa" IS 'Cadastro de empresas do sistema';
COMMENT ON TABLE "SEC"."Departamento" IS 'Cadastro de departamentos das empresas';
COMMENT ON TABLE "SEC"."Perfil" IS 'Perfis de acesso do sistema';
COMMENT ON TABLE "SEC"."Permissao" IS 'Permissões disponíveis no sistema';
COMMENT ON TABLE "SEC"."Usuario" IS 'Cadastro de usuários do sistema';
COMMENT ON TABLE "SEC"."PerfilPermissao" IS 'Relacionamento entre perfis e permissões';
COMMENT ON TABLE "SEC"."UsuarioPerfil" IS 'Relacionamento entre usuários e perfis';
COMMENT ON TABLE "SEC"."AuditoriaGeral" IS 'Registro de auditoria de todas as operações';

COMMENT ON COLUMN "SEC"."Empresa".CNPJ IS 'CNPJ com validação e máscara XX.XXX.XXX/XXXX-XX';
COMMENT ON COLUMN "SEC"."Empresa".CEP IS 'CEP com validação e máscara XX.XXX-XXX';
COMMENT ON COLUMN "SEC"."Usuario".CPF IS 'CPF com validação e máscara XXX.XXX.XXX-XX';
COMMENT ON COLUMN "SEC"."Usuario".Celular IS 'Celular com máscara +55 (XX) 9XXXX-XXXX ou internacional';
COMMENT ON COLUMN "SEC"."Usuario".Whatsapp IS 'WhatsApp com máscara +55 (XX) 9XXXX-XXXX ou internacional';
COMMENT ON COLUMN "SEC"."Usuario".Senha IS 'Senha criptografada (bcrypt hash)';
COMMENT ON COLUMN "SEC"."Usuario".TipoAutenticacao IS 'Tipo de autenticação: LOCAL, GOOGLE, MICROSOFT, INSTAGRAM, FACEBOOK, OUTROS';
COMMENT ON COLUMN "SEC"."Usuario".Imagem IS 'Caminho da imagem no localStorage (*.png, *.jpeg, *.jpg)';
COMMENT ON COLUMN "SEC"."Usuario".DeletadoLogico IS 'Flag para exclusão lógica do registro';

-- =====================================================
-- GRANTS E PERMISSÕES
-- =====================================================

-- Criar role para aplicação (ajuste conforme necessário)
-- CREATE ROLE app_sec LOGIN PASSWORD 'sua_senha_segura';

-- Conceder permissões no schema
-- GRANT USAGE ON SCHEMA SEC TO app_sec;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA SEC TO app_sec;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA SEC TO app_sec;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA SEC TO app_sec;
-- GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA SEC TO app_sec;

-- =====================================================
-- CONSULTAS ÚTEIS PARA TESTES
-- =====================================================

-- Listar todos os usuários ativos
-- SELECT * FROM SEC.vw_usuarios_completo WHERE Ativo = TRUE;

-- Listar permissões de um usuário específico
-- SELECT * FROM SEC.obter_permissoes_usuario(1);

-- Verificar se usuário tem permissão específica
-- SELECT SEC.usuario_tem_permissao(1, 'ADMIN_TOTAL');

-- Obter histórico de alterações de um registro
-- SELECT * FROM SEC.obter_historico_registro('Usuario', 1);

-- Realizar soft delete de um registro
-- CALL SEC.soft_delete('Usuario', 2, 'admin');

-- Restaurar registro deletado
-- CALL SEC.restaurar_registro('Usuario', 2, 'admin');

-- Registrar login bem-sucedido
-- CALL SEC.registrar_login('admin', TRUE);

-- Desbloquear usuário
-- CALL SEC.desbloquear_usuario(1, 'admin');

-- =====================================================
-- SCRIPTS DE MANUTENÇÃO
-- =====================================================

-- View para monitorar logins bloqueados
CREATE OR REPLACE VIEW "SEC".vw_usuarios_bloqueados AS
SELECT 
    IdUsuario,
    Nome,
    Email,
    Usuario,
    TentativasLogin,
    DataBloqueio,
    MotivoBlockeio
FROM "SEC"."Usuario"
WHERE Bloqueado = TRUE
AND DeletadoLogico = FALSE;

-- View para monitorar auditoria recente
CREATE OR REPLACE VIEW "SEC".vw_auditoria_recente AS
SELECT 
    a.IdAuditoria,
    a.NomeTabela,
    a.IdRegistro,
    a.TipoOperacao,
    a.Usuario,
    a.DataOperacao,
    a.CamposAlterados
FROM "SEC"."AuditoriaGeral" a
WHERE a.DataOperacao >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY a.DataOperacao DESC;

-- =====================================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE
-- =====================================================

CREATE INDEX idx_auditoria_usuario ON "SEC"."AuditoriaGeral"(Usuario);
CREATE INDEX idx_usuario_bloqueado ON "SEC"."Usuario"(Bloqueado) WHERE Bloqueado = TRUE;
CREATE INDEX idx_usuario_deletado ON "SEC"."Usuario"(DeletadoLogico) WHERE DeletadoLogico = FALSE;

-- =====================================================
-- FINALIZAÇÃO
-- =====================================================

-- Exibir resumo das tabelas criadas
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM information_schema.tables 
    WHERE table_schema = 'SEC' AND table_type = 'BASE TABLE';
    
    RAISE NOTICE '================================================';
    RAISE NOTICE 'SCRIPT EXECUTADO COM SUCESSO!';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Total de tabelas criadas: %', v_count;
    RAISE NOTICE 'Schema: SEC';
    RAISE NOTICE 'Database: SEC';
    RAISE NOTICE '';
    RAISE NOTICE 'Usuário padrão criado:';
    RAISE NOTICE '  Usuário: admin';
    RAISE NOTICE '  Senha: 123456';
    RAISE NOTICE '  Email: admin@sistema.com.br';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANTE: Altere a senha padrão após o primeiro login!';
    RAISE NOTICE '================================================';
END $$;

-- Listar todas as tabelas criadas
SELECT 
    table_name AS "Tabela",
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema = 'SEC' AND table_name = t.table_name) AS "Colunas"
FROM information_schema.tables t
WHERE table_schema = 'SEC' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;









