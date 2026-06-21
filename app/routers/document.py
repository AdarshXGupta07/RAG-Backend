from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from app.dependencies.auth import get_current_user
from app.models.document import Document
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
import os, uuid

# ✅ Celery task import
from app.tasks import process_document

# ✅ NEW: Rate limiter import
from app.core.limiter import limiter

router = APIRouter(prefix="/documents", tags=["documents"])

# ✅ Upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ NEW: File validation constants
ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
@limiter.limit("20/minute")   # ✅ NEW: per-tenant rate limit
async def upload_file(
    request: Request,          # ✅ NEW: slowapi ko chahiye, function ka pehla param hona zaroori hai
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ NEW: File validation — content type check
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' allowed nahi hai. Sirf PDF ya TXT allowed hai."
        )

    # File disk pe save karo
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"
    file_bytes = await file.read()

    # ✅ NEW: File validation — size check
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File 10MB se badi hai")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # status "pending" → "queued", file_path add kiya
    document = Document(
        filename=file.filename,
        tenant_id=current_user.tenant_id,
        file_path=file_path,   # ← worker ko chahiye
        status="queued"        # ← "pending" tha pehle
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Background task fire karo
    process_document.delay(
        document_id=str(document.id),
        tenant_id=str(current_user.tenant_id)
    )

    # Turant return — chunking ka wait nahi
    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": "queued"     # ← "processed" nahi, abhi sirf queued hai
    }


# Status check endpoint
@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    from app.models.chunk import Chunk
    chunk_count = db.query(Chunk).filter(
        Chunk.document_id == document_id
    ).count()

    return {
        "document_id": document_id,
        "filename": document.filename,
        "status": document.status,
        "chunks_created": chunk_count
    }