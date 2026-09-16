import os
import uuid
import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

def validate_and_save_file(file: UploadFile, document_type: str = "document") -> dict:
    """
    Validates uploaded file against allowed extensions and size limits,
    generates a secure unique filename, and saves it to the uploads directory.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty."
        )

    # Extract and normalize extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{file_ext}' is not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read content and check size
    contents = file.file.read()
    file_size = len(contents)

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE_BYTES / (1024*1024):.0f} MB)."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Generate secure unique stored filename: doc_{uuid}_{timestamp}{ext}
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    stored_filename = f"{document_type}_{timestamp}_{unique_id}{file_ext}"

    destination_path = settings.UPLOAD_DIR / stored_filename

    # Save to disk
    with open(destination_path, "wb") as buffer:
        buffer.write(contents)

    return {
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "file_path": str(destination_path),
        "file_size": file_size,
        "mime_type": file.content_type or "application/octet-stream"
    }
