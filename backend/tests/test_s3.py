"""S3/MinIO integration tests for TransKeep"""

import os

import pytest
import pytest_asyncio
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.s3 import (
    DEFAULT_BUCKET,
    S3Keys,
    create_bucket_if_not_exists,
    delete_file,
    download_file,
    file_exists,
    get_presigned_download_url,
    get_presigned_url,
    s3_client,
    upload_file,
)

# Test configuration
TEST_BUCKET = os.getenv("TEST_S3_BUCKET", "transkeep-test")


@pytest_asyncio.fixture
async def test_bucket():
    """Create test bucket and clean up after tests"""
    try:
        s3_client.create_bucket(Bucket=TEST_BUCKET)
    except ClientError as e:
        if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
            raise

    yield TEST_BUCKET

    # Cleanup: delete all objects and bucket
    try:
        # List and delete all objects
        response = s3_client.list_objects_v2(Bucket=TEST_BUCKET)
        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=TEST_BUCKET, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=TEST_BUCKET)
    except ClientError:
        pass  # Bucket might already be deleted


class TestS3Connection:
    """Test S3/MinIO connectivity"""

    @pytest.mark.asyncio
    async def test_bucket_creation(self, test_bucket: str):
        """Test that bucket can be created"""
        response = s3_client.head_bucket(Bucket=test_bucket)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @pytest.mark.asyncio
    async def test_create_bucket_if_not_exists(self):
        """Test create_bucket_if_not_exists utility"""
        result = await create_bucket_if_not_exists(DEFAULT_BUCKET)
        assert result is True


class TestFileOperations:
    """Test S3 file operations"""

    @pytest.mark.asyncio
    async def test_upload_file_bytes(self, test_bucket: str):
        """Test uploading file as bytes"""
        content = b"Hello, World! This is a test file."
        key = "test/upload_bytes.txt"

        result = await upload_file(
            content,
            key,
            bucket=test_bucket,
            content_type="text/plain",
        )
        assert result == key

        # Verify file exists
        response = s3_client.head_object(Bucket=test_bucket, Key=key)
        assert response["ContentLength"] == len(content)

    @pytest.mark.asyncio
    async def test_download_file(self, test_bucket: str):
        """Test downloading a file"""
        content = b"Download test content"
        key = "test/download.txt"

        # Upload first
        await upload_file(content, key, bucket=test_bucket)

        # Download
        downloaded = await download_file(key, bucket=test_bucket)
        assert downloaded == content

    @pytest.mark.asyncio
    async def test_delete_file(self, test_bucket: str):
        """Test deleting a file"""
        content = b"Delete me"
        key = "test/delete.txt"

        # Upload
        await upload_file(content, key, bucket=test_bucket)
        assert await file_exists(key, bucket=test_bucket) is True

        # Delete
        result = await delete_file(key, bucket=test_bucket)
        assert result is True
        assert await file_exists(key, bucket=test_bucket) is False

    @pytest.mark.asyncio
    async def test_file_exists(self, test_bucket: str):
        """Test file existence check"""
        key = "test/exists.txt"

        # Should not exist initially
        assert await file_exists(key, bucket=test_bucket) is False

        # Upload
        await upload_file(b"exists", key, bucket=test_bucket)

        # Should exist now
        assert await file_exists(key, bucket=test_bucket) is True

    @pytest.mark.asyncio
    async def test_download_nonexistent_file(self, test_bucket: str):
        """Test downloading a file that doesn't exist"""
        with pytest.raises(ClientError) as exc_info:
            await download_file("nonexistent/file.txt", bucket=test_bucket)
        assert exc_info.value.response["Error"]["Code"] in ["NoSuchKey", "404"]


class TestPresignedUrls:
    """Test presigned URL generation"""

    @pytest.mark.asyncio
    async def test_presigned_url_generation(self, test_bucket: str):
        """Test generating presigned URL for download"""
        content = b"Presigned URL test"
        key = "test/presigned.txt"

        await upload_file(content, key, bucket=test_bucket)

        url = get_presigned_url(key, bucket=test_bucket, expires_in=3600)
        assert url is not None
        assert key in url
        assert "X-Amz-Signature" in url or "Signature" in url

    @pytest.mark.asyncio
    async def test_presigned_download_url_with_filename(self, test_bucket: str):
        """Test presigned URL with custom filename"""
        content = b"Download with filename"
        key = "test/original.txt"

        await upload_file(content, key, bucket=test_bucket)

        url = get_presigned_download_url(
            key,
            bucket=test_bucket,
            filename="custom_name.txt",
        )
        assert url is not None
        assert "custom_name.txt" in url or "response-content-disposition" in url.lower()

    @pytest.mark.asyncio
    async def test_presigned_url_expiration(self, test_bucket: str):
        """Test presigned URL with custom expiration"""
        content = b"Expiration test"
        key = "test/expire.txt"

        await upload_file(content, key, bucket=test_bucket)

        # Short expiration
        url = get_presigned_url(key, bucket=test_bucket, expires_in=60)
        assert url is not None
        assert "X-Amz-Expires=60" in url or "Expires" in url


class TestS3Keys:
    """Test S3Keys helper class"""

    def test_upload_path(self):
        """Test upload path generation"""
        path = S3Keys.upload_path(
            user_id="user-123",
            job_id="job-456",
            filename="document.pdf",
        )
        assert path == "uploads/user-123/job-456/document.pdf"

    def test_result_path(self):
        """Test result path generation"""
        path = S3Keys.result_path(
            user_id="user-123",
            job_id="job-456",
            filename="translated.pdf",
        )
        assert path == "results/user-123/job-456/translated.pdf"


class TestLargeFiles:
    """Test handling of larger files"""

    @pytest.mark.asyncio
    async def test_upload_1mb_file(self, test_bucket: str):
        """Test uploading a 1MB file"""
        content = b"x" * (1024 * 1024)  # 1MB
        key = "test/large_1mb.bin"

        result = await upload_file(
            content,
            key,
            bucket=test_bucket,
            content_type="application/octet-stream",
        )
        assert result == key

        # Verify size
        response = s3_client.head_object(Bucket=test_bucket, Key=key)
        assert response["ContentLength"] == 1024 * 1024

    @pytest.mark.asyncio
    async def test_download_1mb_file(self, test_bucket: str):
        """Test downloading a 1MB file"""
        content = b"y" * (1024 * 1024)  # 1MB
        key = "test/download_1mb.bin"

        await upload_file(content, key, bucket=test_bucket)
        downloaded = await download_file(key, bucket=test_bucket)

        assert len(downloaded) == 1024 * 1024
        assert downloaded == content


class TestContentTypes:
    """Test different content types"""

    @pytest.mark.asyncio
    async def test_upload_pdf(self, test_bucket: str):
        """Test uploading with PDF content type"""
        # Minimal PDF header
        content = b"%PDF-1.4 test content"
        key = "test/document.pdf"

        await upload_file(
            content,
            key,
            bucket=test_bucket,
            content_type="application/pdf",
        )

        response = s3_client.head_object(Bucket=test_bucket, Key=key)
        assert response["ContentType"] == "application/pdf"

    @pytest.mark.asyncio
    async def test_upload_json(self, test_bucket: str):
        """Test uploading with JSON content type"""
        import json

        content = json.dumps({"test": "data"}).encode()
        key = "test/data.json"

        await upload_file(
            content,
            key,
            bucket=test_bucket,
            content_type="application/json",
        )

        response = s3_client.head_object(Bucket=test_bucket, Key=key)
        assert response["ContentType"] == "application/json"

