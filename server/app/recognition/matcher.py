"""Identity matching using cosine similarity against registered embeddings."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from enum import Enum

import numpy as np

from . import config as cfg

logger = logging.getLogger("recognition.matcher")


class RecognitionStatus(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    UNCERTAIN = "UNCERTAIN"
    MULTIPLE_CATS = "MULTIPLE_CATS"
    LOW_QUALITY = "LOW_QUALITY"
    NO_CAT = "NO_CAT"
    CAMERA_OFFLINE = "CAMERA_OFFLINE"
    MODEL_ERROR = "MODEL_ERROR"


@dataclass
class MatchResult:
    status: RecognitionStatus
    pet_id: int | None = None
    pet_name: str | None = None
    similarity: float = 0.0
    second_similarity: float = 0.0
    margin: float = 0.0
    all_scores: dict[int, float] | None = None


class EmbeddingStore:
    """In-memory cache of registered pet embeddings for fast matching."""

    def __init__(self):
        self._lock = threading.Lock()
        self._pet_ids: list[int] = []
        self._pet_names: dict[int, str] = {}
        self._embeddings: dict[int, np.ndarray] = {}  # pet_id -> (N, dim) array
        self._centroids: dict[int, np.ndarray] = {}   # pet_id -> mean embedding

    def update_pet(self, pet_id: int, name: str, embeddings: list[np.ndarray]) -> None:
        with self._lock:
            if not embeddings:
                self._embeddings.pop(pet_id, None)
                self._centroids.pop(pet_id, None)
                if pet_id in self._pet_ids:
                    self._pet_ids.remove(pet_id)
                self._pet_names.pop(pet_id, None)
                return
            arr = np.stack(embeddings)
            centroid = arr.mean(axis=0)
            centroid = centroid / (np.linalg.norm(centroid) + 1e-8)
            self._embeddings[pet_id] = arr
            self._centroids[pet_id] = centroid
            self._pet_names[pet_id] = name
            if pet_id not in self._pet_ids:
                self._pet_ids.append(pet_id)

    def remove_pet(self, pet_id: int) -> None:
        with self._lock:
            self._embeddings.pop(pet_id, None)
            self._centroids.pop(pet_id, None)
            self._pet_names.pop(pet_id, None)
            if pet_id in self._pet_ids:
                self._pet_ids.remove(pet_id)

    def match(self, query: np.ndarray) -> MatchResult:
        with self._lock:
            if not self._centroids:
                return MatchResult(status=RecognitionStatus.UNKNOWN)

            scores: dict[int, float] = {}
            for pid, centroid in self._centroids.items():
                sim = float(np.dot(query, centroid))
                scores[pid] = sim

            sorted_pets = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_pid, best_sim = sorted_pets[0]
            second_sim = sorted_pets[1][1] if len(sorted_pets) > 1 else 0.0
            margin = best_sim - second_sim

            if best_sim >= cfg.MATCH_THRESHOLD and margin >= cfg.MIN_MARGIN:
                return MatchResult(
                    status=RecognitionStatus.KNOWN,
                    pet_id=best_pid,
                    pet_name=self._pet_names.get(best_pid),
                    similarity=best_sim,
                    second_similarity=second_sim,
                    margin=margin,
                    all_scores=scores,
                )
            elif best_sim >= cfg.UNCERTAIN_THRESHOLD:
                return MatchResult(
                    status=RecognitionStatus.UNCERTAIN,
                    pet_id=best_pid,
                    pet_name=self._pet_names.get(best_pid),
                    similarity=best_sim,
                    second_similarity=second_sim,
                    margin=margin,
                    all_scores=scores,
                )
            else:
                return MatchResult(
                    status=RecognitionStatus.UNKNOWN,
                    similarity=best_sim,
                    second_similarity=second_sim,
                    margin=margin,
                    all_scores=scores,
                )

    @property
    def pet_count(self) -> int:
        with self._lock:
            return len(self._pet_ids)

    @property
    def pet_ids(self) -> list[int]:
        with self._lock:
            return list(self._pet_ids)


# Singleton store
embedding_store = EmbeddingStore()
