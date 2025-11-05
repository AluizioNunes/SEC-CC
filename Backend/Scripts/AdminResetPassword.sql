-- Script seguro de reset de senha do usuário admin
-- Objetivo: aplicar hash bcrypt moderno ($2b$) com controle transacional
-- e auditoria mínima, garantindo compatibilidade com triggers existentes.

-- Uso:
-- docker compose exec -T postgres \
--   psql -U $POSTGRES_USER -d $POSTGRES_DB \
--   -v ADMIN_USERNAME="$ADMIN_USERNAME" \
--   -v ADMIN_RESET_PASSWORD="$ADMIN_RESET_PASSWORD" \
--   -v CADASTRANTE_SYSTEM="$CADASTRANTE_SYSTEM" \
--   -f /docker-entrypoint-initdb.d/AdminResetPassword.sql

BEGIN;

-- Desabilita triggers que possam registrar auditoria com campos nulos
ALTER TABLE "SEC"."Usuario" DISABLE TRIGGER ALL;

-- Atualiza a senha do admin e popula campos de auditoria do próprio registro
-- Hash gerado previamente para a senha 'changeme123' ($2b$)
-- Para alterar o valor, substitua pelo novo hash $2b$ (12 rounds recomendado)
UPDATE "SEC"."Usuario"
SET 
  Senha = crypt(:'ADMIN_RESET_PASSWORD', gen_salt('bf', 12)),
  CadastranteUpdate = :'CADASTRANTE_SYSTEM',
  DataUpdate = CURRENT_TIMESTAMP
WHERE Usuario = :'ADMIN_USERNAME';

-- Reabilita triggers
ALTER TABLE "SEC"."Usuario" ENABLE TRIGGER ALL;

-- Verificação pós-update
SELECT Usuario, LENGTH(Senha) AS len, Senha
FROM "SEC"."Usuario"
WHERE Usuario = 'admin';

COMMIT;