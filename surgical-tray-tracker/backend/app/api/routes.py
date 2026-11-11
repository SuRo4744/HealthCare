import os
import uuid
import shutil
from typing import Dict, List
from fastapi import APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.models.schemas import TrayAuditResponse
from app.services.detector import process_tray_image

router = APIRouter()
TRAYS_DB: Dict[str, TrayAuditResponse] = {}

def seed_default_tray():
    default_id = "tray-or-04"
    dummy_img = os.path.join(settings.STORAGE_DIR, "uploads", f"{default_id}.jpg")
    audit = process_tray_image(dummy_img, default_id)
    TRAYS_DB[default_id] = audit

seed_default_tray()

@router.get("/trays", response_model=List[TrayAuditResponse])
async def list_trays():
    return list(TRAYS_DB.values())

@router.get("/tray/{tray_id}", response_model=TrayAuditResponse)
async def get_tray(tray_id: str):
    if tray_id not in TRAYS_DB:
        raise HTTPException(status_code=404, detail="Surgical tray audit not found")
    return TRAYS_DB[tray_id]

@router.post("/tray/upload", response_model=TrayAuditResponse)
async def upload_tray_media(
    surgery_type: str = Form("Robotic Total Knee Replacement"),
    file: UploadFile = File(...)
):
    tray_id = f"tray-{uuid.uuid4().hex[:6]}"
    ext = os.path.splitext(file.filename or "tray.jpg")[1] or ".jpg"
    saved_path = os.path.join(settings.STORAGE_DIR, "uploads", f"{tray_id}{ext}")

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audit = process_tray_image(saved_path, tray_id)
    audit.surgery_type = surgery_type
    TRAYS_DB[tray_id] = audit
    return audit

@router.get("/tray/{tray_id}/annotated.jpg")
async def get_annotated_image(tray_id: str):
    uploads_dir = os.path.join(settings.STORAGE_DIR, "uploads")
    for fname in os.listdir(uploads_dir):
        if fname.startswith(tray_id) and "_annotated" in fname:
            return FileResponse(os.path.join(uploads_dir, fname), media_type="image/jpeg")
            
    for fname in os.listdir(uploads_dir):
        if fname.startswith(tray_id):
            return FileResponse(os.path.join(uploads_dir, fname), media_type="image/jpeg")

    import numpy as np
    import cv2
    fallback_path = os.path.join(uploads_dir, f"{tray_id}_annotated.jpg")
    blank = np.zeros((480, 640, 3), dtype=np.uint8) + 50
    cv2.putText(blank, "SurgTrace AI: Tray Scan Active", (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imwrite(fallback_path, blank)
    return FileResponse(fallback_path, media_type="image/jpeg")
