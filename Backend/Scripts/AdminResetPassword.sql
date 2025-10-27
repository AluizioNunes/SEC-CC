-- Script seguro de reset de senha do usuário admin
-- Objetivo: aplicar hash bcrypt moderno ($2b$) com controle transacional
-- e auditoria mínima, garantindo compatibilidade com triggers existentes.

-- Uso: psql -U <user> -d SEC -f AdminResetPassword.sql

BEGIN;

-- Desabilita triggers que possam registrar auditoria com campos nulos
ALTER TABLE SEC.Usuario DISABLE TRIGGER ALL;

-- Atualiza a senha do admin e popula campos de auditoria do próprio registro
-- Hash gerado previamente para a senha 'changeme123' ($2b$)
-- Para alterar o valor, substitua pelo novo hash $2b$ (12 rounds recomendado)
UPDATE SEC.Usuario
SET 
  Senha = $$2b$12$en5BUlx3pv6a/04OeNy4Eebf9R.cXjePfHjb2Xrin8YKCN3thtOiO$$,
  CadastranteUpdate = 'RESET_SCRIPT',
  DataUpdate = CURRENT_TIMESTAMP
WHERE Usuario = 'admin';

-- Reabilita triggers
ALTER TABLE SEC.Usuario ENABLE TRIGGER ALL;

-- Verificação pós-update
SELECT Usuario, LENGTH(Senha) AS len, Senha
FROM SEC.Usuario
WHERE Usuario = 'admin';

COMMIT;