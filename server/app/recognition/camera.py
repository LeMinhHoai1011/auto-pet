"""Camera manager supporting multiple sources.

Sources: webcam (int), ESP32-CAM URL, video file, image file.
Runs capture in a background thread to avoid blocking the event loop.
"""

from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Callable

import cv2
import numpy as np

from . import config as cfg

logger = logging.getLogger("recognition.camera")


class CameraState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class CameraManager:
    def __init__(self):
        self._cap: cv2.VideoCapture | None = None
        self._source: str | int = 0
        self._state = CameraState.DISCONNECTED
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._frame_time: float = 0
        self._frame_count: int = 0
        self._fps: float = 0.0
        self._thread: threading.Thread | None = None
        self._running = False
        self._error_msg: str = ""
        self._reconnect_count: int = 0
        self._on_frame: Callable[[np.ndarray, float], None] | None = None

    @property
    def state(self) -> CameraState:
        return self._state

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def error(self) -> str:
        return self._error_msg

    @property
    def source(self) -> str | int:
        return self._source

    def get_frame(self) -> tuple[np.ndarray | None, float]:
        with self._lock:
            if self._frame is not None:
                return self._frame.copy(), self._frame_time
            return None, 0

    def start(
        self,
        source: str | int | None = None,
        on_frame: Callable[[np.ndarray, float], None] | None = None,
    ) -> bool:
        if self._running:
            self.stop()

        self._source = source if source is not None else _parse_source(cfg.CAMERA_SOURCE)
        self._on_frame = on_frame
        self._running = True
        self._error_msg = ""
        self._state = CameraState.CONNECTING
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info("Camera started: source=%s", self._source)
        return True

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        with self._lock:
            if self._cap is not None:
                self._cap.release()
                self._cap = None
            self._frame = None
        self._state = CameraState.DISCONNECTED
        self._on_frame = None
        logger.info("Camera stopped")

    def _capture_loop(self) -> None:
        fps_interval = 1.0 / cfg.CAMERA_FPS_LIMIT if cfg.CAMERA_FPS_LIMIT > 0 else 0
        fps_counter = 0
        fps_timer = time.time()

        while self._running:
            # Connect if needed
            if self._cap is None or not self._cap.isOpened():
                if not self._connect():
                    time.sleep(2.0)
                    continue

            ret, frame = self._cap.read()
            if not ret:
                logger.warning("Camera read failed, reconnecting...")
                self._state = CameraState.ERROR
                self._error_msg = "Read failed"
                with self._lock:
                    if self._cap is not None:
                        self._cap.release()
                        self._cap = None
                time.sleep(1.0)
                continue

            # Resize if needed
            h, w = frame.shape[:2]
            if w > cfg.FRAME_WIDTH:
                scale = cfg.FRAME_WIDTH / w
                frame = cv2.resize(frame, None, fx=scale, fy=scale)

            now = time.time()
            with self._lock:
                self._frame = frame
                self._frame_time = now
                self._frame_count += 1

            # FPS counting
            fps_counter += 1
            elapsed = now - fps_timer
            if elapsed >= 1.0:
                self._fps = fps_counter / elapsed
                fps_counter = 0
                fps_timer = now

            # Callback
            if self._on_frame is not None:
                try:
                    self._on_frame(frame, now)
                except Exception:
                    logger.exception("on_frame callback error")

            # Rate limiting
            if fps_interval > 0:
                time.sleep(fps_interval)

    def _connect(self) -> bool:
        self._state = CameraState.CONNECTING
        try:
            source = self._source
            if isinstance(source, str) and source.startswith(("http://", "https://", "rtsp://")):
                cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            else:
                cap = cv2.VideoCapture(int(source) if isinstance(source, str) and source.isdigit() else source)

            if not cap.isOpened():
                self._state = CameraState.ERROR
                self._error_msg = f"Cannot open {source}"
                logger.error("Cannot open camera: %s", source)
                return False

            with self._lock:
                self._cap = cap
            self._state = CameraState.CONNECTED
            self._error_msg = ""
            self._reconnect_count += 1
            logger.info("Camera connected: %s", source)
            return True
        except Exception as e:
            self._state = CameraState.ERROR
            self._error_msg = str(e)
            logger.exception("Camera connect error")
            return False

    def get_status(self) -> dict:
        return {
            "state": self._state.value,
            "source": str(self._source),
            "fps": round(self._fps, 1),
            "frame_count": self._frame_count,
            "error": self._error_msg,
        }


def _parse_source(source_str: str) -> str | int:
    """Parse camera source from config string."""
    if source_str.isdigit():
        return int(source_str)
    return source_str


# Singleton
camera_manager = CameraManager()
