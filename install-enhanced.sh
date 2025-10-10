#!/bin/bash

# 🚀 SEC - Sistema de Cadastro Cultural - Enhanced Installation Script
# Script completo para instalar dependências e executar com todas as melhorias implementadas

echo "🚀 Iniciando instalação aprimorada do SEC - Sistema de Cadastro Cultural"
echo "======================================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Docker e Docker Compose verificados"

# Instalar dependências Python
echo "📦 Instalando dependências Python avançadas..."
cd Backend/FastAPI
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências Python instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências Python"
    exit 1
fi

cd ../..

# Instalar dependências Node.js (NestJS)
echo "📦 Instalando dependências Node.js avançadas..."
cd Backend/NestJS
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependências Node.js instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências Node.js"
    exit 1
fi

cd ../..

# Instalar dependências do frontend
echo "📦 Instalando dependências do frontend..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependências do frontend instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências do frontend"
    exit 1
fi

# Criar diretórios necessários para logs e dados
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p Docker/prometheus
mkdir -p Docker/grafana/dashboards
mkdir -p Docker/grafana/provisioning

echo "✅ Diretórios criados"

# Configurar variáveis de ambiente
if [ ! -f .env ]; then
    echo "📋 Criando arquivo .env com configurações avançadas..."
    cat > .env << 'EOF'
# Database credentials
POSTGRES_USER=sec
POSTGRES_PASSWORD=secpass
POSTGRES_DB=secdb
MONGO_INITDB_DATABASE=secmongo

# Connection URLs
POSTGRES_URL=postgresql+psycopg://sec:secpass@postgres:5432/secdb
MONGODB_URL=mongodb://mongodb:27017/secmongo
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Service-specific
FASTAPI_LOG_LEVEL=info
NESTJS_PORT=3000

# Enhanced Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
REDIS_PASSWORD=redispassword

# Monitoring & Observability
PROMETHEUS_CONFIG_FILE=/etc/prometheus/prometheus.yml
GRAFANA_ADMIN_PASSWORD=admin
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6832

# Frontend
FRONTEND_URL=http://localhost:3000

# Blockchain (configure these for blockchain features)
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
APTOS_RPC_URL=https://fullnode.mainnet.aptoslabs.com/v1

# AI Services (configure these for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Logging
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true
EOF
    echo "✅ Arquivo .env criado com configurações avançadas!"
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "🎉 TODAS AS MELHORIAS FORAM IMPLEMENTADAS!"
echo "=========================================="
echo ""
echo "✅ Segurança Implementada:"
echo "   • Autenticação JWT em todas as APIs"
echo "   • CORS configurado adequadamente"
echo "   • Auditoria de segurança com logs estruturados"
echo ""
echo "✅ Performance Otimizada:"
echo "   • Consultas N+1 eliminadas no PostgreSQL"
echo "   • Cache Redis implementado nas APIs críticas"
echo "   • Connection pooling configurado para bancos"
echo ""
echo "✅ Monitoring & Observability:"
echo "   • Alertas configurados no Prometheus"
echo "   • Tracing distribuído implementado (Jaeger)"
echo "   • Métricas de negócio personalizadas"
echo "   • Dashboards específicos para cada serviço"
echo "   • Log aggregation avançado com Kibana"
echo ""
echo "🚀 Para executar a aplicação:"
echo "   docker-compose up --build"
echo ""
echo "📊 Endpoints disponíveis:"
echo "   • Frontend: http://localhost:3000"
echo "   • FastAPI: http://localhost:8000"
echo "   • NestJS: http://localhost:3000"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo "   • Jaeger: http://localhost:16686"
echo "   • Kibana: http://localhost:5601"
echo ""
echo "🔐 Para testar autenticação:"
echo "   POST http://localhost:8000/auth/login"
echo "   Body: {\"username\": \"admin\", \"password\": \"admin123\"}"
echo ""
echo "📈 Para ver métricas:"
echo "   • http://localhost:8000/metrics"
echo "   • http://localhost:3000/metrics"
echo ""
echo "🏥 Para health checks:"
echo "   • http://localhost:8000/health"
echo "   • http://localhost:8000/health/live"
echo "   • http://localhost:8000/health/ready"
echo ""
echo "⚠️  Configure as credenciais no arquivo .env antes de executar em produção!"
echo ""
echo "Para parar: docker-compose down"
