"""Image quality assessment for recognition pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

from . import config as cfg

logger = logging.getLogger("recognition.quality")


class RejectReason(str, Enum):
    OK = "ok"
    TOO_BLURRY = "too_blurry"
    TOO_DARK = "too_dark"
    TOO_BRIGHT = "too_bright"
    TOO_SMALL = "too_small"
    NO_CAT = "no_cat"
    OCCLUDED = "occluded"


@dataclass
class QualityResult:
    passed: bool
    reason: RejectReason
    blur_score: float
    brightness: float
    crop_size: tuple[int, int]


def assess_quality(
    crop: np.ndarray,
    blur_threshold: float | None = None,
) -> QualityResult:
    """Assess whether a crop is good enough for embedding extraction."""
    if crop.size == 0:
        return QualityResult(False, RejectReason.TOO_SMALL, 0, 0, (0, 0))

    h, w = crop.shape[:2]
    crop_size = (w, h)

    if w < cfg.MIN_CROP_SIZE or h < cfg.MIN_CROP_SIZE:
        return QualityResult(False, RejectReason.TOO_SMALL, 0, 0, crop_size)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop

    # Blur detection via Laplacian variance
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    threshold = blur_threshold if blur_threshold is not None else cfg.BLUR_THRESHOLD

    # Brightness check
    brightness = float(gray.mean())

    if blur_score < threshold:
        return QualityResult(False, RejectReason.TOO_BLURRY, blur_score, brightness, crop_size)

    if brightness < cfg.MIN_BRIGHTNESS:
        return QualityResult(False, RejectReason.TOO_DARK, blur_score, brightness, crop_size)

    if brightness > cfg.MAX_BRIGHTNESS:
        return QualityResult(False, RejectReason.TOO_BRIGHT, blur_score, brightness, crop_size)

    return QualityResult(True, RejectReason.OK, blur_score, brightness, crop_size)


def compute_phash(image: np.ndarray, hash_size: int = 8) -> int:
    """Compute perceptual hash for duplicate detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    return int.from_bytes(np.packbits(diff.flatten()).tobytes()[:8], "big")


def hamming_distance(h1: int, h2: int) -> int:
    return bin(h1 ^ h2).count("1")


def is_duplicate(hash1: int, hash2: int, threshold: int = 8) -> bool:
    return hamming_distance(hash1, hash2) < threshold
