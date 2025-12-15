"""Tests for download endpoint"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.translation import Translation, TranslationStatus
from app.models.user import SubscriptionTier, User


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        google_id="test_google_id",
        email="test@example.com",
        name="Test User",
        subscription_tier=SubscriptionTier.FREE,
        usage_this_month=0,
    )


@pytest.fixture
def mock_translation(mock_user):
    """Create a mock translation"""
    job_id = uuid.uuid4()
    return Translation(
        id=job_id,
        tenant_id=mock_user.tenant_id,
        user_id=mock_user.id,
        file_name="test.pdf",
        file_size_bytes=1024,
        source_language="en",
        target_language="ja",
        status=TranslationStatus.COMPLETED,
        progress_percent=100,
        original_file_path=f"uploads/{mock_user.id}/{job_id}/test.pdf",
        result_file_path=f"results/{mock_user.id}/{job_id}/test.pdf",
    )


@pytest.fixture
def mock_translated_blocks():
    """Create mock translated blocks data"""
    return {
        "blocks": [
            {
                "original": {
                    "page": 0,
                    "block_id": 0,
                    "text": "Hello world",
                    "coordinates": {"x": 10, "y": 20, "width": 50, "height": 10},
                    "font_size": 12,
                    "font_name": "helv",
                    "is_bold": False,
                    "is_italic": False,
                    "rotation": 0,
                },
                "translated_text": "こんにちは世界",
                "tone_customized_text": None,
            },
            {
                "original": {
                    "page": 0,
                    "block_id": 1,
                    "text": "Test block",
                    "coordinates": {"x": 10, "y": 40, "width": 50, "height": 10},
                    "font_size": 12,
                    "font_name": "helv",
                    "is_bold": False,
                    "is_italic": False,
                    "rotation": 0,
                },
                "translated_text": "テストブロック",
                "tone_customized_text": None,
            },
        ],
    }


@pytest.fixture
def mock_pdf_bytes():
    """Create mock PDF bytes"""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF"


class TestDownloadEndpoint:
    """Test suite for download endpoint"""

    @pytest.mark.asyncio
    async def test_download_success(
        self,
        async_client: AsyncClient,
        mock_user: User,
        mock_translation: Translation,
        mock_translated_blocks: dict,
        mock_pdf_bytes: bytes,
    ):
        """Test successful PDF download with edits"""
        job_id = str(mock_translation.id)
        
        with patch("app.routers.download.get_current_user", return_value=mock_user), \
             patch("app.routers.download.get_db") as mock_db, \
             patch("app.routers.download.get_redis_client") as mock_redis, \
             patch("app.routers.download.download_file", new_callable=AsyncMock) as mock_download, \
             patch("app.routers.download.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.routers.download.get_presigned_url") as mock_presigned, \
             patch("app.routers.download.PDFReconstructionService.reconstruct_pdf") as mock_reconstruct:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_translation
            mock_session.execute.return_value = mock_result
            
            # Mock Redis
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_cache = AsyncMock()
            mock_cache.get_json = AsyncMock(return_value=mock_translated_blocks)
            mock_redis_client.aclose = AsyncMock()
            
            # Mock S3 operations
            mock_download.return_value = mock_pdf_bytes
            mock_upload.return_value = f"downloads/{mock_user.id}/{job_id}/test.pdf"
            mock_presigned.return_value = "https://s3.example.com/download.pdf"
            
            # Mock PDF reconstruction
            reconstructed_bytes = b"reconstructed_pdf_content"
            mock_reconstruct.return_value = reconstructed_bytes
            
            # Create cache mock
            with patch("app.routers.download.Cache", return_value=mock_cache):
                # Make request with edits
                response = await async_client.post(
                    f"/api/v1/download/{job_id}",
                    json={
                        "edits": [
                            {"block_id": 0, "text": "Edited text"},
                        ],
                    },
                    headers={"Authorization": f"Bearer test_token"},
                )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            
            assert "download_url" in result
            assert result["download_url"] == "https://s3.example.com/download.pdf"
            assert "file_size" in result
            assert result["file_size"] == len(reconstructed_bytes)
            
            # Verify S3 operations were called
            mock_download.assert_called_once()
            mock_upload.assert_called_once()
            mock_presigned.assert_called_once()
            mock_reconstruct.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_not_found(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test download with non-existent job ID"""
        job_id = str(uuid.uuid4())
        
        with patch("app.routers.download.get_current_user", return_value=mock_user), \
             patch("app.routers.download.get_db") as mock_db:
            
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query returning None
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            response = await async_client.post(
                f"/api/v1/download/{job_id}",
                json={"edits": []},
                headers={"Authorization": f"Bearer test_token"},
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_download_unauthorized(
        self,
        async_client: AsyncClient,
        mock_user: User,
        mock_translation: Translation,
    ):
        """Test download with unauthorized user"""
        job_id = str(mock_translation.id)
        
        # Create different user
        other_user = User(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            google_id="other_google_id",
            email="other@example.com",
            name="Other User",
            subscription_tier=SubscriptionTier.FREE,
            usage_this_month=0,
        )
        
        with patch("app.routers.download.get_current_user", return_value=other_user), \
             patch("app.routers.download.get_db") as mock_db:
            
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_translation
            mock_session.execute.return_value = mock_result
            
            response = await async_client.post(
                f"/api/v1/download/{job_id}",
                json={"edits": []},
                headers={"Authorization": f"Bearer test_token"},
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "permission" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_download_not_complete(
        self,
        async_client: AsyncClient,
        mock_user: User,
        mock_translation: Translation,
    ):
        """Test download when translation is not complete"""
        job_id = str(mock_translation.id)
        mock_translation.status = TranslationStatus.TRANSLATING
        
        with patch("app.routers.download.get_current_user", return_value=mock_user), \
             patch("app.routers.download.get_db") as mock_db:
            
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_translation
            mock_session.execute.return_value = mock_result
            
            response = await async_client.post(
                f"/api/v1/download/{job_id}",
                json={"edits": []},
                headers={"Authorization": f"Bearer test_token"},
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "not complete" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_download_no_blocks(
        self,
        async_client: AsyncClient,
        mock_user: User,
        mock_translation: Translation,
        mock_pdf_bytes: bytes,
    ):
        """Test download when blocks are not found in cache"""
        job_id = str(mock_translation.id)
        
        with patch("app.routers.download.get_current_user", return_value=mock_user), \
             patch("app.routers.download.get_db") as mock_db, \
             patch("app.routers.download.get_redis_client") as mock_redis, \
             patch("app.routers.download.download_file", new_callable=AsyncMock) as mock_download:
            
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_translation
            mock_session.execute.return_value = mock_result
            
            # Mock Redis
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_cache = AsyncMock()
            mock_cache.get_json = AsyncMock(return_value=None)  # No blocks found
            mock_redis_client.aclose = AsyncMock()
            
            # Mock S3 download
            mock_download.return_value = mock_pdf_bytes
            
            with patch("app.routers.download.Cache", return_value=mock_cache):
                response = await async_client.post(
                    f"/api/v1/download/{job_id}",
                    json={"edits": []},
                    headers={"Authorization": f"Bearer test_token"},
                )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "blocks not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_download_with_multiple_edits(
        self,
        async_client: AsyncClient,
        mock_user: User,
        mock_translation: Translation,
        mock_translated_blocks: dict,
        mock_pdf_bytes: bytes,
    ):
        """Test download with multiple user edits"""
        job_id = str(mock_translation.id)
        
        with patch("app.routers.download.get_current_user", return_value=mock_user), \
             patch("app.routers.download.get_db") as mock_db, \
             patch("app.routers.download.get_redis_client") as mock_redis, \
             patch("app.routers.download.download_file", new_callable=AsyncMock) as mock_download, \
             patch("app.routers.download.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.routers.download.get_presigned_url") as mock_presigned, \
             patch("app.routers.download.PDFReconstructionService.reconstruct_pdf") as mock_reconstruct:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Mock database query
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_translation
            mock_session.execute.return_value = mock_result
            
            # Mock Redis
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            mock_cache = AsyncMock()
            mock_cache.get_json = AsyncMock(return_value=mock_translated_blocks)
            mock_redis_client.aclose = AsyncMock()
            
            # Mock S3 operations
            mock_download.return_value = mock_pdf_bytes
            mock_upload.return_value = f"downloads/{mock_user.id}/{job_id}/test.pdf"
            mock_presigned.return_value = "https://s3.example.com/download.pdf"
            
            # Mock PDF reconstruction
            reconstructed_bytes = b"reconstructed_pdf_content"
            mock_reconstruct.return_value = reconstructed_bytes
            
            with patch("app.routers.download.Cache", return_value=mock_cache):
                # Make request with multiple edits
                response = await async_client.post(
                    f"/api/v1/download/{job_id}",
                    json={
                        "edits": [
                            {"block_id": 0, "text": "First edit"},
                            {"block_id": 1, "text": "Second edit"},
                        ],
                    },
                    headers={"Authorization": f"Bearer test_token"},
                )
            
            # Assertions
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            
            assert "download_url" in result
            assert result["file_size"] == len(reconstructed_bytes)
            
            # Verify reconstruction was called with edited blocks
            mock_reconstruct.assert_called_once()
            call_args = mock_reconstruct.call_args
            translated_blocks = call_args[1]["translated_blocks"]
            
            # Verify edits were applied
            assert translated_blocks[0].translated_text == "First edit"
            assert translated_blocks[1].translated_text == "Second edit"

    @pytest.mark.asyncio
    async def test_download_invalid_job_id(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test download with invalid job ID format"""
        with patch("app.routers.download.get_current_user", return_value=mock_user):
            response = await async_client.post(
                "/api/v1/download/invalid-uuid",
                json={"edits": []},
                headers={"Authorization": f"Bearer test_token"},
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "invalid" in response.json()["detail"].lower()
