"""
Document management and PDF ingestion endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import uuid

from app.core.config import settings
from app.db.session import get_db
from app.models.sql_models import Document, Medicine
from app.models.schemas import DocumentResponse, DocumentUploadResponse
from app.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])


@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded and indexed documents across medicines.
    """
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        resp = DocumentResponse.model_validate(d)
        if d.medicine:
            resp.medicine_name = d.medicine.generic_name
        results.append(resp)
    return results


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    medicine_id: str = Form(...),
    title: Optional[str] = Form(None),
    source: Optional[str] = Form("Official FDA Package Insert"),
    admin_passcode: Optional[str] = Form(None),
    x_admin_passcode: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Upload a new official drug label PDF, parse, chunk, embed, and index it into ChromaDB.
    Requires admin passcode if configured.
    """
    # Verify Admin Passcode if configured
    provided_pass = admin_passcode or x_admin_passcode
    if settings.ADMIN_PASSCODE and provided_pass != settings.ADMIN_PASSCODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin passcode for document ingestion. Check ADMIN_PASSCODE in .env"
        )

    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for drug label ingestion."
        )

    # Verify target medicine exists
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine '{medicine_id}' not found. Please register the medicine first."
        )

    # Save physical file to uploads directory
    settings.ensure_directories()
    safe_filename = f"{uuid.uuid4().hex[:8]}_{Path(file.filename).name}"
    target_path = Path(settings.UPLOAD_DIR) / safe_filename

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process and index
        doc_record = ingestion_service.process_pdf(
            db=db,
            file_path=str(target_path),
            medicine_id=medicine_id,
            title=title or file.filename.replace(".pdf", "").replace("_", " "),
            source=source or "Official Package Insert",
            original_filename=file.filename
        )

        resp = DocumentResponse.model_validate(doc_record)
        resp.medicine_name = medicine.generic_name

        return DocumentUploadResponse(
            document=resp,
            message=f"Successfully parsed and indexed {doc_record.total_chunks} chunks from '{file.filename}'"
        )
    except Exception as e:
        # Clean up file on failure
        target_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process and index PDF: {str(e)}")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    admin_passcode: Optional[str] = Header(None, alias="X-Admin-Passcode"),
    db: Session = Depends(get_db)
):
    """
    Delete a document and purge its vector embeddings from ChromaDB.
    """
    if settings.ADMIN_PASSCODE and admin_passcode != settings.ADMIN_PASSCODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authorization required to delete documents."
        )

    success = ingestion_service.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
