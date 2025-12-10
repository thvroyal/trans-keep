"""PDF extraction Celery task"""

import tempfile
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.cache import get_redis_client
from app.database import get_db
from app.logger import error as log_error, info
from app.models.translation import Translation, TranslationStatus
from app.s3 import download_file
from app.services.pdf_service import PDFService


@celery_app.task(
    name="extract_pdf",
    bind=True,
    max_retries=3,
    default_retry_delay=30,  # 30 seconds delay between retries
    time_limit=600,  # 10 minutes max
)
def extract_pdf_task(self, job_id: str) -> dict:
    """
    Celery task to extract text from uploaded PDF.
    
    Args:
        job_id: Translation job ID
        
    Returns:
        dict with extraction results
    """
    import asyncio
    
    try:
        return asyncio.run(_extract_pdf_async(job_id))
    except Exception as e:
        log_error("Extract PDF task failed", exc=e, job_id=job_id)
        raise self.retry(exc=e)


async def _extract_pdf_async(job_id: str) -> dict:
    """Async wrapper for extraction"""
    from app.database import get_async_session
    
    async with get_async_session() as db:
        return await extract_pdf_sync(job_id, db)


async def extract_pdf_sync(
    job_id: str,
    db: AsyncSession,
) -> dict:
    """
    Synchronous PDF extraction function (can be called directly or from Celery).
    
    This function:
    1. Downloads PDF from S3
    2. Extracts text with layout
    3. Caches results in Redis
    4. Updates translation status in database
    5. Stores blocks in database (for reconstruction)
    
    Args:
        job_id: Translation job ID
        db: Database session
        
    Returns:
        dict with extraction results
        
    Raises:
        Exception: If extraction fails
    """
    try:
        info("Starting PDF extraction", job_id=job_id)
        
        # Get translation record from database
        translation = await db.get(Translation, UUID(job_id))
        
        if not translation:
            log_error("Translation not found", job_id=job_id)
            raise ValueError(f"Translation {job_id} not found")
        
        # Update status to extracting
        translation.status = TranslationStatus.EXTRACTING
        translation.progress_percent = 10
        await db.commit()
        
        # Get Redis client for caching
        redis = get_redis_client()
        
        try:
            # Download PDF from S3 to temp file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
                info("Downloading PDF from S3", job_id=job_id, s3_key=translation.original_file_path)
                pdf_data = await download_file(translation.original_file_path)
                tmp_file.write(pdf_data)
            
            # Update progress
            translation.progress_percent = 30
            await db.commit()
            await PDFService.update_extraction_progress(
                redis=redis,
                job_id=job_id,
                current_page=0,
                total_pages=PDFService.get_page_count(tmp_path),
            )
            
            # Extract text with layout (with caching)
            info("Extracting PDF text", job_id=job_id)
            result = await PDFService.extract_text_with_layout_cached(
                pdf_path=tmp_path,
                translation_id=job_id,
                redis=redis,
            )
            
            # Update progress
            translation.progress_percent = 80
            await db.commit()
            
            # Check if PDF is scanned
            if result.is_scanned:
                info("Scanned PDF detected", job_id=job_id)
                translation.status = TranslationStatus.FAILED
                translation.error_message = "This PDF appears to be scanned (image-based). OCR support coming in Phase 2."
                await db.commit()
                
                return {
                    "success": False,
                    "error": "scanned_pdf",
                    "message": "PDF is scanned and requires OCR",
                }
            
            # Store metadata in translation record
            # Note: Actual block storage will be implemented when needed
            # For now, blocks are cached in Redis
            translation.progress_percent = 90
            await db.commit()
            
            info(
                "PDF extraction complete",
                job_id=job_id,
                blocks=len(result.blocks),
                pages=result.page_count,
                time_ms=result.extraction_time_ms,
            )
            
            # Mark extraction complete (ready for translation)
            translation.progress_percent = 100
            translation.status = TranslationStatus.TRANSLATING  # Move to next stage
            await db.commit()
            
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            
            return {
                "success": True,
                "blocks": len(result.blocks),
                "pages": result.page_count,
                "characters": result.total_characters,
                "extraction_time_ms": result.extraction_time_ms,
            }
            
        finally:
            # Ensure Redis client is closed
            await redis.aclose()
        
    except Exception as e:
        log_error("PDF extraction failed", exc=e, job_id=job_id)
        
        # Update translation status to failed
        try:
            translation = await db.get(Translation, UUID(job_id))
            if translation:
                translation.status = TranslationStatus.FAILED
                translation.error_message = str(e)
                await db.commit()
        except Exception:
            pass  # Best effort error recording
        
        raise
