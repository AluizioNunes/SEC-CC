# Script simples para configurar chaves API basicas

Write-Host "Configurando chaves API para producao..." -ForegroundColor Green

# Backup do .env atual
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .env ".env.backup.$timestamp"

# Configurar chaves basicas
(Get-Content .env) -replace 'your_openai_api_key_here', 'sk-configure-sua-chave-openai-aqui' | Set-Content .env
(Get-Content .env) -replace 'YOUR_INFURA_KEY', 'configure-seu-project-id-infura-aqui' | Set-Content .env

Write-Host "✅ Chaves basicas configuradas!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Configure chaves API reais no arquivo .env" -ForegroundColor Yellow
Write-Host "2. Execute: docker-compose up -d" -ForegroundColor Yellow
Write-Host "3. Teste todas as funcionalidades" -ForegroundColor Yellow
Write-Host "4. Configure monitoramento no Grafana" -ForegroundColor Yellow
