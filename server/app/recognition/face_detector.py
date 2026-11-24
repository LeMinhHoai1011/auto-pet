"""Cat face detection using OpenCV Haar cascade.

Falls back to using the full body crop if no face is found, since DINOv2
embeddings on the full body are still discriminative for individual cats.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from . import config as cfg

logger = logging.getLogger("recognition.face_detector")

_cascade = None


@dataclass
class FaceRegion:
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2 relative to original frame
    is_face: bool  # True = actual face detected, False = fallback to body crop


def _load_cascade() -> cv2.CascadeClassifier | None:
    global _cascade
    if _cascade is not None:
        return _cascade

    # Try OpenCV's built-in data directory first
    cascade_path = cfg.HAAR_CASCADE
    if not Path(cascade_path).exists():
        cv_data = Path(cv2.data.haarcascades)
        builtin = cv_data / cfg.HAAR_CASCADE
        if builtin.exists():
            cascade_path = str(builtin)
        else:
            logger.warning(
                "Haar cascade %s not found. Cat face detection disabled, "
                "using full body crops for embedding.",
                cfg.HAAR_CASCADE,
            )
            return None

    _cascade = cv2.CascadeClassifier(str(cascade_path))
    if _cascade.empty():
        logger.warning("Failed to load Haar cascade from %s", cascade_path)
        _cascade = None
        return None
    logger.info("Loaded cat face cascade from %s", cascade_path)
    return _cascade


def detect_cat_face(
    frame: np.ndarray,
    cat_bbox: tuple[int, int, int, int],
) -> FaceRegion:
    """Detect cat face within a cat bounding box.

    Returns the face region if found, otherwise the full body crop region.
    """
    x1, y1, x2, y2 = cat_bbox
    h, w = frame.shape[:2]
    # Clamp to frame bounds
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return FaceRegion(bbox=cat_bbox, is_face=False)

    cascade = _load_cascade()
    if cascade is None:
        return FaceRegion(bbox=cat_bbox, is_face=False)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=cfg.FACE_SCALE_FACTOR,
        minNeighbors=cfg.FACE_MIN_NEIGHBORS,
        minSize=(cfg.FACE_MIN_SIZE, cfg.FACE_MIN_SIZE),
    )

    if len(faces) == 0:
        return FaceRegion(bbox=cat_bbox, is_face=False)

    # Pick the largest face
    areas = [fw * fh for (_, _, fw, fh) in faces]
    best = int(np.argmax(areas))
    fx, fy, fw, fh = faces[best]

    # Expand face region by 20% for context
    pad_x = int(fw * 0.2)
    pad_y = int(fh * 0.2)
    face_x1 = max(0, fx - pad_x) + x1
    face_y1 = max(0, fy - pad_y) + y1
    face_x2 = min(w, fx + fw + pad_x + x1)
    face_y2 = min(h, fy + fh + pad_y + y1)

    return FaceRegion(
        bbox=(face_x1, face_y1, face_x2, face_y2),
        is_face=True,
    )
