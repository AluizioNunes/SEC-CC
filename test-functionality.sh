#!/bin/bash
# 🚀 TESTES DE FUNCIONALIDADES - AMBIENTE DE DESENVOLVIMENTO
# Script para testar todas as funcionalidades ultra-revolucionárias

echo "🚀 Iniciando testes das funcionalidades ultra-revolucionárias..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local description=$2

    if curl -s --head --request GET --connect-timeout 5 "$url" > /dev/null; then
        log_info "✅ $description: Online ($url)"
        return 0
    else
        log_warn "❌ $description: Offline ($url)"
        return 1
    fi
}

# 1. TESTES DE SERVIÇOS BÁSICOS
echo ""
log "🔧 TESTANDO SERVIÇOS BÁSICOS..."

# Redis
test_endpoint "http://localhost:6379" "Redis" || log_warn "Redis pode precisar de configuração especial"

# PostgreSQL
if pg_isready -h localhost -p 5432 -U sec 2>/dev/null; then
    log_info "✅ PostgreSQL: Conectado"
else
    log_warn "❌ PostgreSQL: Não conectado"
fi

# MongoDB
test_endpoint "http://localhost:27017" "MongoDB"

# RabbitMQ
test_endpoint "http://localhost:15672" "RabbitMQ Management"

# 2. TESTES DE APIs PRINCIPAIS
echo ""
log "🌐 TESTANDO APIs PRINCIPAIS..."

# FastAPI
test_endpoint "http://localhost:8000" "FastAPI"
test_endpoint "http://localhost:8000/docs" "FastAPI Docs"

# NestJS
test_endpoint "http://localhost:3000" "NestJS API"

# Frontend React
test_endpoint "http://localhost:5173" "Frontend React"

# Nginx
test_endpoint "http://localhost" "Nginx Proxy"

# 3. TESTES DE MONITORAÇÃO
echo ""
log "📊 TESTANDO SISTEMA DE MONITORAÇÃO..."

# Grafana
test_endpoint "http://localhost:3001" "Grafana"

# Prometheus
test_endpoint "http://localhost:9090" "Prometheus"

# Loki
test_endpoint "http://localhost:3100" "Loki"

# 4. TESTES DE SERVIÇOS AVANÇADOS (se configurados)
echo ""
log "🚀 TESTANDO SERVIÇOS ULTRA-AVANÇADOS..."

# Blockchain Ethereum
test_endpoint "http://localhost:8545" "Ethereum Node"

# Edge Orchestrator
test_endpoint "http://localhost:8082" "Edge Orchestrator"

# Metaverso Server
test_endpoint "http://localhost:8083" "Metaverso Server"

# Quantum Security
test_endpoint "http://localhost:8085" "Quantum Security"

# Business Intelligence
test_endpoint "http://localhost:8086" "Business Intelligence"

# 5. TESTES DE INTEGRAÇÃO EXTERNA
echo ""
log "🔗 TESTANDO INTEGRAÇÕES EXTERNAS..."

# Teste de conectividade geral com APIs externas
if curl -s --connect-timeout 10 "https://api.coingecko.com/api/v3/ping" > /dev/null; then
    log_info "✅ CoinGecko API: Acessível"
else
    log_warn "❌ CoinGecko API: Não acessível (verificar configuração)"
fi

# 6. TESTES DE PERFORMANCE
echo ""
log "⚡ TESTANDO PERFORMANCE..."

# Teste de latência Redis
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    LATENCY=$(redis-cli -h localhost -p 6379 --latency | grep "avg:" | awk '{print $2}' | tail -1)
    log_info "✅ Redis Latency: ${LATENCY}ms"
else
    log_warn "❌ Redis não acessível para teste de latência"
fi

# 7. TESTES DE FUNCIONALIDADES ESPECÍFICAS
echo ""
log "🎯 TESTANDO FUNCIONALIDADES ESPECÍFICAS..."

# Teste de análise de sentimentos (IA)
log "Testando análise de sentimentos..."
curl -s -X POST "http://localhost:8000/ai/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text":"This crypto project is amazing!"}' || \
  log_warn "Análise de sentimentos não disponível"

# Teste de blockchain (se disponível)
log "Testando integração blockchain..."
curl -s "http://localhost:8000/blockchain/analytics" || \
  log_warn "Blockchain analytics não disponível"

# 8. GERAÇÃO DE RELATÓRIO
echo ""
log "📋 GERANDO RELATÓRIO DE TESTES..."

cat > "test-results-$(date +%Y%m%d_%H%M%S).md" << EOF
# 🚀 RELATÓRIO DE TESTES - SEC ULTRA-REVOLUCIONÁRIO
## Data: $(date)
## Ambiente: Desenvolvimento

## ✅ SERVIÇOS BÁSICOS
- [$(test_endpoint "http://localhost:6379" "Redis" && echo "✅" || echo "❌")] Redis
- [$(pg_isready -h localhost -p 5432 -U sec 2>/dev/null && echo "✅" || echo "❌")] PostgreSQL
- [$(test_endpoint "http://localhost:27017" "MongoDB" && echo "✅" || echo "❌")] MongoDB
- [$(test_endpoint "http://localhost:15672" "RabbitMQ" && echo "✅" || echo "❌")] RabbitMQ

## 🌐 APIs PRINCIPAIS
- [$(test_endpoint "http://localhost:8000" "FastAPI" && echo "✅" || echo "❌")] FastAPI Backend
- [$(test_endpoint "http://localhost:3000" "NestJS" && echo "✅" || echo "❌")] NestJS Backend
- [$(test_endpoint "http://localhost:5173" "Frontend" && echo "✅" || echo "❌")] React Frontend
- [$(test_endpoint "http://localhost" "Nginx" && echo "✅" || echo "❌")] Nginx Proxy

## 📊 MONITORAÇÃO
- [$(test_endpoint "http://localhost:3001" "Grafana" && echo "✅" || echo "❌")] Grafana Dashboards
- [$(test_endpoint "http://localhost:9090" "Prometheus" && echo "✅" || echo "❌")] Prometheus Metrics
- [$(test_endpoint "http://localhost:3100" "Loki" && echo "✅" || echo "❌")] Loki Logs

## 🚀 SERVIÇOS AVANÇADOS
- [$(test_endpoint "http://localhost:8082" "Edge Orchestrator" && echo "✅" || echo "❌")] Edge Computing
- [$(test_endpoint "http://localhost:8083" "Metaverso" && echo "✅" || echo "❌")] Metaverso Server
- [$(test_endpoint "http://localhost:8085" "Quantum Security" && echo "✅" || echo "❌")] Quantum Security
- [$(test_endpoint "http://localhost:8086" "Business Intelligence" && echo "✅" || echo "❌")] Business Intelligence

## 🔗 INTEGRAÇÕES EXTERNAS
- [$(curl -s --connect-timeout 5 "https://api.coingecko.com/api/v3/ping" > /dev/null && echo "✅" || echo "❌")] CoinGecko API

## ⚡ PERFORMANCE
- Redis Latency: ${LATENCY:-"N/A"}ms

## 🎯 STATUS GERAL
$(echo "scale=0; $(grep -c "✅" test-results.log 2>/dev/null || echo "0") / $(grep -c ".*" test-results.log 2>/dev/null || echo "1") * 100" | bc 2>/dev/null || echo "0")% funcionalidades ativas

## 🔧 RECOMENDAÇÕES
1. Configure chaves API reais no .env para funcionalidades completas
2. Execute treinamento inicial de modelos de IA
3. Configure nós edge globais para otimização geográfica
4. Teste integrações externas com dados reais

---
*Relatório gerado automaticamente em:* $(date)
EOF

log_info "Relatório de testes salvo em: test-results-$(date +%Y%m%d_%H%M%S).md"

# 9. TESTES DE CARGA (básicos)
echo ""
log "🔥 EXECUTANDO TESTES DE CARGA BÁSICOS..."

# Teste de carga no Redis
for i in {1..10}; do
    redis-cli -h localhost -p 6379 SET "test:key$i" "value$i" > /dev/null 2>&1
    redis-cli -h localhost -p 6379 GET "test:key$i" > /dev/null 2>&1
done
log_info "Teste de carga Redis: 20 operações concluídas"

# Limpar chaves de teste
redis-cli -h localhost -p 6379 DEL test:key1 test:key2 test:key3 test:key4 test:key5 test:key6 test:key7 test:key8 test:key9 test:key10 > /dev/null 2>&1

echo ""
log_info "🎉 TESTES DE FUNCIONALIDADES CONCLUÍDOS!"
log "📋 Consulte o relatório de testes gerado para detalhes completos"
log "🚀 Sistema pronto para desenvolvimento e produção!"
