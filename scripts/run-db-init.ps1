[CmdletBinding()]
param(
    [string]$ServiceName = "postgres"
)

$ErrorActionPreference = 'Stop'

function Load-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "Env file not found: $Path" }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq '' -or $line.StartsWith('#')) { return }
        $parts = $line -split '=', 2
        if ($parts.Count -ge 2) {
            $name = $parts[0].Trim()
            $value = $parts[1].Trim()
            # Strip surrounding quotes if present
            if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            [System.Environment]::SetEnvironmentVariable($name, $value)
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$envPath = Join-Path $repoRoot '.env'
Load-DotEnv -Path $envPath

# Required vars
$pgUser = $env:POSTGRES_USER
$pgDb   = $env:POSTGRES_DB
if (-not $pgUser -or -not $pgDb) { throw "POSTGRES_USER and POSTGRES_DB must be set in .env" }

# Optional admin variables with sensible defaults
$adminName = $env:ADMIN_NAME
if (-not $adminName) { $adminName = 'ADMINISTRADOR DO SISTEMA' }
$adminUser = $env:ADMIN_USERNAME
if (-not $adminUser) { $adminUser = 'admin' }
$adminEmail = $env:ADMIN_EMAIL
if (-not $adminEmail) { $adminEmail = 'admin@example.com' }
$adminPassword = $env:ADMIN_PASSWORD
if (-not $adminPassword) { $adminPassword = 'changeme123' }
$defaultUserPassword = $env:DEFAULT_USER_PASSWORD
if (-not $defaultUserPassword) { $defaultUserPassword = 'changeme123' }
$sysActor = $env:CADASTRANTE_SYSTEM
if (-not $sysActor) { $sysActor = 'SYSTEM' }

$sqlPath = Join-Path $repoRoot 'Backend\Scripts\AdminBasicDB.sql'
if (-not (Test-Path $sqlPath)) { throw "SQL file not found: $sqlPath" }

Write-Host "Running DB init against service '$ServiceName' and database '$pgDb'..." -ForegroundColor Cyan
Write-Host "  User: $pgUser" -ForegroundColor DarkCyan
Write-Host "  Admin: $adminUser <$adminEmail>" -ForegroundColor DarkCyan

# Compose psql command
$psqlArgs = @(
    'exec','-T', $ServiceName,
    'psql','-U', $pgUser,'-d', $pgDb,
    '-v', "POSTGRES_USER=$pgUser",
    '-v', "ADMIN_NAME=$adminName",
    '-v', "ADMIN_USERNAME=$adminUser",
    '-v', "ADMIN_EMAIL=$adminEmail",
    '-v', "ADMIN_PASSWORD=$adminPassword",
    '-v', "DEFAULT_USER_PASSWORD=$defaultUserPassword",
    '-v', "CADASTRANTE_SYSTEM=$sysActor",
    '-f','-'
)

# Pipe SQL content into psql via docker compose
$dockerCmd = 'docker compose ' + ($psqlArgs -join ' ')
$script:LASTEXITCODE = 0
(Get-Content -Raw $sqlPath) | & powershell -NoProfile -Command $dockerCmd
if ($LASTEXITCODE -ne 0) { throw "psql returned non-zero exit code: $LASTEXITCODE" }

Write-Host "✅ Database initialization completed." -ForegroundColor Green