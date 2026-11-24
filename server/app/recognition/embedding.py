"""Embedding extraction using DINOv2 ViT-S/14."""

from __future__ import annotations

import logging
import time

import cv2
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image

from . import config as cfg

logger = logging.getLogger("recognition.embedding")

_model = None
_device: str = "cpu"
_transform = None


def _get_transform():
    global _transform
    if _transform is not None:
        return _transform
    _transform = T.Compose([
        T.Resize(256, interpolation=T.InterpolationMode.BICUBIC),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])
    return _transform


def load_model() -> None:
    global _model, _device
    if _model is not None:
        return
    _device = cfg.resolve_device(cfg.EMBEDDING_DEVICE)
    logger.info("Loading %s on %s", cfg.EMBEDDING_MODEL, _device)
    t0 = time.time()
    _model = torch.hub.load(
        "facebookresearch/dinov2",
        cfg.EMBEDDING_MODEL,
        pretrained=True,
    )
    _model.to(_device)
    _model.eval()
    logger.info("DINOv2 loaded in %.1fs (device=%s)", time.time() - t0, _device)


def extract_embedding(crop_bgr: np.ndarray) -> np.ndarray:
    """Extract a normalized embedding vector from a BGR crop.

    Returns a 1D numpy array of shape (EMBEDDING_DIM,).
    """
    load_model()
    # Convert BGR to RGB PIL image
    rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    transform = _get_transform()
    tensor = transform(pil_img).unsqueeze(0).to(_device)

    with torch.no_grad():
        emb = _model(tensor).squeeze(0)
        emb = torch.nn.functional.normalize(emb, dim=0)

    return emb.cpu().numpy().astype(np.float32)


def extract_embeddings_batch(crops_bgr: list[np.ndarray]) -> list[np.ndarray]:
    """Extract embeddings for multiple crops in a single batch."""
    if not crops_bgr:
        return []
    load_model()
    transform = _get_transform()

    tensors = []
    for crop in crops_bgr:
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        tensors.append(transform(pil_img))

    results: list[np.ndarray] = []
    for i in range(0, len(tensors), cfg.EMBEDDING_BATCH_SIZE):
        batch = torch.stack(tensors[i : i + cfg.EMBEDDING_BATCH_SIZE]).to(_device)
        with torch.no_grad():
            embs = _model(batch)
            embs = torch.nn.functional.normalize(embs, dim=1)
        for emb in embs:
            results.append(emb.cpu().numpy().astype(np.float32))
    return results


def get_device() -> str:
    return _device


def get_model_version() -> str:
    return cfg.EMBEDDING_MODEL_VERSION


def unload_model() -> None:
    global _model
    if _model is not None:
        del _model
        _model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("DINOv2 model unloaded")
