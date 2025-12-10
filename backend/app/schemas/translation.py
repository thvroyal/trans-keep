"""Schemas for translation details"""

from typing import Optional
from pydantic import BaseModel, Field


class TranslationDetailsResponse(BaseModel):
    """Response schema for translation details endpoint"""
    
    job_id: str = Field(..., description="Translation job ID")
    file_name: str = Field(..., description="Original file name")
    status: str = Field(..., description="Translation status")
    
    # PDF URLs (presigned S3 URLs)
    original_pdf_url: str = Field(..., description="Presigned URL for original PDF")
    translated_pdf_url: Optional[str] = Field(None, description="Presigned URL for translated PDF (if available)")
    
    # Language info
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")
    
    # Metadata
    page_count: Optional[int] = Field(None, description="Number of pages")
    cost_usd: Optional[float] = Field(None, description="Translation cost")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_name": "document.pdf",
                "status": "completed",
                "original_pdf_url": "https://s3.example.com/original.pdf?signature=...",
                "translated_pdf_url": "https://s3.example.com/translated.pdf?signature=...",
                "source_language": "EN",
                "target_language": "JA",
                "page_count": 10,
                "cost_usd": 0.05,
                "created_at": "2025-12-09T10:00:00Z",
                "completed_at": "2025-12-09T10:05:00Z",
            }
        }

