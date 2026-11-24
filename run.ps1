<#
.SYNOPSIS
  Khởi động toàn bộ hệ thống Pet-Auto trên Windows (không Docker).
  - Mosquitto MQTT broker
  - FastAPI + Uvicorn (Python)
  - Mở Dashboard trong trình duyệt

.PARAMETER NoBrowser
  Chỉ in địa chỉ, không mở trình duyệt.

.PARAMETER DemoOnly
  Chỉ chạy Python HTTP server phục vụ demo nhận dạng (không cần MQTT).

.PARAMETER SkipMqtt
  Bỏ qua khởi động Mosquitto (nếu đã chạy sẵn hoặc không cần).
#>
[CmdletBinding()]
param(
    [switch]$DemoOnly,
    [switch]$NoBrowser,
    [switch]$SkipMqtt
)

$ErrorActionPreference = 'Stop'
$serverDir = Join-Path $PSScriptRoot 'server'

# ── Hàm tiện ích ────────────────────────────────
function Wait-ForUrl([string]$Url, [int]$TimeoutSec = 30) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    do {
        try {
            $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            return $true
        } catch {
            Start-Sleep -Seconds 1
        }
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Find-Mosquitto {
    $cmd = Get-Command mosquitto -CommandType Application -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $paths = @(
        "$env:ProgramFiles\mosquitto\mosquitto.exe",
        "${env:ProgramFiles(x86)}\mosquitto\mosquitto.exe",
        "C:\mosquitto\mosquitto.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Find-Python {
    foreach ($name in 'python', 'python3', 'py') {
        $cmd = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}

function Ensure-Venv {
    $venvDir = Join-Path $serverDir '.venv'
    $venvPython = Join-Path $venvDir 'Scripts\python.exe'

    if (!(Test-Path $venvPython)) {
        $systemPython = Find-Python
        if (!$systemPython) {
            throw 'Python khong tim thay. Cai Python 3.10+ va them vao PATH.'
        }
        Write-Host "[SETUP] Tao virtual environment tai $venvDir ..."
        & $systemPython -m venv $venvDir
        if ($LASTEXITCODE -ne 0) { throw 'Khong tao duoc virtual environment.' }
    }

    $reqFile = Join-Path $serverDir 'requirements.txt'
    Write-Host '[SETUP] Cai dat dependencies...'
    & $venvPython -m pip install -q -r $reqFile
    if ($LASTEXITCODE -ne 0) { throw 'pip install that bai.' }

    return $venvPython
}

# ── Chế độ DemoOnly ─────────────────────────────
if ($DemoOnly) {
    $py = Find-Python
    if (!$py) { throw 'Python khong tim thay.' }
    $dashDir = Join-Path $serverDir 'dashboard'
    $baseUrl = 'http://localhost:8080'
    Write-Host "[DEMO] Phuc vu dashboard tai $baseUrl ..."
    $web = Start-Process -FilePath $py -ArgumentList "-m http.server 8080 --bind 127.0.0.1 --directory `"$dashDir`"" -NoNewWindow -PassThru
    try {
        if (Wait-ForUrl "$baseUrl/pet-demo.js" -TimeoutSec 10) {
            Write-Host "Dashboard  $baseUrl/"
            Write-Host "Pet demo   $baseUrl/pet-demo.html"
            if (!$NoBrowser) { Start-Process "$baseUrl/pet-demo.html" }
        }
        Write-Host 'Nhan Ctrl+C de dung.'
        while (!$web.WaitForExit(500)) {}
    } finally {
        if (!$web.HasExited) { Stop-Process -InputObject $web }
    }
    return
}

# ── Chuẩn bị ────────────────────────────────────
Push-Location -LiteralPath $PSScriptRoot
$jobs = @()

try {
    # Tạo file placeholder nếu chưa có
    $envFile = Join-Path $serverDir '.env'
    $envExample = Join-Path $serverDir '.env.example'
    if (!(Test-Path $envFile)) {
        Copy-Item $envExample $envFile
        Write-Host '[SETUP] Tao server/.env tu .env.example'
    }
    $fbCred = Join-Path $serverDir 'firebase-credentials.json'
    if (!(Test-Path $fbCred)) {
        Set-Content $fbCred '{}' -Encoding ascii
        Write-Host '[SETUP] Tao firebase-credentials.json placeholder'
    }

    # ── Mosquitto ────────────────────────────────
    if (!$SkipMqtt) {
        $mqExe = Find-Mosquitto
        if (!$mqExe) {
            Write-Host ''
            Write-Host '╔══════════════════════════════════════════════════════╗'
            Write-Host '║  Mosquitto chua duoc cai dat.                       ║'
            Write-Host '║  Tai tu: https://mosquitto.org/download/            ║'
            Write-Host '║  Hoac chay voi -SkipMqtt neu MQTT da chay san.      ║'
            Write-Host '╚══════════════════════════════════════════════════════╝'
            Write-Host ''
            throw 'Mosquitto khong tim thay.'
        }

        $mqConf = Join-Path $serverDir 'mosquitto\mosquitto-local.conf'
        Write-Host "[MQTT] Khoi dong Mosquitto: $mqExe"
        $mqProc = Start-Process -FilePath $mqExe -ArgumentList "-c `"$mqConf`" -v" -NoNewWindow -PassThru
        $jobs += $mqProc
        Start-Sleep -Seconds 2

        if ($mqProc.HasExited) {
            Write-Host '[MQTT] Mosquitto da thoat bat thuong. Kiem tra cong 1883 co bi chiem khong.'
            Write-Host '       Neu Mosquitto Windows Service dang chay, dung: net stop mosquitto'
            throw 'Mosquitto khong khoi dong duoc.'
        }
        Write-Host '[MQTT] Mosquitto dang chay tren port 1883'
    } else {
        Write-Host '[MQTT] Bo qua khoi dong Mosquitto (--SkipMqtt)'
    }

    # ── Python venv + dependencies ───────────────
    $venvPython = Ensure-Venv

    # ── FastAPI / Uvicorn ────────────────────────
    Write-Host '[API] Khoi dong FastAPI + Uvicorn...'
    $uvicornArgs = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    $apiProc = Start-Process -FilePath $venvPython -ArgumentList $uvicornArgs -WorkingDirectory $serverDir -NoNewWindow -PassThru
    $jobs += $apiProc

    if (Wait-ForUrl 'http://localhost:8000/api/health' -TimeoutSec 30) {
        Write-Host ''
        Write-Host '╔══════════════════════════════════════════════════════╗'
        Write-Host '║  He thong Pet-Auto da san sang!                      ║'
        Write-Host '╠══════════════════════════════════════════════════════╣'
        Write-Host '║  Dashboard:    http://localhost:8000                  ║'
        Write-Host '║  Swagger API:  http://localhost:8000/docs             ║'
        Write-Host '║  Pet Demo:     http://localhost:8000/pet-demo         ║'
        Write-Host '║  MQTT Broker:  localhost:1883                         ║'
        Write-Host '╚══════════════════════════════════════════════════════╝'
        Write-Host ''
        if (!$NoBrowser) {
            Start-Process 'http://localhost:8000'
        }
    } else {
        Write-Host '[API] API chua san sang sau 30 giay. Kiem tra log phia tren.'
    }

    Write-Host 'Nhan Ctrl+C de dung tat ca dich vu.'
    while ($true) {
        Start-Sleep -Seconds 2
        $exited = $jobs | Where-Object { $_.HasExited }
        if ($exited.Count -gt 0) {
            Write-Host '[WARN] Mot dich vu da thoat bat thuong.'
            break
        }
    }

} finally {
    Write-Host '[STOP] Dang tat cac dich vu...'
    foreach ($j in $jobs) {
        if (!$j.HasExited) {
            try { Stop-Process -InputObject $j -Force } catch {}
        }
    }
    Pop-Location
    Write-Host '[STOP] Da dung tat ca.'
}
