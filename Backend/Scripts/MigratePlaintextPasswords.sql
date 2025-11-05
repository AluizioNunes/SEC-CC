-- MigratePlaintextPasswords.sql
-- Migra senhas em texto para bcrypt ($2b$) na tabela "SEC"."Usuario".
-- Requer extensão pgcrypto: crypt(), gen_salt('bf', 12)

BEGIN;

-- Garantir extensão (executar como superuser)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Atualiza apenas senhas não iniciadas por "$2" (não-bcrypt)
UPDATE "SEC"."Usuario"
SET 
  senha = crypt(senha, gen_salt('bf', 12)),
  cadastranteupdate = COALESCE(:'CADASTRANTE_SYSTEM', 'PASSWORD-MIGRATION'),
  dataupdate = CURRENT_TIMESTAMP
WHERE senha IS NOT NULL
  AND senha NOT LIKE '$2%';

COMMIT;

-- Após execução, verifique:
-- SELECT COUNT(*) FROM "SEC"."Usuario" WHERE senha NOT LIKE '$2%';