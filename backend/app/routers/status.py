"""Status polling endpoint for translation jobs"""

import time
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import Cache, CacheKeys, get_redis_client
from app.database import get_db
from app.logger import error as log_error, info
from app.middleware.auth_middleware import get_current_user
from app.models.translation import Translation, TranslationStatus
from app.models.user import User
from app.schemas.status import StatusResponse

router = APIRouter(prefix="/api/v1", tags=["status"])


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_translation_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatusResponse:
    """
    Get translation job status.
    
    This endpoint is designed for polling. Frontend should call every 2 seconds
    until status is 'completed' or 'failed'.
    
    Args:
        job_id: Translation job ID (UUID)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        StatusResponse with current job status and progress
        
    Raises:
        404: Job not found
        403: User doesn't own this job
        500: Server error
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
            detail="Translation job not found",
        )
    
    # Check ownership
    if translation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this job",
        )
    
    # Get cached progress data from Redis
    redis = get_redis_client()
    cache = Cache(redis)
    progress_key = CacheKeys.job_progress(job_id)
    progress_data = await cache.get_json(progress_key)
    
    # Calculate progress percentage
    progress_percent = _calculate_progress(
        translation.status,
        progress_data,
    )
    
    # Get block counts from cache
    total_blocks = None
    translated_blocks = None
    page_count = None
    
    if progress_data:
        total_blocks = progress_data.get("total_blocks")
        translated_blocks = progress_data.get("translated_blocks")
        page_count = progress_data.get("total_pages")
    
    # Calculate ETA
    eta_seconds = _calculate_eta(
        translation.created_at,
        translation.started_at,
        progress_percent,
    )
    
    # Calculate total cost (translation + tone)
    total_cost = None
    if translation.translation_cost is not None or translation.tone_cost is not None:
        total_cost = (translation.translation_cost or 0) + (translation.tone_cost or 0)
    
    # Build response
    response = StatusResponse(
        job_id=str(translation.id),
        status=translation.status.value,
        progress=progress_percent,
        file_name=translation.file_name,
        page_count=page_count,
        total_blocks=total_blocks,
        translated_blocks=translated_blocks,
        created_at=translation.created_at.isoformat(),
        started_at=translation.started_at.isoformat() if translation.started_at else None,
        completed_at=translation.completed_at.isoformat() if translation.completed_at else None,
        eta_seconds=eta_seconds,
        source_language=translation.source_language,
        target_language=translation.target_language,
        estimated_cost_usd=total_cost,
        error_message=translation.error_message,
    )
    
    info(
        "Status polled",
        job_id=job_id,
        status=translation.status.value,
        progress=progress_percent,
    )
    
    return response


def _calculate_progress(
    status: TranslationStatus,
    progress_data: Optional[dict],
) -> int:
    """
    Calculate progress percentage based on status and cached data.
    
    Args:
        status: Current translation status
        progress_data: Progress data from Redis cache
        
    Returns:
        Progress percentage (0-100)
    """
    # Status-based progress
    if status == TranslationStatus.PENDING:
        return 0
    elif status == TranslationStatus.EXTRACTING:
        # 0-30% during extraction
        if progress_data and "current_page" in progress_data:
            current = progress_data["current_page"]
            total = progress_data.get("total_pages", 1)
            if total > 0:
                return int((current / total) * 30)
        return 15  # Default mid-extraction
    elif status == TranslationStatus.TRANSLATING:
        # 30-95% during translation
        if progress_data and "translated_blocks" in progress_data:
            translated = progress_data["translated_blocks"]
            total = progress_data.get("total_blocks", 1)
            if total > 0:
                # Map 0-100% translation to 30-95% overall
                translation_progress = (translated / total)
                return int(30 + (translation_progress * 65))
        return 60  # Default mid-translation
    elif status == TranslationStatus.COMPLETED:
        return 100
    elif status == TranslationStatus.FAILED:
        # Return last known progress
        if progress_data and "progress_percent" in progress_data:
            return progress_data["progress_percent"]
        return 0
    
    return 0


def _calculate_eta(
    created_at: datetime,
    started_at: Optional[datetime],
    progress_percent: int,
) -> Optional[int]:
    """
    Calculate estimated time remaining in seconds.
    
    Args:
        created_at: Job creation time
        started_at: Processing start time
        progress_percent: Current progress (0-100)
        
    Returns:
        Estimated seconds remaining, or None if can't calculate
    """
    if progress_percent == 0 or progress_percent == 100:
        return None
    
    if not started_at:
        return None
    
    # Calculate elapsed time since start
    elapsed_seconds = (datetime.utcnow() - started_at).total_seconds()
    
    if elapsed_seconds <= 0:
        return None
    
    # Estimate total time: elapsed / (progress / 100)
    estimated_total_seconds = elapsed_seconds / (progress_percent / 100)
    
    # ETA = total - elapsed
    eta = int(estimated_total_seconds - elapsed_seconds)
    
    # Clamp to reasonable range (0 to 1 hour)
    return max(0, min(eta, 3600))

