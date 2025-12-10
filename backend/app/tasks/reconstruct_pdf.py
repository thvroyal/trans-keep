"""PDF Reconstruction Celery task"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.cache import Cache, CacheKeys, get_redis_client
from app.database import get_db
from app.logger import error as log_error, info
from app.models.translation import Translation, TranslationStatus
from app.s3 import S3Keys, download_file, upload_file
from app.services.pdf_reconstruction import PDFReconstructionService


@celery_app.task(
    name="reconstruct_pdf",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute delay between retries
    time_limit=900,  # 15 minutes max
)
def reconstruct_pdf_task(self, job_id: str) -> dict:
    """
    Celery task to reconstruct translated PDF and upload to S3.
    
    Args:
        job_id: Translation job ID
        
    Returns:
        dict with reconstruction results
    """
    import asyncio
    
    try:
        return asyncio.run(_reconstruct_pdf_async(job_id))
    except Exception as e:
        log_error("Reconstruct PDF task failed", exc=e, job_id=job_id)
        raise self.retry(exc=e)


async def _reconstruct_pdf_async(job_id: str) -> dict:
    """Async wrapper for reconstruction"""
    from app.database import get_async_session
    
    async with get_async_session() as db:
        return await reconstruct_pdf_sync(job_id, db)


async def reconstruct_pdf_sync(
    job_id: str,
    db: AsyncSession,
) -> dict:
    """
    Synchronous reconstruction function (can be called directly or from Celery).
    
    This function:
    1. Loads original PDF from S3
    2. Loads translated blocks from Redis cache
    3. Reconstructs PDF using PyMuPDF
    4. Uploads reconstructed PDF to S3
    5. Updates translation record with result path
    
    Args:
        job_id: Translation job ID
        db: Database session
        
    Returns:
        dict with reconstruction results
        
    Raises:
        Exception: If reconstruction fails
    """
    try:
        info("Starting PDF reconstruction", job_id=job_id)
        
        # Get translation record from database
        translation = await db.get(Translation, UUID(job_id))
        
        if not translation:
            log_error("Translation not found", job_id=job_id)
            raise ValueError(f"Translation {job_id} not found")
        
        # Update status to reconstructing
        translation.status = TranslationStatus.RECONSTRUCTING
        translation.progress_percent = 95  # Extraction + translation done, now reconstructing
        await db.commit()
        
        # Get Redis client for loading cached blocks
        redis = get_redis_client()
        cache = Cache(redis)
        
        try:
            # Load original PDF from S3
            info("Loading original PDF from S3", job_id=job_id)
            original_s3_key = S3Keys.upload_path(
                user_id=str(translation.user_id),
                job_id=job_id,
                filename=translation.file_name,
            )
            
            original_pdf_bytes = await download_file(original_s3_key)
            info(
                "Original PDF loaded",
                job_id=job_id,
                size_bytes=len(original_pdf_bytes),
            )
            
            # Load translated blocks from Redis cache
            cache_key = f"{CacheKeys.blocks(job_id)}_translated"
            cached_translation = await cache.get_json(cache_key)
            
            if not cached_translation:
                log_error("Translated blocks not found in cache", job_id=job_id)
                raise ValueError(f"No translated blocks found for job {job_id}")
            
            blocks = cached_translation.get("blocks", [])
            info(
                "Loaded translated blocks from cache",
                job_id=job_id,
                block_count=len(blocks),
            )
            
            # Reconstruct PDF with translated text
            info("Reconstructing PDF", job_id=job_id, block_count=len(blocks))
            reconstructed_pdf_bytes = PDFReconstructionService.reconstruct_pdf_with_tone(
                original_pdf_bytes=original_pdf_bytes,
                translated_blocks=blocks,
                use_tone=False,  # Tone customization handled in Story 3.2
            )
            
            info(
                "PDF reconstructed successfully",
                job_id=job_id,
                output_size=len(reconstructed_pdf_bytes),
            )
            
            # Upload reconstructed PDF to S3
            result_s3_key = S3Keys.result_path(
                user_id=str(translation.user_id),
                job_id=job_id,
                filename=translation.file_name,
            )
            
            info("Uploading reconstructed PDF to S3", job_id=job_id, s3_key=result_s3_key)
            uploaded_key = await upload_file(
                file_data=reconstructed_pdf_bytes,
                key=result_s3_key,
                content_type="application/pdf",
            )
            
            info(
                "Reconstructed PDF uploaded to S3",
                job_id=job_id,
                s3_key=uploaded_key,
            )
            
            # Update translation record
            translation.result_file_path = uploaded_key
            translation.status = TranslationStatus.COMPLETED
            translation.progress_percent = 100
            translation.completed_at = datetime.utcnow()
            await db.commit()
            
            info(
                "Translation record updated",
                job_id=job_id,
                status=TranslationStatus.COMPLETED.value,
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "uploaded_key": uploaded_key,
                "file_size": len(reconstructed_pdf_bytes),
            }
            
        finally:
            # Ensure Redis client is closed
            await redis.aclose()
        
    except Exception as e:
        log_error("Reconstruction failed", exc=e, job_id=job_id)
        
        # Update translation status to failed
        try:
            translation = await db.get(Translation, UUID(job_id))
            if translation:
                translation.status = TranslationStatus.FAILED
                translation.error_message = f"Reconstruction error: {str(e)}"
                await db.commit()
        except Exception:
            pass  # Best effort error recording
        
        raise
