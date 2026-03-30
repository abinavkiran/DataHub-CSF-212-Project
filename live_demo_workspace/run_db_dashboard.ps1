param(
    [int]$Port = 8090
)

$syncScript = Join-Path $PSScriptRoot "..\sync_credentials_env.ps1"
& $syncScript
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Starting DB dashboard at http://localhost:$Port"
docker compose run --rm -p "${Port}:${Port}" dev-env python -m uvicorn live_demo_workspace.db_dashboard:app --host 0.0.0.0 --port $Port
