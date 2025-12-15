"""Download request and response schemas"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class EditRequest(BaseModel):
    """User edit for a specific block"""
    
    block_id: int = Field(..., description="Block ID to edit")
    text: str = Field(..., description="Edited text content")


class DownloadRequest(BaseModel):
    """Request to download PDF with user edits"""
    
    edits: List[EditRequest] = Field(
        default_factory=list,
        description="List of user edits to apply to translated blocks",
    )


class DownloadResponse(BaseModel):
    """Response with download URL and metadata"""
    
    download_url: str = Field(..., description="Presigned S3 URL for download (valid for 1 hour)")
    expires_at: datetime | None = Field(None, description="URL expiration timestamp")
    file_size: int = Field(..., description="File size in bytes")
