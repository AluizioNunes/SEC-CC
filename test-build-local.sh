#!/bin/bash
# 🚀 TESTE DE BUILD LOCAL ANTES DO DEPLOY
# Script para testar se o build funciona corretamente

echo "🚀 Testando build local antes do deploy..."

# Testar instalação de dependências
echo "📦 Testando instalação de dependências..."
cd /d/PROJETOS/SEC
npm install --verbose

if [ $? -ne 0 ]; then
    echo "❌ Falha na instalação de dependências"
    exit 1
fi

echo "✅ Dependências instaladas com sucesso"

# Testar TypeScript compilation
echo "🔷 Testando compilação TypeScript..."
npx tsc -b

if [ $? -ne 0 ]; then
    echo "❌ Falha na compilação TypeScript"
    exit 1
fi

echo "✅ TypeScript compilado com sucesso"

# Testar build do Vite
echo "⚡ Testando build do Vite..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Falha no build do Vite"
    exit 1
fi

echo "✅ Build do Vite concluído com sucesso"

# Verificar se o dist foi criado
if [ -d "dist" ]; then
    echo "✅ Diretório dist criado com sucesso"
    echo "📊 Tamanho do build: $(du -sh dist | cut -f1)"
else
    echo "❌ Diretório dist não foi criado"
    exit 1
fi

echo ""
echo "🎉 TESTE DE BUILD CONCLUÍDO COM SUCESSO!"
echo "✅ O sistema está pronto para deploy"
echo ""
echo "📋 Arquivo recomendado para deploy: docker-compose-simple.yml"
echo "🚀 Execute: docker-compose -f docker-compose-simple.yml up -d"
