# Pet Feeder Server — Start Script
# Activates venv, ensures storage dirs exist, starts uvicorn.

$ErrorActionPreference = "Stop"
$serverDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate venv
$activate = Join-Path $serverDir ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
. $activate

# Ensure storage dirs
foreach ($d in @("storage\pets", "storage\pending")) {
    $p = Join-Path $serverDir $d
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

Write-Host "Starting Pet Feeder Server..." -ForegroundColor Cyan
Write-Host "Dashboard:  http://localhost:8000/"
Write-Host "AI Page:    http://localhost:8000/ai"
Write-Host "API Docs:   http://localhost:8000/docs"
Write-Host ""

Set-Location $serverDir
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
