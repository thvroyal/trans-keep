"""Download router for PDF download with user edits"""

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
from app.s3 import S3Keys, download_file, get_presigned_url, upload_file
from app.schemas.download import DownloadRequest, DownloadResponse
from app.services.pdf_reconstruction import PDFReconstructionService
from app.schemas.pdf import Block, Coordinates, TranslatedBlock

router = APIRouter(prefix="/api/v1", tags=["download"])


@router.post("/download/{job_id}", response_model=DownloadResponse)
async def download_translated_pdf(
    job_id: str,
    request: DownloadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DownloadResponse:
    """
    Download translated PDF with user edits applied.
    
    This endpoint:
    1. Verifies user owns the translation
    2. Loads original PDF from S3
    3. Loads translated blocks from Redis cache
    4. Applies user edits to translated blocks
    5. Reconstructs PDF with edited translations
    6. Uploads final PDF to S3
    7. Returns presigned download URL (valid for 1 hour)
    
    Args:
        job_id: Translation job ID (UUID)
        request: Download request with user edits
        db: Database session
        current_user: Authenticated user
        
    Returns:
        DownloadResponse with download URL and metadata
        
    Raises:
        404: Translation not found
        403: User doesn't own this translation
        400: Translation not complete or blocks not found
        500: PDF reconstruction or upload failed
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
    
    # Check translation is complete
    if translation.status != TranslationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation is not complete. Current status: {translation.status.value}",
        )
    
    info(
        "Download request received",
        job_id=job_id,
        user_id=str(current_user.id),
        edit_count=len(request.edits),
    )
    
    # Get Redis client
    redis = get_redis_client()
    cache = Cache(redis)
    
    try:
        # Load original PDF from S3
        original_s3_key = S3Keys.upload_path(
            user_id=str(translation.user_id),
            job_id=job_id,
            filename=translation.file_name,
        )
        
        info("Loading original PDF from S3", job_id=job_id, s3_key=original_s3_key)
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Translation blocks not found. Translation may not be complete.",
            )
        
        blocks_data = cached_translation.get("blocks", [])
        info(
            "Loaded translated blocks from cache",
            job_id=job_id,
            block_count=len(blocks_data),
        )
        
        # Apply user edits to blocks
        # Create a map of block_id -> edited text for quick lookup
        edits_map = {str(edit.block_id): edit.text for edit in request.edits}
        
        # Convert blocks to TranslatedBlock objects and apply edits
        translated_blocks: list[TranslatedBlock] = []
        for idx, block_data in enumerate(blocks_data):
            original_data = block_data.get("original", {})
            coords_data = original_data.get("coordinates", {})
            
            # Get translated text, preferring tone-customized if available
            translated_text = block_data.get("tone_customized_text") or block_data.get("translated_text", "")
            
            # Apply user edit if exists (edits override translated text)
            block_id_str = str(idx)  # Use index as block_id (matching frontend)
            if block_id_str in edits_map:
                translated_text = edits_map[block_id_str]
                info(
                    "Applied user edit to block",
                    job_id=job_id,
                    block_id=block_id_str,
                    original_text=translated_text[:50] if translated_text else "",
                    edited_text=edits_map[block_id_str][:50],
                )
            
            # Create Block object for original
            original_block = Block(
                page=original_data.get("page", 0),
                block_id=original_data.get("block_id", idx),
                text=original_data.get("text", ""),
                coordinates=Coordinates(
                    x=coords_data.get("x", 0),
                    y=coords_data.get("y", 0),
                    width=coords_data.get("width", 0),
                    height=coords_data.get("height", 0),
                ),
                font_size=original_data.get("font_size", 12),
                font_name=original_data.get("font_name", "helv"),
                is_bold=original_data.get("is_bold", False),
                is_italic=original_data.get("is_italic", False),
                rotation=original_data.get("rotation", 0),
            )
            
            # Create TranslatedBlock
            translated_block = TranslatedBlock(
                original=original_block,
                translated_text=translated_text,
            )
            translated_blocks.append(translated_block)
        
        info(
            "Prepared blocks for reconstruction",
            job_id=job_id,
            total_blocks=len(translated_blocks),
            edited_blocks=len(edits_map),
        )
        
        # Reconstruct PDF with edited translations
        info("Reconstructing PDF with user edits", job_id=job_id)
        reconstructed_pdf_bytes = PDFReconstructionService.reconstruct_pdf(
            original_pdf_bytes=original_pdf_bytes,
            translated_blocks=translated_blocks,
        )
        
        info(
            "PDF reconstructed successfully",
            job_id=job_id,
            output_size=len(reconstructed_pdf_bytes),
        )
        
        # Upload final PDF to S3 (use downloads path to distinguish from auto-reconstructed)
        download_s3_key = f"downloads/{translation.user_id}/{job_id}/{translation.file_name}"
        
        info("Uploading final PDF to S3", job_id=job_id, s3_key=download_s3_key)
        uploaded_key = await upload_file(
            file_data=reconstructed_pdf_bytes,
            key=download_s3_key,
            content_type="application/pdf",
        )
        
        info(
            "Final PDF uploaded to S3",
            job_id=job_id,
            s3_key=uploaded_key,
        )
        
        # Generate presigned URL (valid for 1 hour)
        download_url = get_presigned_url(
            key=uploaded_key,
            expires_in=3600,  # 1 hour
        )
        
        info(
            "Download URL generated",
            job_id=job_id,
            expires_in=3600,
        )
        
        return DownloadResponse(
            download_url=download_url,
            expires_at=None,  # Could calculate from expires_in if needed
            file_size=len(reconstructed_pdf_bytes),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Download failed", exc=e, job_id=job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download: {str(e)}",
        )
    finally:
        # Ensure Redis client is closed
        await redis.aclose()
