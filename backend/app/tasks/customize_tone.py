"""Tone customization Celery task"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.cache import Cache, CacheKeys, get_redis_client
from app.database import get_db
from app.logger import error as log_error, info
from app.models.translation import Translation, TranslationStatus
from app.schemas.pdf import Block, Coordinates
from app.services.tone_service import ToneService
from app.services.translation_service import TranslatedBlock


@celery_app.task(
    name="customize_tone",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute delay between retries
    time_limit=900,  # 15 minutes max
)
def customize_tone_task(self, job_id: str, tone: str) -> dict:
    """
    Celery task to apply tone customization to translated blocks.
    
    Args:
        job_id: Translation job ID
        tone: Tone preset or custom description
        
    Returns:
        dict with tone customization results
    """
    import asyncio
    
    try:
        return asyncio.run(_customize_tone_async(job_id, tone))
    except Exception as e:
        log_error("Customize tone task failed", exc=e, job_id=job_id)
        raise self.retry(exc=e)


async def _customize_tone_async(job_id: str, tone: str) -> dict:
    """Async wrapper for tone customization"""
    from app.database import get_async_session
    
    async with get_async_session() as db:
        return await customize_tone_sync(job_id, tone, db)


async def customize_tone_sync(
    job_id: str,
    tone: str,
    db: AsyncSession,
) -> dict:
    """
    Synchronous tone customization function (can be called directly or from Celery).
    
    This function:
    1. Loads translated blocks from Redis cache
    2. Applies tone customization using Claude API
    3. Stores tone-customized blocks back in cache
    4. Updates translation record with cost
    
    Args:
        job_id: Translation job ID
        tone: Tone preset or custom description
        db: Database session
        
    Returns:
        dict with tone customization results
        
    Raises:
        Exception: If tone customization fails
    """
    try:
        info("Starting tone customization", job_id=job_id, tone=tone)
        
        # Get translation record from database
        translation = await db.get(Translation, UUID(job_id))
        
        if not translation:
            log_error("Translation not found", job_id=job_id)
            raise ValueError(f"Translation {job_id} not found")
        
        # Update status to applying tone
        translation.status = TranslationStatus.APPLYING_TONE
        translation.progress_percent = 85  # Translation done, now customizing tone
        await db.commit()
        
        # Get Redis client for loading cached blocks
        redis = get_redis_client()
        cache = Cache(redis)
        
        try:
            # Load translated blocks from Redis cache
            cache_key = f"{CacheKeys.blocks(job_id)}_translated"
            cached_translation = await cache.get_json(cache_key)
            
            if not cached_translation:
                log_error("Translated blocks not found in cache", job_id=job_id)
                raise ValueError(f"No translated blocks found for job {job_id}")
            
            blocks_data = cached_translation.get("blocks", [])
            info(
                "Loaded translated blocks from cache",
                job_id=job_id,
                block_count=len(blocks_data),
            )
            
            # Convert dict blocks to TranslatedBlock objects
            translated_blocks: list[TranslatedBlock] = []
            for block_data in blocks_data:
                original_data = block_data.get("original", {})
                coords_data = original_data.get("coordinates", {})
                
                original_block = Block(
                    page=original_data.get("page", 0),
                    block_id=original_data.get("block_id", 0),
                    text=original_data.get("text", ""),
                    coordinates=Coordinates(
                        x=coords_data.get("x", 0),
                        y=coords_data.get("y", 0),
                        width=coords_data.get("width", 0),
                        height=coords_data.get("height", 0),
                    ),
                    font_size=original_data.get("font_size", 12),
                    font_name=original_data.get("font_name", "Unknown"),
                    is_bold=original_data.get("is_bold", False),
                    is_italic=original_data.get("is_italic", False),
                    rotation=original_data.get("rotation", 0),
                )
                
                translated_block = TranslatedBlock(
                    original=original_block,
                    translated_text=block_data.get("translated_text", ""),
                    source_lang=block_data.get("source_lang", "auto"),
                    target_lang=block_data.get("target_lang", "en"),
                    billed_characters=block_data.get("billed_characters", 0),
                )
                translated_blocks.append(translated_block)
            
            # Apply tone customization with graceful degradation
            tone_service = ToneService()
            try:
                customized_blocks, total_cost = await tone_service.batch_apply_tone(
                    blocks=translated_blocks,
                    tone=tone,
                )
                
                info(
                    "Tone customization complete",
                    job_id=job_id,
                    block_count=len(customized_blocks),
                    cost_usd=f"${total_cost:.6f}",
                )
            except Exception as tone_error:
                # Graceful degradation: if tone customization fails, use original translated blocks
                warning(
                    "Tone customization failed, using original translations",
                    exc=tone_error,
                    job_id=job_id,
                    tone=tone,
                )
                
                # Use original translated blocks (no tone customization)
                customized_blocks = translated_blocks
                total_cost = 0.0
                
                # Store degraded mode indicator
                translation.warning_message = (
                    "Tone customization temporarily unavailable. "
                    "Translation completed without tone adjustments."
                )
            
            # Store tone-customized blocks in cache
            # Add tone_customized_text to existing cache structure
            tone_customized_data = {
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
                        "tone_customized_text": cb.translated_text,  # New field
                        "source_lang": tb.source_lang,
                        "target_lang": tb.target_lang,
                        "billed_characters": tb.billed_characters,
                    }
                    for tb, cb in zip(translated_blocks, customized_blocks)
                ],
                "total_cost": cached_translation.get("total_cost", 0) + total_cost,
                "total_blocks": len(customized_blocks),
                "tone": tone,
                "tone_cost": total_cost,
            }
            
            # Update cache with tone-customized blocks
            await cache.set_json(
                cache_key,
                tone_customized_data,
                expire_seconds=24 * 60 * 60,  # 24 hours
            )
            
            # Update translation record
            # After tone customization, move to reconstructing (or completed if no reconstruction needed)
            translation.status = TranslationStatus.RECONSTRUCTING
            translation.progress_percent = 90
            # Store tone information
            if tone in ['professional', 'casual', 'technical', 'creative']:
                translation.tone_preset = tone
            else:
                translation.custom_tone = tone
            translation.tone_cost = total_cost
            await db.commit()
            
            info(
                "Translation record updated with tone customization",
                job_id=job_id,
                status=TranslationStatus.RECONSTRUCTING.value,
                cost_usd=f"${total_cost:.6f}",
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "block_count": len(customized_blocks),
                "cost_usd": total_cost,
                "tone": tone,
            }
            
        finally:
            # Ensure Redis client is closed
            await redis.aclose()
        
    except Exception as e:
        log_error("Tone customization failed", exc=e, job_id=job_id)
        
        # Update translation status to failed
        try:
            translation = await db.get(Translation, UUID(job_id))
            if translation:
                translation.status = TranslationStatus.FAILED
                translation.error_message = f"Tone customization error: {str(e)}"
                await db.commit()
        except Exception:
            pass  # Best effort error recording
        
        raise

