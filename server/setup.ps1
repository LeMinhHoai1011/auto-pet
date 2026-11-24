# Pet Feeder Server — Setup Script
# Creates venv, installs dependencies, initializes storage directories.

$ErrorActionPreference = "Stop"
$serverDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Pet Feeder Server Setup ===" -ForegroundColor Cyan

# 1. Python venv
$venvDir = Join-Path $serverDir ".venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvDir
} else {
    Write-Host "[1/4] Virtual environment already exists." -ForegroundColor Green
}

# Activate
$activate = Join-Path $venvDir "Scripts\Activate.ps1"
. $activate

# 2. Install dependencies
Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r (Join-Path $serverDir "requirements.txt")

# 3. Storage directories
Write-Host "[3/4] Creating storage directories..." -ForegroundColor Yellow
$dirs = @("storage\pets", "storage\pending")
foreach ($d in $dirs) {
    $p = Join-Path $serverDir $d
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

# 4. .env file
$envFile = Join-Path $serverDir ".env"
$envExample = Join-Path $serverDir ".env.example"
if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "[4/4] .env created from .env.example — edit it with your settings." -ForegroundColor Yellow
    } else {
        Write-Host "[4/4] No .env.example found — skipping .env creation." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "[4/4] .env already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Run .\download-models.ps1 to pre-download AI models"
Write-Host "  2. Run .\start.ps1 to start the server"
