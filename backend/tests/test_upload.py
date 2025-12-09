"""Tests for upload endpoint"""

import io
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
def valid_pdf_file():
    """Create a mock PDF file"""
    # Minimal valid PDF
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF"
    return io.BytesIO(pdf_content)


@pytest.fixture
def large_pdf_file():
    """Create a mock large PDF file (>100MB)"""
    # Create a file larger than 100MB
    size = 101 * 1024 * 1024  # 101MB
    return io.BytesIO(b"x" * size)


class TestUploadEndpoint:
    """Test suite for file upload endpoint"""

    @pytest.mark.asyncio
    async def test_upload_success(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test successful file upload"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user), \
             patch("app.routers.upload.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.routers.upload.get_db") as mock_db:
            
            # Setup mocks
            mock_upload.return_value = "uploads/test/file.pdf"
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Prepare file upload
            files = {
                "file": ("test.pdf", valid_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
                "source_language": "en",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            
            assert "job_id" in result
            assert result["status"] == "pending"
            assert result["file_name"] == "test.pdf"
            assert result["message"] == "File uploaded successfully. Translation will begin shortly."
            
            # Verify S3 upload was called
            mock_upload.assert_called_once()
            
            # Verify database record was created
            mock_session.add.assert_called_once()
            mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test upload with invalid file type"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user):
            # Prepare non-PDF file
            files = {
                "file": ("test.txt", io.BytesIO(b"text content"), "text/plain")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid file type" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_file_too_large(
        self,
        async_client: AsyncClient,
        mock_user: User,
        large_pdf_file: io.BytesIO,
    ):
        """Test upload with file exceeding size limit"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user):
            # Prepare large file
            files = {
                "file": ("large.pdf", large_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            assert "File too large" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_empty_file(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test upload with empty file"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user):
            # Prepare empty file
            files = {
                "file": ("empty.pdf", io.BytesIO(b""), "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "File is empty" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_missing_target_language(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test upload without target language"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user):
            # Prepare file without target language
            files = {
                "file": ("test.pdf", valid_pdf_file, "application/pdf")
            }
            data = {}
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_upload_without_authentication(
        self,
        async_client: AsyncClient,
        valid_pdf_file: io.BytesIO,
    ):
        """Test upload without authentication token"""
        # Prepare file
        files = {
            "file": ("test.pdf", valid_pdf_file, "application/pdf")
        }
        data = {
            "target_language": "ja",
        }
        
        # Make request without auth
        response = await async_client.post(
            "/api/v1/upload",
            files=files,
            data=data,
        )
        
        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_upload_s3_failure(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test upload when S3 upload fails"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user), \
             patch("app.routers.upload.upload_file", new_callable=AsyncMock) as mock_upload:
            
            # Setup mock to raise exception
            mock_upload.side_effect = Exception("S3 error")
            
            # Prepare file
            files = {
                "file": ("test.pdf", valid_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to upload file to storage" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_sanitizes_filename(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test that unsafe filenames are sanitized"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user), \
             patch("app.routers.upload.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.routers.upload.get_db") as mock_db:
            
            # Setup mocks
            mock_upload.return_value = "uploads/test/file.pdf"
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Prepare file with unsafe name
            files = {
                "file": ("../../../etc/passwd.pdf", valid_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            
            # Filename should be sanitized (no path traversal)
            assert "../" not in result["file_name"]
            assert "etc" not in result["file_name"]
            assert result["file_name"].endswith(".pdf")

    @pytest.mark.asyncio
    async def test_upload_creates_correct_s3_key(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test that S3 key follows correct format"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user), \
             patch("app.routers.upload.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("app.routers.upload.get_db") as mock_db:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Prepare file
            files = {
                "file": ("test.pdf", valid_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_201_CREATED
            
            # Verify S3 key format: uploads/{user_id}/{job_id}/{filename}
            call_args = mock_upload.call_args
            s3_key = call_args.kwargs["key"]
            
            assert s3_key.startswith("uploads/")
            assert str(mock_user.id) in s3_key
            assert "test.pdf" in s3_key

    @pytest.mark.asyncio
    async def test_upload_auto_detect_source_language(
        self,
        async_client: AsyncClient,
        mock_user: User,
        valid_pdf_file: io.BytesIO,
    ):
        """Test upload with auto-detect source language"""
        with patch("app.routers.upload.get_current_user", return_value=mock_user), \
             patch("app.routers.upload.upload_file", new_callable=AsyncMock), \
             patch("app.routers.upload.get_db") as mock_db:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_db.return_value = mock_session
            
            # Prepare file without source language (defaults to 'auto')
            files = {
                "file": ("test.pdf", valid_pdf_file, "application/pdf")
            }
            data = {
                "target_language": "ja",
            }
            
            # Make request
            response = await async_client.post(
                "/api/v1/upload",
                files=files,
                data=data,
            )
            
            # Assertions
            assert response.status_code == status.HTTP_201_CREATED
            
            # Verify database record has source_language='auto'
            add_call = mock_session.add.call_args[0][0]
            assert add_call.source_language == "auto"


class TestFilenameStrReplace:
    """Test filename sanitization function"""

    def test_sanitize_normal_filename(self):
        """Test sanitization of normal filename"""
        from app.routers.upload import sanitize_filename
        
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"

    def test_sanitize_path_traversal(self):
        """Test sanitization removes path traversal"""
        from app.routers.upload import sanitize_filename
        
        result = sanitize_filename("../../../etc/passwd.pdf")
        assert "../" not in result
        assert "etc" not in result or "_" in result

    def test_sanitize_special_characters(self):
        """Test sanitization replaces special characters"""
        from app.routers.upload import sanitize_filename
        
        result = sanitize_filename("my@document#2024$.pdf")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_sanitize_adds_pdf_extension(self):
        """Test sanitization adds .pdf if missing"""
        from app.routers.upload import sanitize_filename
        
        result = sanitize_filename("document")
        assert result.endswith(".pdf")

    def test_sanitize_length_limit(self):
        """Test sanitization limits filename length"""
        from app.routers.upload import sanitize_filename
        
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
