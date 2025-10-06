#!/bin/bash
# 🚀 TESTE COMPLETO ANTES DO DEPLOY NO PORTAINER
# Script para validar todo o ambiente antes do deploy

echo "🚀 Iniciando teste completo do ambiente SEC Ultra-Revolutionary..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 1. TESTE DE DEPENDÊNCIAS NPM
echo ""
log "📦 TESTE 1: Verificação de dependências NPM..."

if [ ! -f "package.json" ]; then
    log_error "❌ package.json não encontrado"
    exit 1
fi

log_info "✅ package.json encontrado"

# Verificar se npm install funciona
npm install --silent

if [ $? -ne 0 ]; then
    log_error "❌ Falha na instalação de dependências"
    exit 1
fi

log_info "✅ Dependências instaladas com sucesso"

# 2. TESTE DE COMPILAÇÃO TYPESCRIPT
echo ""
log "🔷 TESTE 2: Verificação de TypeScript..."

npx tsc --noEmit --skipLibCheck

if [ $? -ne 0 ]; then
    log_error "❌ Problemas de TypeScript encontrados"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Verifique erros de tipos no código"
    echo "  - Execute: npx tsc --noEmit"
    exit 1
fi

log_info "✅ TypeScript compilado sem erros"

# 3. TESTE DE BUILD DO VITE
echo ""
log "⚡ TESTE 3: Verificação de build do Vite..."

npm run build

if [ $? -ne 0 ]; then
    log_error "❌ Falha no build do Vite"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Verifique configuração do Vite"
    echo "  - Execute: npm run build --verbose"
    echo "  - Verifique se há erros de import"
    exit 1
fi

log_info "✅ Build do Vite concluído com sucesso"

# 4. VERIFICAÇÃO DO OUTPUT DO BUILD
echo ""
log "📊 TESTE 4: Verificação do output do build..."

if [ -d "dist" ]; then
    FILE_COUNT=$(find dist -type f | wc -l)
    TOTAL_SIZE=$(du -sh dist | cut -f1)

    log_info "✅ Diretório dist criado com sucesso"
    log_info "📁 Número de arquivos: $FILE_COUNT"
    log_info "📊 Tamanho total: $TOTAL_SIZE"

    # Verificar arquivos críticos
    if [ -f "dist/index.html" ]; then
        log_info "✅ index.html encontrado"
    else
        log_error "❌ index.html não encontrado no build"
        exit 1
    fi

else
    log_error "❌ Diretório dist não foi criado"
    exit 1
fi

# 5. TESTE DE BUILD DO DOCKER
echo ""
log "🐳 TESTE 5: Verificação de build do Docker..."

# Tentar fazer build da imagem
docker build -f ./docker/frontend/Dockerfile -t cc-frontend:test .

if [ $? -ne 0 ]; then
    log_error "❌ Falha no build do Docker"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Verifique o Dockerfile"
    echo "  - Verifique se há espaço suficiente em disco"
    echo "  - Execute: docker system prune"
    exit 1
fi

log_info "✅ Build do Docker concluído com sucesso"

# 6. TESTE DE COMPOSE SYNTAX
echo ""
log "📋 TESTE 6: Verificação de sintaxe do docker-compose..."

docker-compose config --quiet

if [ $? -ne 0 ]; then
    log_error "❌ Erro na configuração do docker-compose"
    exit 1
fi

log_info "✅ Sintaxe do docker-compose válida"

# 7. LIMPEZA DE ARTEFATOS DE TESTE
echo ""
log "🧹 TESTE 7: Limpeza de artefatos..."

# Remover imagem de teste
docker rmi cc-frontend:test 2>/dev/null || true

# Remover dist de teste se necessário
# rm -rf dist

log_info "✅ Limpeza concluída"

# 8. RELATÓRIO FINAL
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 RELATÓRIO FINAL 🎉                       ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ ✅ Dependências NPM: OK                                        ║"
echo "║ ✅ TypeScript: OK                                              ║"
echo "║ ✅ Build do Vite: OK                                           ║"
echo "║ ✅ Output do build: OK                                         ║"
echo "║ ✅ Build do Docker: OK                                         ║"
echo "║ ✅ Sintaxe docker-compose: OK                                  ║"
echo "║ ✅ Limpeza: OK                                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
log_info "🎉 TODOS OS TESTES PASSARAM!"
log "🚀 Sistema pronto para deploy no Portainer"
echo ""
echo "📋 COMANDO RECOMENDADO PARA DEPLOY:"
echo "  docker-compose up -d"
echo ""
echo "🌐 URLs PARA TESTAR APÓS DEPLOY:"
echo "  Frontend: http://localhost:5173"
echo "  FastAPI:  http://localhost:8000/docs"
echo "  NestJS:   http://localhost:3000"
echo "  Grafana:  http://localhost:3001"
