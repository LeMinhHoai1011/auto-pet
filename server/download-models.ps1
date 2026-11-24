# Pet Feeder Server — Download AI Models
# Pre-downloads YOLOv8n and DINOv2 so the first pipeline start is fast.

$ErrorActionPreference = "Stop"
$serverDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate venv
$activate = Join-Path $serverDir ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
. $activate

Write-Host "=== Downloading AI Models ===" -ForegroundColor Cyan

# 1. YOLOv8n (ultralytics downloads to ~/.config/ultralytics or %APPDATA%)
Write-Host "[1/3] Downloading YOLOv8n (COCO)..." -ForegroundColor Yellow
python -I -c "from ultralytics import YOLO; m = YOLO('yolov8n.pt'); print('YOLOv8n ready:', m.model_name)"

# 2. DINOv2 ViT-S/14 (torch.hub downloads to ~/.cache/torch/hub)
Write-Host "[2/3] Downloading DINOv2 ViT-S/14..." -ForegroundColor Yellow
python -I -c "import torch; m = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14'); print('DINOv2 ready:', type(m).__name__)"

# 3. OpenCV Haar cascade (bundled with opencv-python)
Write-Host "[3/3] Verifying Haar cascade..." -ForegroundColor Yellow
python -I -c "import cv2, os; p = os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalcatface_extended.xml'); assert os.path.exists(p), f'Not found: {p}'; print('Haar cascade OK:', p)"

Write-Host ""
Write-Host "All models downloaded successfully!" -ForegroundColor Green
