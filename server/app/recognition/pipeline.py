"""Main recognition pipeline — orchestrates all components.

Runs in shadow/observation mode during Phase 2: observes and logs but
does NOT trigger feeding commands.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

import cv2
import numpy as np

from . import config as cfg
from .camera import CameraManager, CameraState, camera_manager
from .collector import SessionCollector, AppearanceSession
from .detector import detect_cats, is_in_roi, Detection
from .embedding import extract_embedding, load_model as load_embedding_model
from .face_detector import detect_cat_face
from .matcher import MatchResult, RecognitionStatus, embedding_store
from .quality_filter import assess_quality
from .tracker import CatTracker, TrackedCat

logger = logging.getLogger("recognition.pipeline")


class PipelineMode(str, Enum):
    OFF = "off"
    OBSERVE = "observe"      # Shadow mode: detect + identify, no feeding
    ACTIVE = "active"        # Full mode: could trigger feeding (Phase 3+)
    REGISTER = "register"    # Registration mode: collect images for a specific cat


@dataclass
class CatObservation:
    """Current observation state for a tracked cat."""
    tracker_id: int
    bbox: tuple[int, int, int, int]
    detection_conf: float
    match_result: MatchResult | None = None
    frames_seen: int = 0
    confirmed_identity: int | None = None
    confirmed_name: str | None = None
    identity_votes: dict[int, int] = field(default_factory=dict)
    vote_total: int = 0


@dataclass
class PipelineState:
    """Current snapshot of pipeline state for the dashboard."""
    mode: PipelineMode = PipelineMode.OFF
    camera_state: str = "disconnected"
    fps: float = 0.0
    ai_fps: float = 0.0
    process_time_ms: float = 0.0
    cats_detected: int = 0
    observations: list[CatObservation] = field(default_factory=list)
    active_sessions: int = 0
    total_collected: int = 0
    device_info: str = "cpu"
    error: str = ""


class RecognitionPipeline:
    """Main pipeline coordinating detection, tracking, recognition, collection."""

    def __init__(self):
        self._mode = PipelineMode.OFF
        self._tracker = CatTracker()
        self._collector = SessionCollector()
        self._observations: dict[int, CatObservation] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._ai_fps: float = 0.0
        self._process_time_ms: float = 0.0
        self._total_collected: int = 0
        self._last_ai_time: float = 0.0
        self._frame_callbacks: list = []
        self._fed_tracker_ids: set[int] = set()
        self._on_pet_confirmed_cb = None

        # Registration state
        self._registering_pet_id: int | None = None
        self._registration_session: AppearanceSession | None = None

    def set_on_pet_confirmed(self, callback) -> None:
        """Set callback(pet_id, pet_name, tracker_id) called when pet is confirmed."""
        self._on_pet_confirmed_cb = callback

    @property
    def mode(self) -> PipelineMode:
        return self._mode

    def start(self, mode: PipelineMode = PipelineMode.OBSERVE) -> None:
        if self._running:
            self.stop()

        self._mode = mode
        self._running = True

        # Pre-load models in background
        threading.Thread(target=self._preload_models, daemon=True).start()

        # Start camera
        camera_manager.start(on_frame=self._on_frame)
        logger.info("Pipeline started in %s mode", mode.value)

    def stop(self) -> None:
        self._running = False
        camera_manager.stop()
        self._mode = PipelineMode.OFF
        self._observations.clear()
        self._collector.reset()
        self._tracker.reset()
        self._fed_tracker_ids.clear()
        logger.info("Pipeline stopped")

    def start_registration(self, pet_id: int | None = None) -> None:
        """Switch to registration mode for a specific pet."""
        self._registering_pet_id = pet_id
        self._mode = PipelineMode.REGISTER
        self._collector.reset()
        logger.info("Registration mode started for pet_id=%s", pet_id)

    def stop_registration(self) -> AppearanceSession | None:
        """Stop registration and return the collected session."""
        session = self._registration_session
        self._registering_pet_id = None
        self._registration_session = None
        self._mode = PipelineMode.OBSERVE
        logger.info("Registration mode stopped")
        return session

    def get_state(self) -> PipelineState:
        with self._lock:
            return PipelineState(
                mode=self._mode,
                camera_state=camera_manager.state.value,
                fps=camera_manager.fps,
                ai_fps=self._ai_fps,
                process_time_ms=self._process_time_ms,
                cats_detected=len(self._observations),
                observations=list(self._observations.values()),
                active_sessions=len(self._collector.get_active_sessions()),
                total_collected=self._total_collected,
                device_info=cfg.resolve_device(cfg.EMBEDDING_DEVICE),
                error=camera_manager.error,
            )

    def add_frame_callback(self, cb) -> None:
        self._frame_callbacks.append(cb)

    def remove_frame_callback(self, cb) -> None:
        if cb in self._frame_callbacks:
            self._frame_callbacks.remove(cb)

    def _preload_models(self) -> None:
        try:
            from .detector import _load_model as load_yolo
            load_yolo()
            load_embedding_model()
            logger.info("All models pre-loaded")
        except Exception:
            logger.exception("Model pre-loading failed")

    def _on_frame(self, frame: np.ndarray, timestamp: float) -> None:
        """Called by camera manager for each captured frame."""
        if not self._running or self._mode == PipelineMode.OFF:
            return

        # Rate limit AI processing
        ai_interval = 1.0 / cfg.AI_FPS_LIMIT if cfg.AI_FPS_LIMIT > 0 else 0
        if timestamp - self._last_ai_time < ai_interval:
            return
        self._last_ai_time = timestamp

        try:
            t0 = time.time()
            self._process_frame(frame, timestamp)
            self._process_time_ms = (time.time() - t0) * 1000
            self._ai_fps = 1000.0 / max(self._process_time_ms, 1)
        except Exception:
            logger.exception("Pipeline frame processing error")

        # Notify frame callbacks (for streaming)
        for cb in self._frame_callbacks:
            try:
                cb(frame, self._observations)
            except Exception:
                pass

    def _process_frame(self, frame: np.ndarray, timestamp: float) -> None:
        h, w = frame.shape[:2]

        # 1. Detect cats
        detections = detect_cats(frame)

        # 2. Filter by ROI
        roi_dets = [d for d in detections if is_in_roi(d, w, h)]

        # 3. Track
        tracked = self._tracker.update(roi_dets, frame)

        # 4. Close sessions for cats that left
        active_tids = {t.tracker_id for t in tracked}
        for tid in list(self._observations.keys()):
            if tid not in active_tids:
                self._collector.close_session(tid)
                with self._lock:
                    self._observations.pop(tid, None)

        # Cleanup stale sessions
        self._collector.cleanup_stale(max_age_sec=10.0)

        # 5. Process each tracked cat
        for cat in tracked:
            obs = self._observations.get(cat.tracker_id)
            if obs is None:
                obs = CatObservation(
                    tracker_id=cat.tracker_id,
                    bbox=cat.bbox,
                    detection_conf=cat.confidence,
                )
                with self._lock:
                    self._observations[cat.tracker_id] = obs
            else:
                obs.bbox = cat.bbox
                obs.detection_conf = cat.confidence

            obs.frames_seen += 1

            # 5a. Face detection + crop
            face = detect_cat_face(frame, cat.bbox)
            x1, y1, x2, y2 = face.bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            # 5b. Quality check
            quality = assess_quality(crop)

            # 5c. Identity matching (only if quality is OK and we have registered pets)
            if quality.passed and embedding_store.pet_count > 0:
                try:
                    emb = extract_embedding(crop)
                    match = embedding_store.match(emb)
                    obs.match_result = match

                    # Vote-based confirmation
                    if match.status == RecognitionStatus.KNOWN and match.pet_id is not None:
                        obs.identity_votes[match.pet_id] = obs.identity_votes.get(match.pet_id, 0) + 1
                        obs.vote_total += 1

                        if obs.identity_votes[match.pet_id] >= cfg.CONFIRMATION_FRAMES:
                            was_unconfirmed = obs.confirmed_identity is None
                            obs.confirmed_identity = match.pet_id
                            obs.confirmed_name = match.pet_name

                            if was_unconfirmed and cat.tracker_id not in self._fed_tracker_ids:
                                self._fed_tracker_ids.add(cat.tracker_id)
                                if self._on_pet_confirmed_cb and self._mode == PipelineMode.ACTIVE:
                                    try:
                                        self._on_pet_confirmed_cb(match.pet_id, match.pet_name, cat.tracker_id)
                                    except Exception:
                                        logger.exception("Auto-feed callback failed")
                except Exception:
                    logger.exception("Embedding extraction/matching failed")
                    obs.match_result = MatchResult(status=RecognitionStatus.MODEL_ERROR)
            elif not quality.passed:
                obs.match_result = MatchResult(status=RecognitionStatus.LOW_QUALITY)

            # 5d. Collect images for sessions
            session = self._collector.on_cat_detected(
                tracker_id=cat.tracker_id,
                frame=frame,
                crop=crop,
                timestamp=timestamp,
            )
            if session is not None:
                self._total_collected += 1
                if self._mode == PipelineMode.REGISTER:
                    self._registration_session = session


# Singleton
pipeline = RecognitionPipeline()
