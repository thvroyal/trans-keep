"""Orchestrator for translation pipeline

Chains together: upload → extract → translate → complete
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.database import get_async_session
from app.logger import error as log_error, info
from app.models.translation import Translation, TranslationStatus
from app.tasks.extract_pdf import extract_pdf_sync
from app.tasks.translate_blocks import translate_blocks_sync


@celery_app.task(
    name="process_translation_pipeline",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute delay between retries
)
def process_translation_pipeline(self, job_id: str) -> dict:
    """
    Main orchestrator task for the translation pipeline.
    
    This task coordinates the entire translation workflow:
    1. Extract text from PDF (with layout preservation)
    2. Translate extracted blocks using DeepL
    3. Update job status and mark complete
    
    Note: This is a synchronous Celery task that calls async functions.
    We use asyncio.run() to bridge sync/async.
    
    Args:
        job_id: Translation job ID (UUID as string)
        
    Returns:
        dict with pipeline results
        
    Raises:
        Exception: If any step fails (will trigger retry)
    """
    import asyncio
    
    try:
        info("Starting translation pipeline", job_id=job_id)
        
        # Run the async pipeline
        result = asyncio.run(_run_pipeline_async(job_id))
        
        info("Translation pipeline complete", job_id=job_id, result=result)
        return result
        
    except Exception as e:
        log_error("Translation pipeline failed", exc=e, job_id=job_id)
        
        # Update job status to failed
        try:
            asyncio.run(_mark_job_failed(job_id, str(e)))
        except Exception:
            pass  # Best effort
        
        # Retry the task (if retries remaining)
        raise self.retry(exc=e)


async def _run_pipeline_async(job_id: str) -> dict:
    """
    Run the full translation pipeline asynchronously.
    
    Args:
        job_id: Translation job ID
        
    Returns:
        dict with pipeline results
    """
    # Get database session
    async with get_async_session() as db:
        # Step 1: Extract PDF
        info("Pipeline step 1: Extracting PDF", job_id=job_id)
        extraction_result = await extract_pdf_sync(job_id, db)
        
        if not extraction_result["success"]:
            raise Exception(f"Extraction failed: {extraction_result.get('error', 'Unknown error')}")
        
        # Step 2: Translate blocks
        info("Pipeline step 2: Translating blocks", job_id=job_id)
        translation_result = await translate_blocks_sync(job_id, db)
        
        if not translation_result["success"]:
            raise Exception(f"Translation failed: {translation_result.get('error', 'Unknown error')}")
        
        # Pipeline complete
        info(
            "Pipeline complete",
            job_id=job_id,
            blocks_extracted=extraction_result.get("blocks", 0),
            blocks_translated=translation_result.get("translated_blocks", 0),
            cost_usd=translation_result.get("cost_usd", 0),
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "extraction": extraction_result,
            "translation": translation_result,
        }


async def _mark_job_failed(job_id: str, error_message: str) -> None:
    """
    Mark a job as failed in the database.
    
    Args:
        job_id: Translation job ID
        error_message: Error description
    """
    async with get_async_session() as db:
        try:
            translation = await db.get(Translation, UUID(job_id))
            if translation:
                translation.status = TranslationStatus.FAILED
                translation.error_message = f"Pipeline failed: {error_message}"
                await db.commit()
        except Exception as e:
            log_error("Failed to mark job as failed", exc=e, job_id=job_id)


# Convenience function to trigger the pipeline from the upload endpoint
def trigger_translation_pipeline(job_id: str) -> str:
    """
    Trigger the translation pipeline for a newly uploaded file.
    
    This should be called from the upload endpoint after file is stored in S3.
    
    Args:
        job_id: Translation job ID
        
    Returns:
        Celery task ID
    """
    task = process_translation_pipeline.delay(job_id)
    info("Translation pipeline triggered", job_id=job_id, task_id=task.id)
    return task.id
