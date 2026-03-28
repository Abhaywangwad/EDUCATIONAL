$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
$port = 8000

function Get-BasePythonCommand {
    $localPython311 = Join-Path $env:LocalAppData "Programs\Python\Python311\python.exe"
    if (Test-Path $localPython311) {
        return @($localPython311)
    }

    try {
        $python = Get-Command python -ErrorAction Stop
        return @($python.Source)
    }
    catch {
    }

    try {
        $launcher = Get-Command py -ErrorAction Stop
        return @($launcher.Source, "-3.11")
    }
    catch {
    }

    return $null
}

$basePythonCommand = @(Get-BasePythonCommand)
if (-not $basePythonCommand) {
    Write-Host "Python 3.11+ is not installed yet." -ForegroundColor Yellow
    Write-Host "Install Python, then run this script again." -ForegroundColor Yellow
    exit 1
}

$basePythonExecutable = $basePythonCommand[0]
$basePythonArgs = @()
if ($basePythonCommand.Length -gt 1) {
    $basePythonArgs = $basePythonCommand[1..($basePythonCommand.Length - 1)]
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating backend virtual environment..." -ForegroundColor Cyan
    & $basePythonExecutable @basePythonArgs -m venv (Join-Path $backendDir ".venv")
}

$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt")

$portInUse = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -gt 4 } |
    Select-Object -First 1
if ($portInUse) {
    Write-Host "Port $port is already in use by process $($portInUse.OwningProcess)." -ForegroundColor Yellow
    Write-Host "Stop the old server first, for example:" -ForegroundColor Yellow
    Write-Host "Stop-Process -Id $($portInUse.OwningProcess) -Force" -ForegroundColor White
    exit 1
}

Write-Host "Starting FastAPI backend on http://127.0.0.1:$port" -ForegroundColor Green
Write-Host "Keep this terminal open while the backend is running." -ForegroundColor Gray
Push-Location $backendDir
$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = ".\.venv\Lib\site-packages;."
    & $basePythonExecutable @basePythonArgs -m run_server $port
}
finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
