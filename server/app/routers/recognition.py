"""Recognition API — pipeline control, sessions, logs, streaming."""

from __future__ import annotations

import asyncio
import io
import json
import logging
import time
from datetime import datetime

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import (
    Pet, PetEmbedding, RecognitionSession, RecognitionSample, RecognitionLog,
)
from ..schemas import (
    RecognitionSessionOut, RecognitionLogOut, SessionAssign, PipelineStatusOut,
)

logger = logging.getLogger("api.recognition")

router = APIRouter(prefix="/api/recognition", tags=["recognition"])


@router.get("/status", response_model=PipelineStatusOut)
async def get_pipeline_status():
    from ..recognition.pipeline import pipeline
    state = pipeline.get_state()
    return PipelineStatusOut(
        mode=state.mode.value,
        camera_state=state.camera_state,
        fps=state.fps,
        ai_fps=state.ai_fps,
        process_time_ms=state.process_time_ms,
        cats_detected=state.cats_detected,
        active_sessions=state.active_sessions,
        total_collected=state.total_collected,
        device_info=state.device_info,
        error=state.error,
    )


@router.post("/start")
async def start_pipeline(mode: str = Query("observe")):
    from ..recognition.pipeline import pipeline, PipelineMode
    try:
        pm = PipelineMode(mode)
    except ValueError:
        raise HTTPException(400, f"Invalid mode: {mode}")
    if pm == PipelineMode.ACTIVE:
        return {"ok": False, "error": "Active mode not available in Phase 2 (shadow mode only)"}
    pipeline.start(pm)
    return {"ok": True, "mode": pm.value}


@router.post("/stop")
async def stop_pipeline():
    from ..recognition.pipeline import pipeline
    pipeline.stop()
    return {"ok": True}


@router.get("/stream")
async def video_stream():
    """MJPEG video stream with bounding boxes and recognition overlays."""
    from ..recognition.pipeline import pipeline

    async def generate():
        while True:
            from ..recognition.camera import camera_manager
            frame, ts = camera_manager.get_frame()
            if frame is None:
                await asyncio.sleep(0.1)
                continue

            # Draw overlays
            annotated = frame.copy()
            state = pipeline.get_state()
            for obs in state.observations:
                x1, y1, x2, y2 = obs.bbox
                # Color based on recognition status
                if obs.match_result is None:
                    color = (200, 200, 200)  # gray
                    label = f"Cat #{obs.tracker_id}"
                elif obs.confirmed_name:
                    color = (0, 220, 0)  # green
                    label = f"{obs.confirmed_name} ({obs.match_result.similarity:.0%})"
                elif obs.match_result.status.value == "UNKNOWN":
                    color = (0, 165, 255)  # orange
                    label = f"Unknown #{obs.tracker_id}"
                elif obs.match_result.status.value == "UNCERTAIN":
                    color = (0, 255, 255)  # yellow
                    name = obs.match_result.pet_name or "?"
                    label = f"{name}? ({obs.match_result.similarity:.0%})"
                else:
                    color = (200, 200, 200)
                    label = f"#{obs.tracker_id} [{obs.match_result.status.value}]"

                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
                )

            # Draw ROI if enabled
            from ..recognition import config as cfg
            if cfg.ROI_ENABLED:
                h, w = annotated.shape[:2]
                rx1, ry1 = int(cfg.ROI_X1 * w), int(cfg.ROI_Y1 * h)
                rx2, ry2 = int(cfg.ROI_X2 * w), int(cfg.ROI_Y2 * h)
                cv2.rectangle(annotated, (rx1, ry1), (rx2, ry2), (255, 255, 0), 1)

            # Encode
            _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 70])
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buf.tobytes()
                + b"\r\n"
            )
            await asyncio.sleep(1.0 / cfg.CAMERA_FPS_LIMIT)

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/identify")
async def identify_from_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Identify a cat from a single uploaded image."""
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Cannot decode image")

    from ..recognition.detector import detect_cats, detect_all
    from ..recognition.face_detector import detect_cat_face
    from ..recognition.quality_filter import assess_quality
    from ..recognition.embedding import extract_embedding
    from ..recognition.matcher import embedding_store

    img_h, img_w = img.shape[:2]

    dets = detect_cats(img)
    if not dets:
        all_dets = detect_all(img)
        debug_classes = [
            {"class": d.class_name, "confidence": round(d.confidence, 4)}
            for d in all_dets[:5]
        ]
        return {
            "status": "NO_PET",
            "detections": 0,
            "image_size": [img_w, img_h],
            "other_objects": debug_classes,
            "message": "Không tìm thấy chó/mèo trong ảnh. Hãy upload ảnh rõ nét có chó hoặc mèo.",
        }

    has_registered = embedding_store.pet_count > 0
    results = []
    for det in dets:
        face = detect_cat_face(img, det.bbox)
        x1, y1, x2, y2 = face.bbox
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)
        crop = img[y1:y2, x1:x2]

        quality = assess_quality(crop)

        if not has_registered:
            results.append({
                "bbox": det.bbox,
                "class": det.class_name,
                "status": "NO_REGISTERED_PETS",
                "detection_confidence": round(det.confidence, 4),
                "quality": quality.reason.value,
                "message": "Phát hiện thú cưng nhưng chưa có pet nào đăng ký. Thêm pet và upload ít nhất 5 ảnh trước.",
            })
            continue

        if not quality.passed and quality.reason.value == "too_small":
            results.append({
                "bbox": det.bbox,
                "class": det.class_name,
                "status": "LOW_QUALITY",
                "reason": quality.reason.value,
                "crop_size": list(quality.crop_size),
                "detection_confidence": round(det.confidence, 4),
            })
            continue

        emb = extract_embedding(crop)
        match = embedding_store.match(emb)

        results.append({
            "bbox": det.bbox,
            "class": det.class_name,
            "status": match.status.value,
            "pet_id": match.pet_id,
            "pet_name": match.pet_name,
            "similarity": round(match.similarity, 4),
            "margin": round(match.margin, 4),
            "detection_confidence": round(det.confidence, 4),
            "is_face": face.is_face,
            "quality": quality.reason.value,
        })

    return {"status": "ok", "detections": len(dets), "results": results}


@router.get("/sessions", response_model=list[RecognitionSessionOut])
async def list_sessions(
    status: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RecognitionSession).order_by(RecognitionSession.created_at.desc())
    if status:
        stmt = stmt.where(RecognitionSession.status == status)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RecognitionSession).where(RecognitionSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    samples_result = await db.execute(
        select(RecognitionSample).where(RecognitionSample.session_id == session.id)
    )
    samples = samples_result.scalars().all()

    return {
        "session": RecognitionSessionOut.model_validate(session),
        "samples": [
            {
                "id": s.id,
                "image_path": s.image_path,
                "quality_score": s.quality_score,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in samples
        ],
    }


@router.post("/sessions/{session_id}/assign")
async def assign_session(
    session_id: str,
    req: SessionAssign,
    db: AsyncSession = Depends(get_db),
):
    """Assign collected images from a session to a pet."""
    result = await db.execute(
        select(RecognitionSession).where(RecognitionSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    from ..recognition.registry import save_pet_image
    from ..recognition.embedding import extract_embedding, get_model_version
    from ..recognition.config import STORAGE_DIR
    from ..models import PetImage, PetEmbedding

    # Create new pet if requested
    if req.create_new and req.new_pet_name:
        pet = Pet(name=req.new_pet_name)
        db.add(pet)
        await db.flush()
        pet_id = pet.id
    elif req.pet_id is not None:
        pet_result = await db.execute(select(Pet).where(Pet.id == req.pet_id))
        pet = pet_result.scalar_one_or_none()
        if not pet:
            raise HTTPException(404, "Pet not found")
        pet_id = pet.id
    else:
        raise HTTPException(400, "Must provide pet_id or create_new=true with new_pet_name")

    # Get samples
    if req.selected_sample_ids:
        samples_result = await db.execute(
            select(RecognitionSample).where(
                RecognitionSample.session_id == session.id,
                RecognitionSample.id.in_(req.selected_sample_ids),
            )
        )
    else:
        samples_result = await db.execute(
            select(RecognitionSample).where(RecognitionSample.session_id == session.id)
        )
    samples = samples_result.scalars().all()

    added = 0
    for sample in samples:
        fpath = STORAGE_DIR / sample.image_path
        if not fpath.exists():
            continue
        img = cv2.imread(str(fpath))
        if img is None:
            continue

        # Save as pet image
        rel_path = save_pet_image(pet_id, img)
        pet_img = PetImage(
            pet_id=pet_id,
            image_path=rel_path,
            source="session",
            confirmed=True,
        )
        db.add(pet_img)
        await db.flush()

        # Create embedding
        emb = extract_embedding(img)
        pet_emb = PetEmbedding(
            pet_id=pet_id,
            image_id=pet_img.id,
            embedding=emb.tobytes(),
            model_version=get_model_version(),
        )
        db.add(pet_emb)
        added += 1

    # Update session
    session.assigned_pet_id = pet_id
    session.status = "assigned"

    # Update pet embedding count
    pet_result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = pet_result.scalar_one_or_none()
    if pet:
        pet.embedding_count = (
            await db.execute(
                select(func.count(PetEmbedding.id)).where(PetEmbedding.pet_id == pet_id)
            )
        ).scalar() or 0

    await db.commit()

    # Refresh embedding store
    from .pets import _refresh_pet_in_store
    await _refresh_pet_in_store(pet_id, db)

    return {"ok": True, "added": added, "pet_id": pet_id}


@router.post("/sessions/{session_id}/reject")
async def reject_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RecognitionSession).where(RecognitionSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    session.status = "rejected"
    await db.commit()
    return {"ok": True}


@router.get("/logs", response_model=list[RecognitionLogOut])
async def list_recognition_logs(
    pet_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RecognitionLog).order_by(RecognitionLog.created_at.desc())
    if pet_id is not None:
        stmt = stmt.where(RecognitionLog.pet_id == pet_id)
    if status:
        stmt = stmt.where(RecognitionLog.status == status)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
