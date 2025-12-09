"""Upload request/response schemas"""

from pydantic import BaseModel, Field, field_validator


class UploadResponse(BaseModel):
    """Response schema for file upload"""

    job_id: str = Field(..., description="Unique job ID for tracking translation")
    status: str = Field(..., description="Initial status (pending)")
    message: str = Field(..., description="Success message")
    file_name: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")


class TranslationLanguages(BaseModel):
    """Language pair for translation"""

    source_language: str = Field(
        default="auto",
        description="Source language code (auto-detect if 'auto')",
    )
    target_language: str = Field(
        ...,
        description="Target language code (e.g., 'ja', 'es', 'fr')",
    )

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, v: str) -> str:
        """Ensure target language is provided"""
        if not v or v.strip() == "":
            raise ValueError("Target language is required")
        return v.lower().strip()

    @field_validator("source_language")
    @classmethod
    def validate_source_language(cls, v: str) -> str:
        """Normalize source language"""
        return v.lower().strip() if v else "auto"
