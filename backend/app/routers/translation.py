"""Translation details and download endpoints"""

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
from app.s3 import S3Keys, get_presigned_url
from app.schemas.translation import (
    AlternativesRequest,
    AlternativesResponse,
    ApplyToneRequest,
    ApplyToneResponse,
    RetranslateRequest,
    RetranslateResponse,
    ToneEstimateResponse,
    TranslationDetailsResponse,
)
from app.services.alternatives_service import AlternativesService
from app.services.tone_service import ToneService
from app.tasks.customize_tone import customize_tone_task

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


@router.post("/translation/{job_id}/tone", response_model=ApplyToneResponse)
async def apply_tone(
    job_id: str,
    request: ApplyToneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplyToneResponse:
    """
    Apply tone customization to a translation.
    
    This endpoint triggers a Celery task to apply tone customization
    using Claude API. The task runs asynchronously.
    
    Args:
        job_id: Translation job ID (UUID)
        request: Tone customization request
        db: Database session
        current_user: Authenticated user
        
    Returns:
        ApplyToneResponse with job status
        
    Raises:
        404: Translation not found
        403: User doesn't own this translation
        400: Translation not in correct status
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
            detail="You don't have permission to modify this translation",
        )
    
    # Check if translation is ready for tone customization
    # Must be in TRANSLATING or COMPLETED status
    if translation.status not in [TranslationStatus.TRANSLATING, TranslationStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation must be translated first. Current status: {translation.status.value}",
        )
    
    # Get cost estimate
    redis = get_redis_client()
    cache = Cache(redis)
    
    try:
        # Load translated blocks to estimate cost
        cache_key = f"{CacheKeys.blocks(job_id)}_translated"
        cached_translation = await cache.get_json(cache_key)
        
        estimated_cost = None
        if cached_translation:
            blocks_data = cached_translation.get("blocks", [])
            total_chars = sum(
                len(block.get("translated_text", ""))
                for block in blocks_data
            )
            tone_service = ToneService()
            estimated_cost = tone_service.get_cost_estimate(total_chars)
        
        # Trigger Celery task
        customize_tone_task.delay(job_id, request.tone)
        
        info(
            "Tone customization task triggered",
            job_id=job_id,
            tone=request.tone,
            estimated_cost=estimated_cost,
        )
        
        return ApplyToneResponse(
            success=True,
            job_id=job_id,
            message="Tone customization started",
            estimated_cost_usd=estimated_cost,
        )
    finally:
        await redis.aclose()


@router.get("/translation/{job_id}/tone/estimate", response_model=ToneEstimateResponse)
async def get_tone_estimate(
    job_id: str,
    tone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ToneEstimateResponse:
    """
    Get cost estimate for tone customization.
    
    Args:
        job_id: Translation job ID (UUID)
        tone: Tone preset or custom description
        db: Database session
        current_user: Authenticated user
        
    Returns:
        ToneEstimateResponse with cost estimate
        
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
    
    # Load translated blocks to calculate estimate
    redis = get_redis_client()
    cache = Cache(redis)
    
    try:
        cache_key = f"{CacheKeys.blocks(job_id)}_translated"
        cached_translation = await cache.get_json(cache_key)
        
        if not cached_translation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation not yet completed. Cannot estimate cost.",
            )
        
        blocks_data = cached_translation.get("blocks", [])
        total_chars = sum(
            len(block.get("translated_text", ""))
            for block in blocks_data
        )
        
        tone_service = ToneService()
        estimated_cost = tone_service.get_cost_estimate(total_chars)
        
        return ToneEstimateResponse(
            estimated_cost_usd=estimated_cost,
            character_count=total_chars,
        )
    finally:
        await redis.aclose()


@router.get("/translation/{job_id}/tone/comparison")
async def get_tone_comparison(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get tone comparison data (original vs tone-customized text).
    
    Returns a sample of blocks with both original translation and tone-customized
    text for comparison display.
    
    Args:
        job_id: Translation job ID (UUID)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        dict with comparison blocks and metadata
        
    Raises:
        404: Translation not found
        403: User doesn't own this translation
        400: Tone customization not yet applied
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
    
    # Load tone-customized blocks from cache
    redis = get_redis_client()
    cache = Cache(redis)
    
    try:
        cache_key = f"{CacheKeys.blocks(job_id)}_translated"
        cached_translation = await cache.get_json(cache_key)
        
        if not cached_translation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation data not found",
            )
        
        blocks_data = cached_translation.get("blocks", [])
        
        # Check if tone customization has been applied
        if not any(block.get("tone_customized_text") for block in blocks_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tone customization has not been applied yet",
            )
        
        # Get sample blocks for comparison (first 10 blocks with text)
        comparison_blocks = []
        for block in blocks_data[:10]:  # Get up to 10 blocks for comparison
            translated_text = block.get("translated_text", "")
            tone_customized_text = block.get("tone_customized_text", "")
            
            if translated_text and tone_customized_text:
                comparison_blocks.append({
                    "original": translated_text,
                    "customized": tone_customized_text,
                })
        
        # Get tone info
        tone = cached_translation.get("tone", translation.tone_preset or translation.custom_tone or "unknown")
        tone_cost = cached_translation.get("tone_cost", translation.tone_cost)
        
        return {
            "blocks": comparison_blocks,
            "tone": tone,
            "cost_usd": tone_cost,
            "total_blocks": len(blocks_data),
            "sample_count": len(comparison_blocks),
        }
    finally:
        await redis.aclose()


@router.get("/translation/{job_id}/blocks")
async def get_translation_blocks(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get translation blocks for editing.
    
    Returns all blocks with original and translated text for a translation job.
    Used by the frontend to display and edit individual blocks.
    
    Args:
        job_id: Translation job ID (UUID)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        dict with blocks array
        
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
    
    # Load translated blocks from cache
    redis = get_redis_client()
    cache = Cache(redis)
    
    try:
        cache_key = f"{CacheKeys.blocks(job_id)}_translated"
        cached_translation = await cache.get_json(cache_key)
        
        if not cached_translation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation blocks not found. Translation may not be complete.",
            )
        
        blocks_data = cached_translation.get("blocks", [])
        
        # Format blocks for frontend
        formatted_blocks = []
        for idx, block in enumerate(blocks_data):
            formatted_blocks.append({
                "block_id": str(idx),  # Use index as block_id for now
                "page_num": block.get("page_num", 0),
                "block_num": block.get("block_num", idx),
                "original_text": block.get("original_text", ""),
                "translated_text": block.get("translated_text", ""),
                "tone_customized_text": block.get("tone_customized_text"),
            })
        
        return {
            "blocks": formatted_blocks,
            "total_blocks": len(formatted_blocks),
            "source_language": translation.source_language,
            "target_language": translation.target_language,
        }
    finally:
        await redis.aclose()


@router.post("/alternatives", response_model=AlternativesResponse)
async def get_alternatives(
    request: AlternativesRequest,
    current_user: User = Depends(get_current_user),
) -> AlternativesResponse:
    """
    Generate alternative translations for a given text.
    
    Uses Claude API to generate 2-5 alternative translations with different
    phrasing or style.
    
    Args:
        request: Alternatives request with text, target language, and count
        current_user: Authenticated user
        
    Returns:
        AlternativesResponse with list of alternative translations
        
    Raises:
        400: Invalid request
        500: API error
    """
    try:
        alternatives_service = AlternativesService()
        alternatives, cost = await alternatives_service.generate_alternatives(
            text=request.text,
            target_lang=request.target_lang,
            count=request.count,
        )
        
        # Filter out empty alternatives
        alternatives = [alt for alt in alternatives if alt.strip()]
        
        info(
            "Alternatives generated",
            user_id=str(current_user.id),
            alternatives_count=len(alternatives),
            cost_usd=cost,
        )
        
        return AlternativesResponse(alternatives=alternatives)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log_error("Failed to generate alternatives", exc=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate alternatives",
        )


@router.post("/retranslate", response_model=RetranslateResponse)
async def retranslate_text(
    request: RetranslateRequest,
    current_user: User = Depends(get_current_user),
) -> RetranslateResponse:
    """
    Re-translate edited text with custom tone.
    
    Uses Claude API to re-translate text with a specific tone applied.
    This is useful when users edit a translation and want to re-translate
    it with a different tone.
    
    Args:
        request: Re-translation request with text, tone, and target language
        current_user: Authenticated user
        
    Returns:
        RetranslateResponse with re-translated text and cost
        
    Raises:
        400: Invalid request
        500: API error
    """
    try:
        tone_service = ToneService()
        
        # Apply tone customization (which effectively re-translates with tone)
        translated_text, cost = await tone_service.apply_tone(
            text=request.text,
            tone=request.tone,
            target_lang=request.target_lang,
        )
        
        info(
            "Text re-translated",
            user_id=str(current_user.id),
            tone=request.tone,
            cost_usd=cost,
        )
        
        return RetranslateResponse(
            translated_text=translated_text,
            cost_usd=cost,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Graceful degradation: if tone customization fails, return original text
        warning(
            "Tone customization failed, returning original text",
            exc=e,
            user_id=str(current_user.id),
            tone=request.tone,
        )
        
        # Return original text with degraded mode indicator
        return RetranslateResponse(
            translated_text=request.text,  # Return original text
            cost_usd=0.0,
            degraded_mode=True,
            degraded_message="Tone customization temporarily unavailable. Original text returned.",
        )

