"""Tests for PDF reconstruction service and Celery task"""

import io
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import fitz
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import Cache, CacheKeys
from app.models.translation import Translation, TranslationStatus
from app.services.pdf_reconstruction import PDFReconstructionService
from app.tasks.reconstruct_pdf import reconstruct_pdf_sync
from app.schemas.pdf import Block, Coordinates, TranslatedBlock


class TestPDFReconstructionService:
    """Tests for PDF reconstruction service"""

    @pytest.fixture
    def simple_pdf_bytes(self) -> bytes:
        """Create a simple test PDF"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Original English Text")
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return output.getvalue()

    @pytest.fixture
    def translated_blocks(self) -> list:
        """Create sample translated blocks"""
        coords = Coordinates(x=0.1, y=0.1, width=0.8, height=0.1)
        original = Block(
            page=1,
            block_id="block_1",
            text="Original English Text",
            coordinates=coords,
            font_size=12,
            font_name="helv",
            is_bold=False,
            is_italic=False,
            rotation=0,
        )
        
        block = TranslatedBlock(
            original=original,
            translated_text="翻译的日文文本",
            source_lang="en",
            target_lang="ja",
            billed_characters=10,
        )
        return [block]

    def test_reconstruct_pdf_success(self, simple_pdf_bytes, translated_blocks):
        """Test successful PDF reconstruction"""
        result = PDFReconstructionService.reconstruct_pdf(
            original_pdf_bytes=simple_pdf_bytes,
            translated_blocks=translated_blocks,
        )
        
        # Verify output is valid PDF
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Verify it's a valid PDF by trying to open it
        reconstructed_doc = fitz.open(stream=result, filetype="pdf")
        assert reconstructed_doc.page_count >= 1
        reconstructed_doc.close()

    def test_reconstruct_pdf_with_invalid_pdf_raises_error(self, translated_blocks):
        """Test reconstruction with corrupted PDF raises ValueError"""
        invalid_pdf = b"This is not a PDF"
        
        with pytest.raises(ValueError, match="Invalid PDF"):
            PDFReconstructionService.reconstruct_pdf(
                original_pdf_bytes=invalid_pdf,
                translated_blocks=translated_blocks,
            )

    def test_reconstruct_pdf_with_tone_selects_tone_text(self, simple_pdf_bytes):
        """Test reconstruction selects tone-customized text when available"""
        blocks_with_tone = [
            {
                "original": {
                    "page": 1,
                    "block_id": "block_1",
                    "text": "Original",
                    "coordinates": {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.1},
                    "font_size": 12,
                    "font_name": "helv",
                    "is_bold": False,
                    "is_italic": False,
                },
                "translated_text": "翻訳されたテキスト",
                "tone_customized_text": "丁寧なトーンのテキスト",
                "source_lang": "en",
                "target_lang": "ja",
                "billed_characters": 10,
            }
        ]
        
        result = PDFReconstructionService.reconstruct_pdf_with_tone(
            original_pdf_bytes=simple_pdf_bytes,
            translated_blocks=blocks_with_tone,
            use_tone=True,
        )
        
        # Verify it's a valid PDF
        assert isinstance(result, bytes)
        reconstructed_doc = fitz.open(stream=result, filetype="pdf")
        assert reconstructed_doc.page_count >= 1
        reconstructed_doc.close()

    def test_reconstruct_pdf_with_tone_fallback_to_translated(self, simple_pdf_bytes):
        """Test reconstruction falls back to translated_text when tone not available"""
        blocks_without_tone = [
            {
                "original": {
                    "page": 1,
                    "block_id": "block_1",
                    "text": "Original",
                    "coordinates": {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.1},
                    "font_size": 12,
                    "font_name": "helv",
                    "is_bold": False,
                    "is_italic": False,
                },
                "translated_text": "翻訳されたテキスト",
                "source_lang": "en",
                "target_lang": "ja",
                "billed_characters": 10,
            }
        ]
        
        result = PDFReconstructionService.reconstruct_pdf_with_tone(
            original_pdf_bytes=simple_pdf_bytes,
            translated_blocks=blocks_without_tone,
            use_tone=True,
        )
        
        # Verify it's a valid PDF
        assert isinstance(result, bytes)
        reconstructed_doc = fitz.open(stream=result, filetype="pdf")
        assert reconstructed_doc.page_count >= 1
        reconstructed_doc.close()


class TestReconstructPDFTask:
    """Tests for reconstruct_pdf Celery task"""

    @pytest.fixture
    def mock_translation(self) -> Translation:
        """Create mock Translation model"""
        trans = Translation(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            file_name="test.pdf",
            file_size_bytes=1024,
            source_language="en",
            target_language="ja",
            status=TranslationStatus.TRANSLATING,
            progress_percent=90,
            original_file_path="uploads/user123/job456/test.pdf",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return trans

    @pytest.fixture
    def cached_translated_blocks(self) -> dict:
        """Sample cached translated blocks from Redis"""
        return {
            "blocks": [
                {
                    "original": {
                        "page": 1,
                        "block_id": "block_1",
                        "text": "Original English",
                        "coordinates": {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.1},
                        "font_size": 12,
                        "font_name": "helv",
                        "is_bold": False,
                        "is_italic": False,
                    },
                    "translated_text": "翻訳されたテキスト",
                    "source_lang": "en",
                    "target_lang": "ja",
                    "billed_characters": 15,
                }
            ],
            "total_cost": 0.0015,
            "total_blocks": 1,
        }

    @pytest.mark.asyncio
    async def test_reconstruct_pdf_sync_success(
        self,
        mock_translation,
        cached_translated_blocks,
    ):
        """Test successful reconstruction task execution"""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.get = AsyncMock(return_value=mock_translation)
        mock_db.commit = AsyncMock()

        # Create simple PDF bytes
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Original English Text")
        pdf_bytes = io.BytesIO()
        doc.save(pdf_bytes)
        pdf_bytes.seek(0)

        with patch("app.tasks.reconstruct_pdf.get_redis_client") as mock_redis, \
             patch("app.tasks.reconstruct_pdf.download_file", new_callable=AsyncMock) as mock_download, \
             patch("app.tasks.reconstruct_pdf.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.tasks.reconstruct_pdf.Cache") as mock_cache_class:

            # Setup mocks
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_redis_client.aclose = AsyncMock()

            mock_download.return_value = pdf_bytes.getvalue()
            mock_upload.return_value = "results/user123/job456/test.pdf"

            mock_cache_instance = AsyncMock()
            mock_cache_class.return_value = mock_cache_instance
            cache_key = f"{CacheKeys.blocks(str(mock_translation.id))}_translated"
            mock_cache_instance.get_json = AsyncMock(
                return_value=cached_translated_blocks
            )

            # Execute
            result = await reconstruct_pdf_sync(str(mock_translation.id), mock_db)

            # Verify
            assert result["success"] is True
            assert result["job_id"] == str(mock_translation.id)
            assert result["uploaded_key"] == "results/user123/job456/test.pdf"
            assert result["file_size"] > 0

            # Verify database was updated
            assert mock_translation.status == TranslationStatus.COMPLETED
            assert mock_translation.result_file_path == "results/user123/job456/test.pdf"
            assert mock_translation.progress_percent == 100
            mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_reconstruct_pdf_sync_missing_translation(self):
        """Test reconstruction with missing translation record"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.get = AsyncMock(return_value=None)

        job_id = str(uuid.uuid4())

        with pytest.raises(ValueError, match="Translation .* not found"):
            await reconstruct_pdf_sync(job_id, mock_db)

    @pytest.mark.asyncio
    async def test_reconstruct_pdf_sync_missing_blocks_in_cache(
        self,
        mock_translation,
    ):
        """Test reconstruction fails gracefully when blocks not in cache"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.get = AsyncMock(return_value=mock_translation)
        mock_db.commit = AsyncMock()

        # Create simple PDF bytes
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Original English Text")
        pdf_bytes = io.BytesIO()
        doc.save(pdf_bytes)
        pdf_bytes.seek(0)

        with patch("app.tasks.reconstruct_pdf.get_redis_client") as mock_redis, \
             patch("app.tasks.reconstruct_pdf.download_file", new_callable=AsyncMock) as mock_download, \
             patch("app.tasks.reconstruct_pdf.Cache") as mock_cache_class:

            # Setup mocks - cache returns None (blocks not found)
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_redis_client.aclose = AsyncMock()

            mock_download.return_value = pdf_bytes.getvalue()

            mock_cache_instance = AsyncMock()
            mock_cache_class.return_value = mock_cache_instance
            mock_cache_instance.get_json = AsyncMock(return_value=None)

            # Execute - should raise error
            with pytest.raises(ValueError, match="No translated blocks found"):
                await reconstruct_pdf_sync(str(mock_translation.id), mock_db)

            # Verify job marked as failed
            assert mock_translation.status == TranslationStatus.FAILED
            assert "Reconstruction error" in mock_translation.error_message


class TestReconstructionIntegration:
    """Integration tests for full pipeline with reconstruction"""

    def test_multipage_pdf_reconstruction(self):
        """Test reconstruction works for multi-page PDFs"""
        # Create a 5-page PDF
        doc = fitz.open()
        for i in range(5):
            page = doc.new_page()
            page.insert_text((50, 50 + i*50), f"Page {i+1} Text")
        
        pdf_bytes = io.BytesIO()
        doc.save(pdf_bytes)
        pdf_bytes.seek(0)

        # Create blocks for some pages
        blocks = []
        for page_num in [1, 2, 5]:
            coords = Coordinates(x=0.1, y=0.1, width=0.8, height=0.1)
            original = Block(
                page=page_num,
                block_id=f"block_{page_num}",
                text=f"Page {page_num} Text",
                coordinates=coords,
                font_size=12,
                font_name="helv",
                is_bold=False,
                is_italic=False,
                rotation=0,
            )
            
            block = TranslatedBlock(
                original=original,
                translated_text=f"ページ{page_num}のテキスト",
                source_lang="en",
                target_lang="ja",
                billed_characters=20,
            )
            blocks.append(block)

        # Reconstruct
        result = PDFReconstructionService.reconstruct_pdf(
            original_pdf_bytes=pdf_bytes.getvalue(),
            translated_blocks=blocks,
        )

        # Verify
        assert isinstance(result, bytes)
        reconstructed = fitz.open(stream=result, filetype="pdf")
        assert reconstructed.page_count == 5
        reconstructed.close()

    def test_large_pdf_reconstruction_performance(self):
        """Test reconstruction performance with larger PDF (100+ pages)"""
        # Create a 50-page PDF (reasonable size for performance test)
        doc = fitz.open()
        for i in range(50):
            page = doc.new_page()
            page.insert_text((50, 50), f"Page {i+1}")
        
        pdf_bytes = io.BytesIO()
        doc.save(pdf_bytes)
        pdf_bytes.seek(0)
        original_size = len(pdf_bytes.getvalue())

        # Create blocks for every 10th page
        blocks = []
        for page_num in range(1, 51, 10):
            coords = Coordinates(x=0.1, y=0.1, width=0.8, height=0.1)
            original = Block(
                page=page_num,
                block_id=f"block_{page_num}",
                text=f"Page {page_num}",
                coordinates=coords,
                font_size=12,
                font_name="helv",
                is_bold=False,
                is_italic=False,
                rotation=0,
            )
            
            block = TranslatedBlock(
                original=original,
                translated_text=f"ページ{page_num}",
                source_lang="en",
                target_lang="ja",
                billed_characters=10,
            )
            blocks.append(block)

        import time
        start_time = time.time()
        
        result = PDFReconstructionService.reconstruct_pdf(
            original_pdf_bytes=pdf_bytes.getvalue(),
            translated_blocks=blocks,
        )
        
        elapsed = time.time() - start_time

        # Verify result
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Performance check: should complete in reasonable time (< 10 seconds for 50 pages)
        assert elapsed < 10.0, f"Reconstruction took {elapsed:.2f}s, expected < 10s"
