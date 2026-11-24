"""Cat detection using YOLOv8/YOLO11 (ultralytics)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import numpy as np

from . import config as cfg

logger = logging.getLogger("recognition.detector")

_model = None


@dataclass
class Detection:
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    class_id: int
    class_name: str


def _load_model():
    global _model
    if _model is not None:
        return _model
    from ultralytics import YOLO

    device = cfg.resolve_device(cfg.YOLO_DEVICE)
    logger.info("Loading YOLO model %s on %s", cfg.YOLO_MODEL, device)
    t0 = time.time()
    _model = YOLO(cfg.YOLO_MODEL)
    _model.to(device)
    logger.info("YOLO loaded in %.1fs", time.time() - t0)
    return _model


def detect_cats(frame: np.ndarray) -> list[Detection]:
    """Run YOLO on a BGR frame, return cat detections only."""
    model = _load_model()
    results = model.predict(
        frame,
        conf=cfg.YOLO_CONF_THRESHOLD,
        classes=cfg.YOLO_PET_CLASS_IDS,
        verbose=False,
    )
    detections: list[Detection] = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            name = "cat" if cls_id == cfg.YOLO_CAT_CLASS_ID else "dog"
            detections.append(Detection(
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                confidence=conf,
                class_id=cls_id,
                class_name=name,
            ))
    return detections


def detect_all(frame: np.ndarray) -> list[Detection]:
    """Run YOLO on a BGR frame, return all detections (for debugging)."""
    model = _load_model()
    results = model.predict(frame, conf=0.3, verbose=False)
    detections: list[Detection] = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            name = model.names.get(cls_id, str(cls_id))
            detections.append(Detection(
                bbox=(int(x1), int(y1), int(x2), int(y2)),
                confidence=conf,
                class_id=cls_id,
                class_name=name,
            ))
    return detections


def is_in_roi(det: Detection, frame_w: int, frame_h: int) -> bool:
    """Check if the center of a detection is inside the configured ROI."""
    if not cfg.ROI_ENABLED:
        return True
    cx = (det.bbox[0] + det.bbox[2]) / 2 / frame_w
    cy = (det.bbox[1] + det.bbox[3]) / 2 / frame_h
    return cfg.ROI_X1 <= cx <= cfg.ROI_X2 and cfg.ROI_Y1 <= cy <= cfg.ROI_Y2


def unload_model():
    global _model
    if _model is not None:
        del _model
        _model = None
        logger.info("YOLO model unloaded")
