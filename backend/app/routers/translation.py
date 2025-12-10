"""Translation details and download endpoints"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.logger import error as log_error, info
from app.middleware.auth_middleware import get_current_user
from app.models.translation import Translation
from app.models.user import User
from app.s3 import S3Keys, get_presigned_url
from app.schemas.translation import TranslationDetailsResponse

router = APIRouter(prefix="/api/v1", tags=["translation"])


@router.get("/translation/{job_id}", response_model=TranslationDetailsResponse)
async def get_translation_details(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TranslationDetailsResponse:
    """
    Get translation details including PDF URLs.
    
    Returns presigned S3 URLs for both original and translated PDFs.
    URLs are valid for 1 hour.
    
    Args:
        job_id: Translation job ID (UUID)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TranslationDetailsResponse with PDF URLs
        
    Raises:
        404: Translation not found
        403: User doesn't own this translation
    """
    # Validate UUID format
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format",
        )
    
    # Get translation from database
    result = await db.execute(
        select(Translation).where(Translation.id == job_uuid)
    )
    translation = result.scalar_one_or_none()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found",
        )
    
    # Check ownership
    if translation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this translation",
        )
    
    # Generate presigned URLs for PDFs (valid for 1 hour)
    original_s3_key = S3Keys.upload_path(
        user_id=str(translation.user_id),
        job_id=str(translation.id),
        filename=translation.file_name,
    )
    original_pdf_url = get_presigned_url(original_s3_key, expires_in=3600)
    
    # Translated PDF URL (only if translation is complete)
    translated_pdf_url = None
    if translation.status.value == "completed":
        translated_s3_key = S3Keys.result_path(
            user_id=str(translation.user_id),
            job_id=str(translation.id),
            filename=translation.file_name,
        )
        try:
            translated_pdf_url = get_presigned_url(translated_s3_key, expires_in=3600)
        except Exception as e:
            log_error("Failed to generate presigned URL for translated PDF", exc=e, job_id=job_id)
            # Don't fail the request if translated PDF isn't ready yet
    
    # Calculate total cost (translation + tone)
    total_cost = None
    if translation.translation_cost is not None or translation.tone_cost is not None:
        total_cost = (translation.translation_cost or 0) + (translation.tone_cost or 0)
    
    # Build response
    response = TranslationDetailsResponse(
        job_id=str(translation.id),
        file_name=translation.file_name,
        status=translation.status.value,
        original_pdf_url=original_pdf_url,
        translated_pdf_url=translated_pdf_url,
        source_language=translation.source_language,
        target_language=translation.target_language,
        page_count=None,  # TODO: Get from extraction metadata
        cost_usd=total_cost,
        created_at=translation.created_at.isoformat(),
        completed_at=translation.completed_at.isoformat() if translation.completed_at else None,
    )
    
    info(
        "Translation details retrieved",
        job_id=job_id,
        status=translation.status.value,
    )
    
    return response


@router.get("/download/{job_id}")
async def download_translated_pdf(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get download URL for translated PDF.
    
    Returns a presigned S3 URL for downloading the translated PDF.
    URL is valid for 1 hour.
    
    Args:
        job_id: Translation job ID (UUID)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        dict with download_url
        
    Raises:
        404: Translation not found or not completed
        403: User doesn't own this translation
    """
    # Validate UUID format
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format",
        )
    
    # Get translation from database
    result = await db.execute(
        select(Translation).where(Translation.id == job_uuid)
    )
    translation = result.scalar_one_or_none()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found",
        )
    
    # Check ownership
    if translation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to download this translation",
        )
    
    # Check if translation is completed
    if translation.status.value != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Translation is not yet completed",
        )
    
    # Generate presigned URL for translated PDF
    translated_s3_key = S3Keys.result_path(
        user_id=str(translation.user_id),
        job_id=str(translation.id),
        filename=translation.file_name,
    )
    
    try:
        download_url = get_presigned_url(translated_s3_key, expires_in=3600)
    except Exception as e:
        log_error("Failed to generate download URL", exc=e, job_id=job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL",
        )
    
    info("Download URL generated", job_id=job_id)
    
    return {"download_url": download_url}

