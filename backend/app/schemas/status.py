"""Schemas for translation job status"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Response schema for job status endpoint"""
    
    job_id: str = Field(..., description="Translation job ID")
    status: str = Field(..., description="Current status: pending, extracting, translating, completed, failed")
    progress: int = Field(..., description="Progress percentage (0-100)", ge=0, le=100)
    
    # Optional details
    file_name: Optional[str] = Field(None, description="Original file name")
    page_count: Optional[int] = Field(None, description="Total pages in PDF")
    total_blocks: Optional[int] = Field(None, description="Total text blocks extracted")
    translated_blocks: Optional[int] = Field(None, description="Number of blocks translated")
    
    # Timing
    created_at: str = Field(..., description="Job creation timestamp (ISO 8601)")
    started_at: Optional[str] = Field(None, description="Processing start timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    eta_seconds: Optional[int] = Field(None, description="Estimated time remaining (seconds)")
    
    # Language info
    source_language: Optional[str] = Field(None, description="Source language code")
    target_language: Optional[str] = Field(None, description="Target language code")
    
    # Cost tracking
    estimated_cost_usd: Optional[float] = Field(None, description="Estimated translation cost")
    
    # Error info
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "translating",
                "progress": 45,
                "file_name": "document.pdf",
                "page_count": 10,
                "total_blocks": 100,
                "translated_blocks": 45,
                "created_at": "2025-12-09T10:00:00Z",
                "started_at": "2025-12-09T10:00:05Z",
                "completed_at": None,
                "eta_seconds": 120,
                "source_language": "EN",
                "target_language": "JA",
                "estimated_cost_usd": 0.05,
                "error_message": None,
            }
        }

