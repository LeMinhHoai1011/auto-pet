"""Pet management API endpoints."""

from __future__ import annotations

import io
import logging
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Pet, PetImage, PetEmbedding
from ..schemas import PetCreate, PetUpdate, PetOut, PetImageOut
from ..recognition import torch_available, torch_error

logger = logging.getLogger("api.pets")


def _require_torch():
    if not torch_available:
        raise HTTPException(503, torch_error)

router = APIRouter(prefix="/api/pets", tags=["pets"])


@router.get("/", response_model=list[PetOut])
async def list_pets(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Pet).order_by(Pet.name)
    if active_only:
        stmt = stmt.where(Pet.active == True)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=PetOut)
async def create_pet(req: PetCreate, db: AsyncSession = Depends(get_db)):
    pet = Pet(
        name=req.name,
        breed=req.breed,
        color=req.color,
        age_months=req.age_months,
        weight_kg=req.weight_kg,
        notes=req.notes,
        portion_grams=req.portion_grams,
        daily_limit_grams=req.daily_limit_grams,
        min_feed_interval_min=req.min_feed_interval_min,
        auto_feed=req.auto_feed,
    )
    db.add(pet)
    await db.commit()
    await db.refresh(pet)
    return pet


@router.get("/{pet_id}", response_model=PetOut)
async def get_pet(pet_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, "Pet not found")
    return pet


@router.patch("/{pet_id}", response_model=PetOut)
async def update_pet(pet_id: int, req: PetUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, "Pet not found")

    for field_name, value in req.model_dump(exclude_unset=True).items():
        setattr(pet, field_name, value)
    await db.commit()
    await db.refresh(pet)

    # Refresh embedding store if needed
    if req.name is not None or req.active is not None:
        await _refresh_pet_in_store(pet_id, db)

    return pet


@router.delete("/{pet_id}")
async def deactivate_pet(pet_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, "Pet not found")
    pet.active = False
    await db.commit()
    from ..recognition.matcher import embedding_store
    embedding_store.remove_pet(pet_id)
    return {"ok": True, "message": "Pet deactivated (not deleted, to preserve history)"}


@router.post("/{pet_id}/images", response_model=list[dict])
async def upload_pet_images(
    pet_id: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, "Pet not found")

    _require_torch()
    from ..recognition.registry import process_upload_image, save_pet_image
    from ..recognition.embedding import get_model_version

    results = []
    new_embeddings = 0

    for f in files:
        if f.content_type and not f.content_type.startswith("image/"):
            results.append({"filename": f.filename, "accepted": False, "reason": "not_image"})
            continue

        data = await f.read()
        if len(data) > 10 * 1024 * 1024:
            results.append({"filename": f.filename, "accepted": False, "reason": "too_large"})
            continue

        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            results.append({"filename": f.filename, "accepted": False, "reason": "decode_failed"})
            continue

        processed = process_upload_image(img)
        if not processed["accepted"]:
            results.append({"filename": f.filename, "accepted": False, "reason": processed["reason"]})
            continue

        # Save image
        rel_path = save_pet_image(pet_id, processed["crop"])

        # Save to DB
        pet_image = PetImage(
            pet_id=pet_id,
            image_path=rel_path,
            source="upload",
            is_face=processed.get("is_face", False),
            phash=processed.get("phash"),
            confirmed=True,
        )
        db.add(pet_image)
        await db.flush()

        # Save embedding
        emb_bytes = processed["embedding"].tobytes()
        pet_emb = PetEmbedding(
            pet_id=pet_id,
            image_id=pet_image.id,
            embedding=emb_bytes,
            model_version=get_model_version(),
        )
        db.add(pet_emb)
        new_embeddings += 1

        results.append({
            "filename": f.filename,
            "accepted": True,
            "image_id": pet_image.id,
            "is_face": processed.get("is_face", False),
        })

    if new_embeddings > 0:
        pet.embedding_count = (
            await db.execute(
                select(func.count(PetEmbedding.id)).where(PetEmbedding.pet_id == pet_id)
            )
        ).scalar() or 0
        await db.commit()
        await _refresh_pet_in_store(pet_id, db)
    else:
        await db.commit()

    return results


@router.delete("/{pet_id}/images/{image_id}")
async def delete_pet_image(
    pet_id: int, image_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PetImage).where(PetImage.id == image_id, PetImage.pet_id == pet_id)
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(404, "Image not found")

    from ..recognition.registry import delete_pet_image_file
    delete_pet_image_file(image.image_path)

    # Delete associated embeddings
    emb_result = await db.execute(
        select(PetEmbedding).where(PetEmbedding.image_id == image_id)
    )
    for emb in emb_result.scalars().all():
        await db.delete(emb)

    await db.delete(image)

    # Update embedding count
    pet_result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = pet_result.scalar_one_or_none()
    if pet:
        pet.embedding_count = (
            await db.execute(
                select(func.count(PetEmbedding.id)).where(PetEmbedding.pet_id == pet_id)
            )
        ).scalar() or 0

    await db.commit()
    await _refresh_pet_in_store(pet_id, db)
    return {"ok": True}


@router.post("/{pet_id}/embeddings/rebuild")
async def rebuild_embeddings(pet_id: int, db: AsyncSession = Depends(get_db)):
    """Rebuild all embeddings for a pet from their confirmed images."""
    _require_torch()
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet:
        raise HTTPException(404, "Pet not found")

    # Delete existing embeddings
    emb_result = await db.execute(
        select(PetEmbedding).where(PetEmbedding.pet_id == pet_id)
    )
    for emb in emb_result.scalars().all():
        await db.delete(emb)
    await db.flush()

    # Rebuild from confirmed images
    from ..recognition.embedding import extract_embedding, get_model_version
    from ..recognition.config import STORAGE_DIR

    img_result = await db.execute(
        select(PetImage).where(PetImage.pet_id == pet_id, PetImage.confirmed == True)
    )
    count = 0
    for img in img_result.scalars().all():
        fpath = STORAGE_DIR / img.image_path
        if not fpath.exists():
            continue
        bgr = cv2.imread(str(fpath))
        if bgr is None:
            continue
        emb = extract_embedding(bgr)
        pet_emb = PetEmbedding(
            pet_id=pet_id,
            image_id=img.id,
            embedding=emb.tobytes(),
            model_version=get_model_version(),
        )
        db.add(pet_emb)
        count += 1

    pet.embedding_count = count
    await db.commit()
    await _refresh_pet_in_store(pet_id, db)
    return {"ok": True, "rebuilt": count}


@router.get("/{pet_id}/images", response_model=list[PetImageOut])
async def list_pet_images(pet_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PetImage).where(PetImage.pet_id == pet_id).order_by(PetImage.created_at.desc())
    )
    return result.scalars().all()


async def _refresh_pet_in_store(pet_id: int, db: AsyncSession) -> None:
    from ..recognition.matcher import embedding_store

    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if not pet or not pet.active:
        embedding_store.remove_pet(pet_id)
        return

    emb_result = await db.execute(
        select(PetEmbedding).where(PetEmbedding.pet_id == pet_id)
    )
    embeddings = []
    for emb in emb_result.scalars().all():
        arr = np.frombuffer(emb.embedding, dtype=np.float32)
        embeddings.append(arr)

    embedding_store.update_pet(pet_id, pet.name, embeddings)
