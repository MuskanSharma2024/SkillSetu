from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
import os

from app.database import get_db
from app.models import User, Document, StudentProfile
from app.schemas import DocumentResponse
from app.dependencies import get_current_user
from app.utils.storage import validate_and_save_file

router = APIRouter(prefix="/documents", tags=["Documents"])

def build_doc_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        document_type=doc.document_type,
        original_filename=doc.original_filename,
        stored_filename=doc.stored_filename,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        download_url=f"/api/documents/{doc.id}/download",
        created_at=doc.created_at
    )

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("resume"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure document upload endpoint with size and extension validation.
    Stores file to local secure storage and records metadata in the database.
    If the document is a resume and user is a student, automatically updates the student profile.
    """
    valid_types = ["resume", "certificate", "id_proof", "curriculum_doc"]
    if document_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed types: {', '.join(valid_types)}"
        )

    saved_info = validate_and_save_file(file, document_type)

    doc_record = Document(
        user_id=current_user.id,
        document_type=document_type,
        original_filename=saved_info["original_filename"],
        stored_filename=saved_info["stored_filename"],
        file_path=saved_info["file_path"],
        file_size=saved_info["file_size"],
        mime_type=saved_info["mime_type"]
    )
    db.add(doc_record)
    db.flush()

    # Link to student profile if resume
    if document_type == "resume" and current_user.role == "student":
        student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if student_prof:
            student_prof.resume_url = f"/api/documents/{doc_record.id}/download"

    db.commit()
    db.refresh(doc_record)

    return build_doc_response(doc_record)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_metadata(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve metadata for a stored document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return build_doc_response(doc)

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Securely stream or download a stored document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Underlying file not found on disk."
        )

    return FileResponse(
        path=file_path,
        filename=doc.original_filename,
        media_type=doc.mime_type
    )

@router.get("", response_model=List[DocumentResponse])
def list_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents uploaded by the currently authenticated user."""
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return [build_doc_response(d) for d in docs]
