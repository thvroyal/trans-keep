"""Translation Celery task"""

from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import Cache, CacheKeys, get_redis_client
from app.database import get_db
from app.logger import error as log_error, info
from app.models.translation import Translation, TranslationStatus
from app.schemas.pdf import Block
from app.services.pdf_service import PDFService
from app.services.translation_service import TranslationService


# Note: Celery app will be configured in Story 2.4
# For now, this is a stub that shows the task structure

# @celery_app.task(bind=True, max_retries=3, rate_limit='10/m')
# async def translate_blocks_task(self, job_id: str) -> dict:
#     """
#     Celery task to translate extracted text blocks.
#     
#     This task will be activated once Celery is configured in Story 2.4.
#     
#     Args:
#         job_id: Translation job ID
#         
#     Returns:
#         dict with translation results
#     """
#     return await translate_blocks_sync(job_id)


async def translate_blocks_sync(
    job_id: str,
    db: AsyncSession,
) -> dict:
    """
    Synchronous translation function (can be called directly or from Celery).
    
    This function:
    1. Loads extracted blocks from Redis cache (from Story 2.2)
    2. Translates blocks using DeepL with batch processing
    3. Stores translated blocks in Redis cache
    4. Updates translation status and cost in database
    
    Args:
        job_id: Translation job ID
        db: Database session
        
    Returns:
        dict with translation results
        
    Raises:
        Exception: If translation fails
    """
    try:
        info("Starting translation", job_id=job_id)
        
        # Get translation record from database
        translation = await db.get(Translation, UUID(job_id))
        
        if not translation:
            log_error("Translation not found", job_id=job_id)
            raise ValueError(f"Translation {job_id} not found")
        
        # Update status to translating
        translation.status = TranslationStatus.TRANSLATING
        translation.progress_percent = 50  # Extraction done, translation starting
        await db.commit()
        
        # Get Redis client for loading cached blocks
        redis = await get_redis_client()
        cache = Cache(redis)
        
        try:
            # Load extracted blocks from Redis cache (from extraction task)
            cache_key = CacheKeys.blocks(job_id)
            cached_extraction = await cache.get_json(cache_key)
            
            if not cached_extraction:
                log_error("Extracted blocks not found in cache", job_id=job_id)
                raise ValueError(f"No extracted blocks found for job {job_id}")
            
            # Deserialize blocks
            extraction_result = PDFService._deserialize_extraction_result(cached_extraction)
            blocks = extraction_result.blocks
            
            info(
                "Loaded extracted blocks from cache",
                job_id=job_id,
                block_count=len(blocks),
            )
            
            # Update progress
            translation.progress_percent = 60
            await db.commit()
            
            # Initialize translation service
            translation_service = TranslationService()
            
            # Translate blocks with batch processing
            info(
                "Starting batch translation",
                job_id=job_id,
                blocks=len(blocks),
                source_lang=translation.source_language,
                target_lang=translation.target_language,
            )
            
            translated_blocks, translation_cost = await translation_service.batch_translate(
                blocks=blocks,
                source_lang=translation.source_language,
                target_lang=translation.target_language,
            )
            
            # Update progress
            translation.progress_percent = 90
            await db.commit()
            
            # Store translated blocks in Redis cache
            # Format: {translation_id}_translated
            translated_cache_key = f"{cache_key}_translated"
            translated_data = {
                "blocks": [
                    {
                        "original": {
                            "page": tb.original.page,
                            "block_id": tb.original.block_id,
                            "text": tb.original.text,
                            "coordinates": {
                                "x": tb.original.coordinates.x,
                                "y": tb.original.coordinates.y,
                                "width": tb.original.coordinates.width,
                                "height": tb.original.coordinates.height,
                            },
                            "font_size": tb.original.font_size,
                            "font_name": tb.original.font_name,
                            "is_bold": tb.original.is_bold,
                            "is_italic": tb.original.is_italic,
                            "rotation": tb.original.rotation,
                        },
                        "translated_text": tb.translated_text,
                        "source_lang": tb.source_lang,
                        "target_lang": tb.target_lang,
                        "billed_characters": tb.billed_characters,
                    }
                    for tb in translated_blocks
                ],
                "total_cost": translation_cost,
                "total_blocks": len(translated_blocks),
            }
            
            # Cache for 24 hours
            await cache.set_json(
                translated_cache_key,
                translated_data,
                expire_seconds=24 * 60 * 60,
            )
            
            info(
                "Translation complete",
                job_id=job_id,
                translated_blocks=len(translated_blocks),
                cost_usd=f"${translation_cost:.4f}",
            )
            
            # Update translation record
            translation.translation_cost = translation_cost
            translation.progress_percent = 100
            translation.status = TranslationStatus.COMPLETED
            await db.commit()
            
            # Get usage stats
            usage = translation_service.get_usage()
            info(
                "DeepL usage after translation",
                job_id=job_id,
                character_count=usage.get("character_count"),
                character_remaining=usage.get("character_remaining"),
            )
            
            return {
                "success": True,
                "translated_blocks": len(translated_blocks),
                "cost_usd": translation_cost,
                "billed_characters": sum(tb.billed_characters for tb in translated_blocks),
            }
            
        finally:
            # Ensure Redis client is closed
            await redis.aclose()
        
    except Exception as e:
        log_error("Translation failed", exc=e, job_id=job_id)
        
        # Update translation status to failed
        try:
            translation = await db.get(Translation, UUID(job_id))
            if translation:
                translation.status = TranslationStatus.FAILED
                translation.error_message = f"Translation error: {str(e)}"
                await db.commit()
        except Exception:
            pass  # Best effort error recording
        
        raise


async def get_translated_blocks_from_cache(
    job_id: str,
    redis,
) -> dict | None:
    """
    Retrieve translated blocks from Redis cache.
    
    Args:
        job_id: Translation job ID
        redis: Redis client
        
    Returns:
        Dict with translated blocks or None if not found
    """
    cache = Cache(redis)
    cache_key = f"{CacheKeys.blocks(job_id)}_translated"
    
    return await cache.get_json(cache_key)
