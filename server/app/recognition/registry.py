"""Pet registry — manages pet profiles and their recognition data.

Provides synchronous helpers that work with the database and the in-memory
embedding store.  Higher-level async wrappers live in the API layer.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path

import cv2
import numpy as np

from . import config as cfg
from .embedding import extract_embedding, extract_embeddings_batch, get_model_version
from .face_detector import detect_cat_face
from .quality_filter import assess_quality, compute_phash, is_duplicate
from .detector import detect_cats
from .matcher import embedding_store

logger = logging.getLogger("recognition.registry")


def _pet_dir(pet_id: int) -> Path:
    d = cfg.PETS_DIR / str(pet_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_pet_image(pet_id: int, image_bgr: np.ndarray) -> str:
    """Save an image for a pet. Returns the relative path."""
    fname = f"{uuid.uuid4().hex}.jpg"
    fpath = _pet_dir(pet_id) / fname
    cv2.imwrite(str(fpath), image_bgr)
    return f"pets/{pet_id}/{fname}"


def delete_pet_image_file(rel_path: str) -> None:
    fpath = cfg.STORAGE_DIR / rel_path
    if fpath.exists():
        fpath.unlink()


def save_pending_image(session_id: str, image_bgr: np.ndarray) -> str:
    """Save a pending image. Returns the relative path."""
    d = cfg.PENDING_DIR / session_id
    d.mkdir(parents=True, exist_ok=True)
    fname = f"{uuid.uuid4().hex}.jpg"
    fpath = d / fname
    cv2.imwrite(str(fpath), image_bgr)
    return f"pending/{session_id}/{fname}"


def delete_pending_session_files(session_id: str) -> None:
    d = cfg.PENDING_DIR / session_id
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)


def process_upload_image(image_bgr: np.ndarray) -> dict:
    """Process a single uploaded image for pet registration.

    Returns a dict with keys: accepted, reason, crop, embedding, phash.
    """
    # Detect cat
    dets = detect_cats(image_bgr)
    if not dets:
        return {"accepted": False, "reason": "no_cat"}
    if len(dets) > 1:
        return {"accepted": False, "reason": "multiple_cats"}

    det = dets[0]
    # Detect face region
    face = detect_cat_face(image_bgr, det.bbox)

    # Crop
    x1, y1, x2, y2 = face.bbox
    h, w = image_bgr.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    crop = image_bgr[y1:y2, x1:x2]

    # Quality check
    quality = assess_quality(crop)
    if not quality.passed:
        return {"accepted": False, "reason": quality.reason.value}

    # Embedding
    emb = extract_embedding(crop)
    phash = compute_phash(crop)

    return {
        "accepted": True,
        "reason": "ok",
        "crop": crop,
        "embedding": emb,
        "phash": phash,
        "face_bbox": face.bbox,
        "is_face": face.is_face,
        "detection_conf": det.confidence,
    }


def rebuild_embedding_store(pets_data: list[dict]) -> None:
    """Reload the in-memory embedding store from database records.

    pets_data: list of {"pet_id": int, "name": str, "embeddings": list[np.ndarray]}
    """
    for pet in pets_data:
        embedding_store.update_pet(
            pet["pet_id"],
            pet["name"],
            pet["embeddings"],
        )
    logger.info(
        "Embedding store rebuilt: %d pets, %d total embeddings",
        embedding_store.pet_count,
        sum(len(p["embeddings"]) for p in pets_data),
    )
