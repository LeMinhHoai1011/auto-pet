"""Recognition package — AI-powered pet detection and identification.

Probes torch availability once at import time so that endpoints can
fail fast with a clear 503 instead of a cryptic OS error.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("recognition")

torch_available: bool = True
torch_error: str = ""

try:
    import torch  # noqa: F401
except OSError as exc:
    torch_available = False
    if getattr(exc, "winerror", None) == 4551:
        torch_error = (
            "Windows Application Control đã chặn PyTorch. "
            "Tắt Smart App Control trong Settings → Privacy & Security → Windows Security "
            "→ App & Browser Control → Smart App Control, rồi khởi động lại server."
        )
    else:
        torch_error = f"Không thể nạp PyTorch: {exc}"
    logger.warning("PyTorch unavailable: %s", torch_error)
except ImportError as exc:
    torch_available = False
    torch_error = f"PyTorch chưa cài đặt: {exc}"
    logger.warning("PyTorch not installed: %s", torch_error)
