[CmdletBinding()]param([string]$ServiceName = "postgres")
$ErrorActionPreference = 'Stop'

function Load-DotEnv { param([string]$Path)
    if (-not (Test-Path $Path)) { throw "Env file not found: $Path" }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim(); if ($line -eq '' -or $line.StartsWith('#')) { return }
        $parts = $line -split '=', 2; if ($parts.Count -ge 2) {
            $name = $parts[0].Trim(); $value = $parts[1].Trim()
            if ($value.StartsWith('"') -and $value.EndsWith('"')) { $value = $value.Substring(1, $value.Length - 2) }
            [System.Environment]::SetEnvironmentVariable($name, $value); Set-Item -Path "Env:$name" -Value $value }
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$envPath = Join-Path $repoRoot '.env'
Load-DotEnv -Path $envPath

# Required vars
$pgUser = $env:POSTGRES_USER; $pgDb = $env:POSTGRES_DB
if (-not $pgUser -or -not $pgDb) { throw "POSTGRES_USER and POSTGRES_DB must be set in .env" }

# Admin vars
$adminUser = $env:ADMIN_USERNAME; if (-not $adminUser) { $adminUser = 'admin' }
$adminReset = $env:ADMIN_RESET_PASSWORD; if (-not $adminReset) { $adminReset = 'changeme123' }
$sysActor = $env:CADASTRANTE_SYSTEM; if (-not $sysActor) { $sysActor = 'SYSTEM' }

$sqlPath = Join-Path $repoRoot 'Backend\Scripts\AdminResetPassword.sql'
if (-not (Test-Path $sqlPath)) { throw "SQL file not found: $sqlPath" }

Write-Host "Resetando senha do usuário '$adminUser' no banco '$pgDb'..." -ForegroundColor Cyan

$psqlArgs = @('exec','-T', $ServiceName,
    'psql','-U', $pgUser,'-d', $pgDb,
    '-v', "ADMIN_USERNAME=$adminUser",
    '-v', "ADMIN_RESET_PASSWORD=$adminReset",
    '-v', "CADASTRANTE_SYSTEM=$sysActor",
    '-f','-')

$dockerCmd = 'docker compose ' + ($psqlArgs -join ' ')
$script:LASTEXITCODE = 0
(Get-Content -Raw $sqlPath) | & powershell -NoProfile -Command $dockerCmd
if ($LASTEXITCODE -ne 0) { throw "psql returned non-zero exit code: $LASTEXITCODE" }

Write-Host "✅ Reset de senha concluído." -ForegroundColor Green