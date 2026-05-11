from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from backend.database.models import User, UserRole
from backend.security.auth import get_current_user

router = APIRouter(prefix="/files", tags=["File Uploads"])

UPLOAD_ROOT = Path("uploads")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    patient_id: int | None = Form(default=None),
    document_type: str = Form(default="general"),
    description: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user.role == UserRole.patient:
        if not current_user.patient_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient account is not linked to a chart")
        patient_id = current_user.patient_id

    if current_user.role != UserRole.patient and patient_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="patient_id is required for staff uploads")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10MB limit")

    safe_name = "".join(char for char in (file.filename or "upload.bin") if char.isalnum() or char in ("-", "_", "."))
    if not safe_name:
        safe_name = "upload.bin"

    upload_date = datetime.now(UTC).date().isoformat()
    upload_dir = UPLOAD_ROOT / upload_date
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}_{safe_name}"
    stored_path = upload_dir / stored_name
    stored_path.write_bytes(contents)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "stored_path": str(stored_path),
        "content_type": file.content_type,
        "size": len(contents),
        "patient_id": patient_id,
        "document_type": document_type,
        "description": description,
        "uploaded_by": current_user.id,
    }
