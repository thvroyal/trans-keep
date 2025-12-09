"""Upload router for file uploads"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.translation import Translation, TranslationStatus
from app.models.user import User
from app.s3 import S3Keys, upload_file
from app.schemas.upload import UploadResponse
from app.logger import info, error as log_error
from app.tasks.orchestrator import trigger_translation_pipeline

router = APIRouter(prefix="/api/v1", tags=["upload"])

# File validation constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
ALLOWED_CONTENT_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename with only safe characters
    """
    # Get the base name (remove any path components)
    safe_name = Path(filename).name
    
    # Replace unsafe characters
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ")
    safe_name = "".join(c if c in safe_chars else "_" for c in safe_name)
    
    # Ensure it has a .pdf extension
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    
    return safe_name[:255]  # Limit length


async def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file type and size.
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If validation fails
    """
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF files are supported. Received: {file.content_type}",
        )
    
    # Check file extension
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Only .pdf files are supported. Received: {ext}",
            )
    
    # Check file size by reading the content
    contents = await file.read()
    file_size = len(contents)
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )
    
    if file_size > MAX_FILE_SIZE:
        file_size_mb = file_size / (1024 * 1024)
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {max_size_mb}MB. Your file is {file_size_mb:.2f}MB",
        )
    
    # Reset file pointer for subsequent reads
    await file.seek(0)
    
    return contents, file_size


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to translate"),
    target_language: str = Form(..., description="Target language code (e.g., 'ja', 'es', 'fr')"),
    source_language: str = Form(default="auto", description="Source language code or 'auto' for auto-detect"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload a PDF file for translation.
    
    This endpoint:
    1. Validates the file (type, size, content)
    2. Uploads to S3 with organized key structure
    3. Creates a database record with 'pending' status
    4. Returns job_id for status polling
    
    Rate limits:
    - Free tier: 10 files/month
    - Pro tier: 100 files/month
    
    Args:
        file: PDF file (max 100MB)
        target_language: Target language code
        source_language: Source language code or 'auto'
        current_user: Authenticated user (from JWT)
        db: Database session
        
    Returns:
        UploadResponse with job_id and status
        
    Raises:
        HTTPException 400: Invalid file type/size
        HTTPException 413: File too large
        HTTPException 500: Server error during upload
    """
    # Log upload attempt
    info(
        "Upload attempt started",
        user_id=str(current_user.id),
        filename=file.filename,
        content_type=file.content_type,
    )
    
    # Validate file
    try:
        contents, file_size = await validate_file(file)
    except HTTPException:
        raise
    except Exception as e:
        log_error("File validation failed", exc=e, filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate file",
        )
    
    # Generate unique job ID
    job_id = uuid.uuid4()
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename or "document.pdf")
    
    # Generate S3 key
    s3_key = S3Keys.upload_path(
        user_id=str(current_user.id),
        job_id=str(job_id),
        filename=safe_filename,
    )
    
    # Upload to S3
    try:
        await upload_file(
            file_data=contents,
            key=s3_key,
            content_type="application/pdf",
        )
        info(
            "File uploaded to S3",
            job_id=str(job_id),
            s3_key=s3_key,
            file_size=file_size,
        )
    except Exception as e:
        log_error("S3 upload failed", exc=e, job_id=str(job_id), s3_key=s3_key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage",
        )
    
    # Create database record
    try:
        translation = Translation(
            id=job_id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            file_name=safe_filename,
            file_size_bytes=file_size,
            source_language=source_language.lower().strip(),
            target_language=target_language.lower().strip(),
            status=TranslationStatus.PENDING,
            progress_percent=0,
            original_file_path=s3_key,
        )
        
        db.add(translation)
        await db.commit()
        await db.refresh(translation)
        
        info(
            "Translation record created",
            job_id=str(job_id),
            user_id=str(current_user.id),
            status=translation.status.value,
        )
        
        # Trigger Celery pipeline to process the translation
        try:
            task_id = trigger_translation_pipeline(str(job_id))
            info(
                "Translation pipeline triggered",
                job_id=str(job_id),
                task_id=task_id,
            )
        except Exception as e:
            log_error("Failed to trigger translation pipeline", exc=e, job_id=str(job_id))
            # Don't fail the upload if pipeline trigger fails
            # User can retry or admin can manually trigger
        
    except Exception as e:
        log_error("Database record creation failed", exc=e, job_id=str(job_id))
        # Try to clean up S3 file if DB fails
        try:
            from app.s3 import delete_file
            await delete_file(s3_key)
        except Exception:
            pass  # Best effort cleanup
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create translation record",
        )
    
    # Return response
    return UploadResponse(
        job_id=str(job_id),
        status="pending",
        message="File uploaded successfully. Translation will begin shortly.",
        file_name=safe_filename,
        file_size_bytes=file_size,
    )
