$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $repoRoot "backend\.env"

if (-not (Test-Path $envPath)) {
    Write-Host "backend/.env was not found." -ForegroundColor Red
    exit 1
}

$secureKey = Read-Host "Paste your OpenAI API key" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)

try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ([string]::IsNullOrWhiteSpace($plainKey)) {
    Write-Host "No key entered. Nothing changed." -ForegroundColor Yellow
    exit 1
}

$content = Get-Content -Raw $envPath
$updated = [Regex]::Replace(
    $content,
    '(?m)^OPENAI_API_KEY=.*$',
    "OPENAI_API_KEY=$plainKey"
)

Set-Content -LiteralPath $envPath -Value $updated -NoNewline
Write-Host "OpenAI API key saved to backend/.env" -ForegroundColor Green
