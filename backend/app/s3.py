"""S3/MinIO file storage utilities"""

import io
from typing import BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import get_settings

settings = get_settings()

# Configure boto3 client
_s3_config = Config(
    signature_version="s3v4",
    retries={"max_attempts": 3, "mode": "standard"},
)

# Create S3 client (works with both AWS S3 and MinIO)
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,  # None for real AWS S3
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
    config=_s3_config,
)

# Default bucket name
DEFAULT_BUCKET = settings.aws_bucket_name


async def upload_file(
    file_data: bytes | BinaryIO,
    key: str,
    bucket: str = DEFAULT_BUCKET,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to S3/MinIO.
    
    Args:
        file_data: File content as bytes or file-like object
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        content_type: MIME type of the file
        
    Returns:
        The S3 key of the uploaded file
        
    Raises:
        ClientError: If upload fails
    """
    if isinstance(file_data, bytes):
        file_data = io.BytesIO(file_data)

    s3_client.upload_fileobj(
        file_data,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return key


async def download_file(
    key: str,
    bucket: str = DEFAULT_BUCKET,
) -> bytes:
    """
    Download a file from S3/MinIO.
    
    Args:
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        
    Returns:
        File content as bytes
        
    Raises:
        ClientError: If download fails or file not found
    """
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


async def delete_file(
    key: str,
    bucket: str = DEFAULT_BUCKET,
) -> bool:
    """
    Delete a file from S3/MinIO.
    
    Args:
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        
    Returns:
        True if deleted successfully
        
    Raises:
        ClientError: If deletion fails
    """
    s3_client.delete_object(Bucket=bucket, Key=key)
    return True


async def file_exists(
    key: str,
    bucket: str = DEFAULT_BUCKET,
) -> bool:
    """
    Check if a file exists in S3/MinIO.
    
    Args:
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        
    Returns:
        True if file exists, False otherwise
    """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def get_presigned_url(
    key: str,
    bucket: str = DEFAULT_BUCKET,
    expires_in: int = 3600,
    method: str = "get_object",
) -> str:
    """
    Generate a presigned URL for temporary access.
    
    Args:
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        expires_in: URL expiration time in seconds (default 1 hour)
        method: S3 method ('get_object' for download, 'put_object' for upload)
        
    Returns:
        Presigned URL string
    """
    return s3_client.generate_presigned_url(
        method,
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def get_presigned_download_url(
    key: str,
    bucket: str = DEFAULT_BUCKET,
    expires_in: int = 3600,
    filename: str | None = None,
) -> str:
    """
    Generate a presigned URL for downloading with optional filename.
    
    Args:
        key: S3 object key (path)
        bucket: Bucket name (defaults to configured bucket)
        expires_in: URL expiration time in seconds (default 1 hour)
        filename: Optional filename for Content-Disposition header
        
    Returns:
        Presigned URL string
    """
    params = {"Bucket": bucket, "Key": key}
    if filename:
        params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'

    return s3_client.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=expires_in,
    )


async def create_bucket_if_not_exists(bucket: str = DEFAULT_BUCKET) -> bool:
    """
    Create bucket if it doesn't exist (for local development with MinIO).
    
    Args:
        bucket: Bucket name to create
        
    Returns:
        True if bucket was created or already exists
    """
    try:
        s3_client.head_bucket(Bucket=bucket)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            s3_client.create_bucket(Bucket=bucket)
            return True
        raise


# S3 key path helpers
class S3Keys:
    """S3 key path constants and helpers"""

    # Upload paths
    UPLOADS = "uploads/{user_id}/{job_id}/{filename}"
    RESULTS = "results/{user_id}/{job_id}/{filename}"

    @classmethod
    def upload_path(cls, user_id: str, job_id: str, filename: str) -> str:
        """Generate upload path for original files"""
        return cls.UPLOADS.format(
            user_id=user_id,
            job_id=job_id,
            filename=filename,
        )

    @classmethod
    def result_path(cls, user_id: str, job_id: str, filename: str) -> str:
        """Generate result path for translated files"""
        return cls.RESULTS.format(
            user_id=user_id,
            job_id=job_id,
            filename=filename,
        )

