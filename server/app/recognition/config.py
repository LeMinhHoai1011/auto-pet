"""Recognition pipeline configuration."""

from __future__ import annotations

import os
from pathlib import Path

_server_dir = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = _server_dir / "storage"
PETS_DIR = STORAGE_DIR / "pets"
PENDING_DIR = STORAGE_DIR / "pending"
MODELS_DIR = _server_dir / "models"

PETS_DIR.mkdir(parents=True, exist_ok=True)
PENDING_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# ── Detection ────────────────────────────────────────────
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
YOLO_CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", "0.45"))
YOLO_CAT_CLASS_ID = 15   # COCO class id for "cat"
YOLO_DOG_CLASS_ID = 16   # COCO class id for "dog"
YOLO_PET_CLASS_IDS = [15, 16]  # detect both cats and dogs
YOLO_DEVICE = os.getenv("YOLO_DEVICE", "")  # "" = auto, "cpu", "cuda:0"

# ── Tracking ─────────────────────────────────────────────
TRACK_THRESH = float(os.getenv("TRACK_THRESH", "0.4"))
TRACK_BUFFER = int(os.getenv("TRACK_BUFFER", "30"))
MATCH_THRESH = float(os.getenv("MATCH_THRESH", "0.8"))

# ── Cat face detection ───────────────────────────────────
HAAR_CASCADE = os.getenv(
    "HAAR_CASCADE",
    "haarcascade_frontalcatface_extended.xml",
)
FACE_MIN_SIZE = int(os.getenv("FACE_MIN_SIZE", "40"))
FACE_SCALE_FACTOR = float(os.getenv("FACE_SCALE_FACTOR", "1.1"))
FACE_MIN_NEIGHBORS = int(os.getenv("FACE_MIN_NEIGHBORS", "3"))

# ── Image quality ────────────────────────────────────────
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "80.0"))
MIN_BRIGHTNESS = float(os.getenv("MIN_BRIGHTNESS", "30.0"))
MAX_BRIGHTNESS = float(os.getenv("MAX_BRIGHTNESS", "240.0"))
MIN_CROP_SIZE = int(os.getenv("MIN_CROP_SIZE", "64"))

# ── Embedding ────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "dinov2_vits14")
EMBEDDING_DIM = 384  # DINOv2 ViT-S/14
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "")  # "" = auto
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "8"))

# ── Identity matching ────────────────────────────────────
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.55"))
UNCERTAIN_THRESHOLD = float(os.getenv("UNCERTAIN_THRESHOLD", "0.45"))
MIN_MARGIN = float(os.getenv("MIN_MARGIN", "0.05"))
CONFIRMATION_FRAMES = int(os.getenv("CONFIRMATION_FRAMES", "3"))

# ── Collection ───────────────────────────────────────────
SESSION_CONFIRM_SEC = float(os.getenv("SESSION_CONFIRM_SEC", "2.0"))
CAPTURE_INTERVAL_SEC = float(os.getenv("CAPTURE_INTERVAL_SEC", "1.0"))
SESSION_DURATION_SEC = float(os.getenv("SESSION_DURATION_SEC", "20.0"))
MAX_IMAGES_PER_SESSION = int(os.getenv("MAX_IMAGES_PER_SESSION", "15"))
MIN_IMAGES_PER_SESSION = int(os.getenv("MIN_IMAGES_PER_SESSION", "5"))
MAX_IMAGES_PER_PET = int(os.getenv("MAX_IMAGES_PER_PET", "100"))
PENDING_RETENTION_DAYS = int(os.getenv("PENDING_RETENTION_DAYS", "7"))

# ── Registration ─────────────────────────────────────────
MIN_REGISTRATION_IMAGES = int(os.getenv("MIN_REGISTRATION_IMAGES", "5"))
MAX_REGISTRATION_IMAGES = int(os.getenv("MAX_REGISTRATION_IMAGES", "30"))
REGISTRATION_DURATION_SEC = float(os.getenv("REGISTRATION_DURATION_SEC", "30.0"))
DUPLICATE_SIMILARITY = float(os.getenv("DUPLICATE_SIMILARITY", "0.95"))

# ── Camera / Pipeline ───────────────────────────────────
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")  # 0=webcam, url, file path
CAMERA_FPS_LIMIT = int(os.getenv("CAMERA_FPS_LIMIT", "10"))
AI_FPS_LIMIT = int(os.getenv("AI_FPS_LIMIT", "5"))
IDLE_FPS_LIMIT = int(os.getenv("IDLE_FPS_LIMIT", "1"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "480"))

# ── ROI (Region of Interest) ────────────────────────────
# Normalized coordinates [x1, y1, x2, y2] where (0,0) is top-left
ROI_ENABLED = os.getenv("ROI_ENABLED", "false").lower() == "true"
ROI_X1 = float(os.getenv("ROI_X1", "0.0"))
ROI_Y1 = float(os.getenv("ROI_Y1", "0.0"))
ROI_X2 = float(os.getenv("ROI_X2", "1.0"))
ROI_Y2 = float(os.getenv("ROI_Y2", "1.0"))

# ── Model version tracking ───────────────────────────────
EMBEDDING_MODEL_VERSION = f"{EMBEDDING_MODEL}_v1"


def resolve_device(preferred: str = "") -> str:
    """Return 'cuda' if available and requested, else 'cpu'."""
    import torch
    if preferred == "cpu":
        return "cpu"
    if preferred and preferred.startswith("cuda"):
        if torch.cuda.is_available():
            return preferred
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"
