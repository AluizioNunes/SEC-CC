param(
    [Parameter(Mandatory = $true)]
    [string]$Url,

    [Parameter(Mandatory = $true)]
    [string]$Username,

    [Parameter(Mandatory = $true)]
    [string]$Password,

    [Parameter(Mandatory = $true)]
    [int]$EndpointId,

    [Parameter(Mandatory = $true)]
    [string]$StackName,

    [Parameter(Mandatory = $false)]
    [string]$ComposeFilePath = "docker-compose.yml",

    [Parameter(Mandatory = $false)]
    [switch]$CreateIfMissing
)

$ErrorActionPreference = 'Stop'

Write-Host "Authenticating to Portainer at $Url ..."

try {
    $authBody = @{ username = $Username; password = $Password } | ConvertTo-Json
    $auth = Invoke-RestMethod -Uri "$Url/api/auth" -Method Post -Body $authBody -ContentType "application/json"
} catch {
    throw "Failed to authenticate to Portainer: $($_.Exception.Message)"
}

$token = $auth.jwt
if (-not $token) { throw "Authentication succeeded but no JWT token returned." }
$headers = @{ Authorization = "Bearer $token" }

if (-not (Test-Path -LiteralPath $ComposeFilePath)) {
    throw "Compose file not found at path: $ComposeFilePath"
}

$composeContent = Get-Content -Raw -LiteralPath $ComposeFilePath

Write-Host "Finding stack '$StackName' on endpoint $EndpointId ..."
try {
    $stacks = Invoke-RestMethod -Uri "$Url/api/stacks" -Method Get -Headers $headers
} catch {
    throw "Failed to list stacks: $($_.Exception.Message)"
}

$stack = $stacks | Where-Object { $_.Name -eq $StackName -and $_.EndpointId -eq $EndpointId }

if (-not $stack -and $CreateIfMissing) {
    Write-Host "Stack not found; creating stack '$StackName' ..."
    $createBody = @{ Name = $StackName; StackFileContent = $composeContent; Env = @() } | ConvertTo-Json -Depth 6
    $createUri = "$Url/api/stacks?type=2&method=file&endpointId=$EndpointId" # type=2 -> docker-compose (standalone)
    try {
        $createResp = Invoke-RestMethod -Uri $createUri -Method Post -Headers $headers -ContentType "application/json" -Body $createBody
        $stackId = $createResp.Id
        Write-Host "Stack created with ID $stackId."
    } catch {
        throw "Failed to create stack: $($_.Exception.Message)"
    }
}
elseif (-not $stack) {
    throw "Stack '$StackName' not found on endpoint $EndpointId. Use -CreateIfMissing to create it."
}
else {
    $stackId = $stack.Id
    Write-Host "Updating stack '$StackName' (ID $stackId) ..."
    # Preserve existing env vars from the stack if available
    $envVars = $stack.Env
    if (-not $envVars) { $envVars = @() }
    $updateBody = @{ StackFileContent = $composeContent; Prune = $true; Env = $envVars } | ConvertTo-Json -Depth 6
    $updateUri = "$Url/api/stacks/$stackId?endpointId=$EndpointId&method=file"
    try {
        $updateResp = Invoke-RestMethod -Uri $updateUri -Method Put -Headers $headers -ContentType "application/json" -Body $updateBody
        Write-Host "Stack updated and redeploy requested."
    } catch {
        throw "Failed to update stack: $($_.Exception.Message)"
    }
}

Write-Host "Done. Please monitor the stack in Portainer UI for health stabilization."