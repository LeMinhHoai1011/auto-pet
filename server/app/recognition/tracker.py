"""Simple IoU-based multi-object tracker for cats.

Replaces ByteTrack (removed in supervision>=0.26) with a lightweight
IoU tracker that assigns stable IDs across frames.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from . import config as cfg
from .detector import Detection

logger = logging.getLogger("recognition.tracker")


@dataclass
class TrackedCat:
    tracker_id: int
    bbox: tuple[int, int, int, int]
    confidence: float


@dataclass
class _Track:
    tid: int
    bbox: np.ndarray
    confidence: float
    lost: int = 0


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


class CatTracker:
    def __init__(self):
        self._tracks: list[_Track] = []
        self._next_id: int = 1
        self._match_thresh: float = cfg.MATCH_THRESH
        self._lost_buffer: int = cfg.TRACK_BUFFER
        logger.info("IoU tracker initialized (match=%.2f, buffer=%d)",
                     self._match_thresh, self._lost_buffer)

    def update(self, detections: list[Detection], frame: np.ndarray) -> list[TrackedCat]:
        det_boxes = [np.array(d.bbox, dtype=np.float32) for d in detections]
        det_confs = [d.confidence for d in detections]

        matched_t: set[int] = set()
        matched_d: set[int] = set()
        results: list[TrackedCat] = []

        for di, dbox in enumerate(det_boxes):
            best_iou = 0.0
            best_ti = -1
            for ti, track in enumerate(self._tracks):
                if ti in matched_t:
                    continue
                score = _iou(dbox, track.bbox)
                if score > best_iou:
                    best_iou = score
                    best_ti = ti
            if best_iou >= self._match_thresh and best_ti >= 0:
                self._tracks[best_ti].bbox = dbox
                self._tracks[best_ti].confidence = det_confs[di]
                self._tracks[best_ti].lost = 0
                matched_t.add(best_ti)
                matched_d.add(di)

        for di, dbox in enumerate(det_boxes):
            if di in matched_d:
                continue
            t = _Track(tid=self._next_id, bbox=dbox, confidence=det_confs[di])
            self._next_id += 1
            self._tracks.append(t)

        alive: list[_Track] = []
        for ti, track in enumerate(self._tracks):
            if ti not in matched_t and ti < len(self._tracks):
                track.lost += 1
            if track.lost <= self._lost_buffer:
                alive.append(track)
        self._tracks = alive

        for track in self._tracks:
            if track.lost == 0:
                b = track.bbox.astype(int)
                results.append(TrackedCat(
                    tracker_id=track.tid,
                    bbox=(int(b[0]), int(b[1]), int(b[2]), int(b[3])),
                    confidence=track.confidence,
                ))
        return results

    def reset(self):
        self._tracks.clear()
        self._next_id = 1
