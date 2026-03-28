$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"

Push-Location $frontendDir
try {
    if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
        npm.cmd install
    }

    Write-Host "Starting Next.js frontend on http://localhost:3000" -ForegroundColor Green
    npm.cmd run dev
}
finally {
    Pop-Location
}
