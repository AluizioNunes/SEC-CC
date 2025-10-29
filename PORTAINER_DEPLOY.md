# Deploy no Portainer - Stack SEC

## Problemas Resolvidos

### RabbitMQ "unhealthy" no Portainer
- **Causa**: Dependência de arquivos externos e healthcheck inadequado
- **Solução**: Configuração simplificada sem dependências de arquivos locais

## Configurações Aplicadas

### 1. RabbitMQ Simplificado
- Removidas dependências de arquivos externos (`rabbitmq.conf`, `definitions.template.json`)
- Healthcheck robusto com timeout e retry adequados
- Variáveis de ambiente com fallbacks seguros

### 2. Healthcheck Melhorado
```yaml
healthcheck:
  test: ["CMD-SHELL", "timeout 10s bash -c 'until rabbitmq-diagnostics check_running; do sleep 1; done' && rabbitmq-diagnostics check_port_connectivity"]
  interval: 30s
  timeout: 15s
  retries: 3
  start_period: 120s
```

### 3. Variáveis de Ambiente Necessárias
```env
# RabbitMQ
RABBITMQ_ADMIN_USER=admin
RABBITMQ_ADMIN_PASSWORD=admin123
RABBITMQ_VHOST=/
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

# PostgreSQL
POSTGRES_USER=sec_user
POSTGRES_PASSWORD=sec_password
POSTGRES_DB=sec_db

# MongoDB
MONGODB_USER=sec_mongo
MONGODB_PASSWORD=sec_mongo_pass
MONGO_INITDB_DATABASE=sec_mongo_db

# FastAPI
FASTAPI_SECRET_KEY=your-secret-key-here
FASTAPI_ALGORITHM=HS256
FASTAPI_ACCESS_TOKEN_EXPIRE_MINUTES=30

# NestJS
NESTJS_PORT=3000
DATABASE_URL=postgresql://sec_user:sec_password@postgres:5432/sec_db
```

## Instruções para Deploy no Portainer

### 1. Preparação
1. Acesse o Portainer
2. Vá em "Stacks" → "Add stack"
3. Nomeie como "sec"

### 2. Configuração do Stack
1. **Método 1 - Upload do arquivo**:
   - Faça upload do `docker-compose.yml`
   - Faça upload do `.env` na seção "Environment variables"

2. **Método 2 - Web editor**:
   - Cole o conteúdo do `docker-compose.yml`
   - Cole as variáveis do `.env` na seção "Environment variables"

### 3. Verificação Pós-Deploy
- Todos os containers devem ficar "healthy" em até 3 minutos
- RabbitMQ Management UI: `http://host:15672` (admin/admin123)
- Frontend: `http://host:3001`
- NestJS API: `http://host:3000`
- FastAPI: `http://host:8000`

### 4. Troubleshooting

#### RabbitMQ ainda "unhealthy"
1. Verifique se as variáveis de ambiente estão definidas
2. Aguarde até 2 minutos para o healthcheck completar
3. Verifique logs do container para erros específicos

#### Erro "dependency failed to start"
1. Verifique se todas as variáveis obrigatórias estão definidas
2. Confirme que não há conflitos de porta no host
3. Reinicie o stack completo se necessário

## Credenciais Padrão

- **RabbitMQ**: admin / admin123
- **PostgreSQL**: sec_user / sec_password
- **MongoDB**: sec_mongo / sec_mongo_pass
- **Sistema**: admin / 123456 (após executar script de inicialização)

## Portas Expostas

- 3001: Frontend (React)
- 3000: NestJS API
- 8000: FastAPI
- 5432: PostgreSQL
- 27018: MongoDB
- 5672: RabbitMQ AMQP
- 15672: RabbitMQ Management
- 9090: Prometheus
- 3100: Loki
- 3200: Tempo