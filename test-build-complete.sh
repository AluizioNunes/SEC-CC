#!/bin/bash
# 🚀 TESTE DE BUILD LOCAL ANTES DO DEPLOY NO PORTAINER
# Script para testar se o build funciona corretamente

echo "🚀 Testando build do frontend localmente..."

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

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    log_error "❌ package.json não encontrado. Execute este script na raiz do projeto."
    exit 1
fi

# 1. TESTAR INSTALAÇÃO DE DEPENDÊNCIAS
echo ""
log "📦 TESTE 1: Instalação de dependências..."

npm install --verbose

if [ $? -ne 0 ]; then
    log_error "❌ Falha na instalação de dependências"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Execute: npm install"
    echo "  - Verifique se package-lock.json existe"
    echo "  - Limpe cache: npm cache clean --force"
    exit 1
fi

log_info "✅ Dependências instaladas com sucesso"

# 2. TESTAR COMPILAÇÃO TYPESCRIPT
echo ""
log "🔷 TESTE 2: Compilação TypeScript..."

npx tsc -b --verbose

if [ $? -ne 0 ]; then
    log_error "❌ Falha na compilação TypeScript"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Verifique erros de tipos no código"
    echo "  - Execute: npx tsc --noEmit"
    echo "  - Verifique tsconfig.json"
    exit 1
fi

log_info "✅ TypeScript compilado com sucesso"

# 3. TESTAR BUILD DO VITE
echo ""
log "⚡ TESTE 3: Build do Vite..."

npm run build

if [ $? -ne 0 ]; then
    log_error "❌ Falha no build do Vite"
    echo ""
    echo "🔧 Possíveis soluções:"
    echo "  - Verifique erros no console"
    echo "  - Execute: npm run build --verbose"
    echo "  - Verifique vite.config.ts"
    echo "  - Verifique se há erros de import"
    exit 1
fi

log_info "✅ Build do Vite concluído com sucesso"

# 4. VERIFICAR OUTPUT DO BUILD
echo ""
log "📊 TESTE 4: Verificação do output..."

if [ -d "dist" ]; then
    FILE_COUNT=$(find dist -type f | wc -l)
    TOTAL_SIZE=$(du -sh dist | cut -f1)

    log_info "✅ Diretório dist criado com sucesso"
    log_info "📁 Número de arquivos: $FILE_COUNT"
    log_info "📊 Tamanho total: $TOTAL_SIZE"

    # Mostrar alguns arquivos importantes
    echo ""
    log "📋 Arquivos importantes no build:"
    ls -la dist/index.html 2>/dev/null || log_warn "index.html não encontrado"
    ls -la dist/assets/ 2>/dev/null || log_warn "Pasta assets não encontrada"

else
    log_error "❌ Diretório dist não foi criado"
    exit 1
fi

# 5. TESTAR BUILD DO DOCKER
echo ""
log "🐳 TESTE 5: Build do Docker..."

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

# 6. LIMPAR ARTEFATOS DE TESTE
echo ""
log "🧹 TESTE 6: Limpeza..."

# Remover imagem de teste
docker rmi cc-frontend:test 2>/dev/null || true

log_info "✅ Limpeza concluída"

# 7. RELATÓRIO FINAL
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 RELATÓRIO FINAL 🎉                       ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ ✅ Instalação de dependências: OK                              ║"
echo "║ ✅ Compilação TypeScript: OK                                   ║"
echo "║ ✅ Build do Vite: OK                                           ║"
echo "║ ✅ Output do build: OK                                         ║"
echo "║ ✅ Build do Docker: OK                                         ║"
echo "║ ✅ Limpeza: OK                                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
log_info "🎉 TESTE DE BUILD CONCLUÍDO COM SUCESSO!"
log "🚀 O sistema está pronto para deploy no Portainer"
echo ""
echo "📋 COMANDO RECOMENDADO PARA DEPLOY:"
echo "  docker-compose up -d"
echo ""
echo "🌐 URLs PARA TESTAR APÓS DEPLOY:"
echo "  Frontend: http://localhost:5173"
echo "  FastAPI:  http://localhost:8000/docs"
echo "  NestJS:   http://localhost:3000"
echo "  Grafana:  http://localhost:3001"
