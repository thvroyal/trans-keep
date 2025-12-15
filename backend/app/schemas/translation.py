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


class ApplyToneRequest(BaseModel):
    """Request schema for applying tone customization"""
    
    tone: str = Field(..., description="Tone preset (professional, casual, technical, creative) or custom description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tone": "professional"
            }
        }


class ApplyToneResponse(BaseModel):
    """Response schema for tone customization"""
    
    success: bool = Field(..., description="Whether tone customization was started")
    job_id: str = Field(..., description="Translation job ID")
    message: str = Field(..., description="Status message")
    estimated_cost_usd: Optional[float] = Field(None, description="Estimated cost in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Tone customization started",
                "estimated_cost_usd": 0.048
            }
        }


class ToneEstimateResponse(BaseModel):
    """Response schema for tone cost estimate"""
    
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")
    character_count: int = Field(..., description="Total character count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estimated_cost_usd": 0.048,
                "character_count": 50000
            }
        }


class AlternativesRequest(BaseModel):
    """Request schema for generating alternative translations"""
    
    text: str = Field(..., description="Text to generate alternatives for")
    target_lang: str = Field(..., description="Target language code")
    count: int = Field(3, ge=1, le=5, description="Number of alternatives to generate (1-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "target_lang": "JA",
                "count": 3
            }
        }


class AlternativesResponse(BaseModel):
    """Response schema for alternative translations"""
    
    alternatives: list[str] = Field(..., description="List of alternative translations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alternatives": [
                    "こんにちは、お元気ですか？",
                    "こんにちは、いかがお過ごしですか？",
                    "こんにちは、調子はどうですか？"
                ]
            }
        }


class RetranslateRequest(BaseModel):
    """Request schema for re-translating edited text"""
    
    text: str = Field(..., description="Text to re-translate")
    tone: str = Field("professional", description="Tone preset or custom description")
    target_lang: str = Field(..., description="Target language code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a test",
                "tone": "professional",
                "target_lang": "JA"
            }
        }


class RetranslateResponse(BaseModel):
    """Response schema for re-translation"""
    
    translated_text: str = Field(..., description="Re-translated text")
    cost_usd: float = Field(..., description="Cost in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "これはテストです",
                "cost_usd": 0.0001
            }
        }

