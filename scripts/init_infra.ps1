# BharatGov Access - Windows PowerShell Local Initialization Script

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " BharatGov Access - Local Dev Infrastructure Init" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "[*] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "[*] Creating data directories..." -ForegroundColor Green
$dirs = @(
    "data/raw/html",
    "data/raw/screenshots",
    "data/raw/axe",
    "data/raw/lighthouse",
    "data/raw/headers",
    "data/raw/metadata",
    "data/processed",
    "data/releases",
    "data/quarantine",
    "data/logs"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

Write-Host "[*] Checking Python environment and directories..." -ForegroundColor Green
python -c "from configs.settings import settings; settings.ensure_dirs(); print('Settings loaded successfully:', settings.environment)"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Infrastructure initialization complete!" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
