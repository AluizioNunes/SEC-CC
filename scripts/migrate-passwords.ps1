Param(
  [string]$ServiceName = "postgres",
  [string]$DbUser = "postgres",
  [string]$DbName = "postgres",
  [string]$SysActor = "PASSWORD-MIGRATION"
)

$ErrorActionPreference = 'Stop'

$sqlPath = Join-Path $PSScriptRoot '..' 'Backend' 'Scripts' 'MigratePlaintextPasswords.sql'
if (-not (Test-Path $sqlPath)) { throw "SQL script not found: $sqlPath" }

Write-Host "🚀 Iniciando migração de senhas para bcrypt..." -ForegroundColor Cyan

$psqlArgs = @('exec','-T', $ServiceName,
    'psql','-U', $DbUser,'-d', $DbName,
    '-v', "CADASTRANTE_SYSTEM=$SysActor",
    '-f','-')

# Executa docker compose diretamente e envia o conteúdo do SQL via STDIN
$script:LASTEXITCODE = 0
Get-Content -Raw $sqlPath | & docker compose @psqlArgs
if ($LASTEXITCODE -ne 0) { throw "psql retornou código de saída diferente de zero: $LASTEXITCODE" }

Write-Host "✅ Migração concluída com sucesso." -ForegroundColor Green