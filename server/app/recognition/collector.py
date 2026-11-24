"""Image collector for recognition sessions.

Manages automatic image collection when cats appear in the feeding area.
Groups images by appearance session and tracking ID.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

import numpy as np

from . import config as cfg
from .quality_filter import assess_quality, compute_phash, is_duplicate

logger = logging.getLogger("recognition.collector")


@dataclass
class CollectedImage:
    image: np.ndarray
    phash: int
    timestamp: float
    tracker_id: int
    quality_score: float


@dataclass
class AppearanceSession:
    session_id: str
    tracker_id: int
    started_at: float
    last_seen_at: float
    images: list[CollectedImage] = field(default_factory=list)
    confirmed: bool = False  # Stable detection confirmed
    closed: bool = False

    @property
    def duration(self) -> float:
        return self.last_seen_at - self.started_at

    @property
    def image_count(self) -> int:
        return len(self.images)


class SessionCollector:
    """Manages appearance sessions and image collection."""

    def __init__(self):
        self._sessions: dict[int, AppearanceSession] = {}  # tracker_id -> session
        self._all_sessions: dict[str, AppearanceSession] = {}  # session_id -> session
        self._last_capture: dict[int, float] = {}  # tracker_id -> last capture time

    def on_cat_detected(
        self,
        tracker_id: int,
        frame: np.ndarray,
        crop: np.ndarray,
        timestamp: float | None = None,
    ) -> AppearanceSession | None:
        """Called each frame when a tracked cat is detected.

        Returns the session if an image was collected, None otherwise.
        """
        now = timestamp or time.time()

        # Get or create session
        session = self._sessions.get(tracker_id)
        if session is None:
            session = AppearanceSession(
                session_id=uuid.uuid4().hex,
                tracker_id=tracker_id,
                started_at=now,
                last_seen_at=now,
            )
            self._sessions[tracker_id] = session
            self._all_sessions[session.session_id] = session
            logger.debug("New session %s for tracker %d", session.session_id, tracker_id)

        session.last_seen_at = now

        # Check if session should be confirmed (stable presence)
        if not session.confirmed:
            if session.duration >= cfg.SESSION_CONFIRM_SEC:
                session.confirmed = True
                logger.info("Session %s confirmed (%.1fs)", session.session_id, session.duration)
            else:
                return None

        # Rate limit captures
        last_cap = self._last_capture.get(tracker_id, 0)
        if now - last_cap < cfg.CAPTURE_INTERVAL_SEC:
            return None

        # Check session limits
        if session.image_count >= cfg.MAX_IMAGES_PER_SESSION:
            return None
        if session.duration > cfg.SESSION_DURATION_SEC:
            return None

        # Quality check
        quality = assess_quality(crop)
        if not quality.passed:
            return None

        # Duplicate check against session images
        phash = compute_phash(crop)
        for existing in session.images:
            if is_duplicate(phash, existing.phash):
                return None

        # Collect!
        collected = CollectedImage(
            image=crop.copy(),
            phash=phash,
            timestamp=now,
            tracker_id=tracker_id,
            quality_score=quality.blur_score,
        )
        session.images.append(collected)
        self._last_capture[tracker_id] = now
        logger.debug(
            "Session %s: collected image %d (quality=%.1f)",
            session.session_id, session.image_count, quality.blur_score,
        )
        return session

    def close_session(self, tracker_id: int) -> AppearanceSession | None:
        """Close a session when a cat leaves the frame."""
        session = self._sessions.pop(tracker_id, None)
        self._last_capture.pop(tracker_id, None)
        if session is not None:
            session.closed = True
            logger.info(
                "Session %s closed: %d images, %.1fs",
                session.session_id, session.image_count, session.duration,
            )
        return session

    def get_active_sessions(self) -> list[AppearanceSession]:
        return [s for s in self._sessions.values() if not s.closed]

    def get_session(self, session_id: str) -> AppearanceSession | None:
        return self._all_sessions.get(session_id)

    def cleanup_stale(self, max_age_sec: float = 60.0) -> list[AppearanceSession]:
        """Close sessions that haven't been updated recently."""
        now = time.time()
        stale: list[AppearanceSession] = []
        for tid in list(self._sessions.keys()):
            s = self._sessions[tid]
            if now - s.last_seen_at > max_age_sec:
                closed = self.close_session(tid)
                if closed:
                    stale.append(closed)
        return stale

    def reset(self) -> None:
        self._sessions.clear()
        self._all_sessions.clear()
        self._last_capture.clear()
