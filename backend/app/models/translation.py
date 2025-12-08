"""Translation model for TransKeep"""

import enum
import uuid
from datetime import datetime, timedelta

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TranslationStatus(str, enum.Enum):
    """Translation job status"""

    PENDING = "pending"
    EXTRACTING = "extracting"
    TRANSLATING = "translating"
    APPLYING_TONE = "applying_tone"
    RECONSTRUCTING = "reconstructing"
    COMPLETED = "completed"
    FAILED = "failed"


def default_expires_at() -> datetime:
    """Default expiration time: 24 hours from now"""
    return datetime.utcnow() + timedelta(hours=24)


class Translation(Base):
    """
    Translation model for tracking document translation jobs.
    
    Each translation represents a single document being processed.
    Stores file paths, status, progress, and metadata.
    """

    __tablename__ = "translations"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Tenant and user references
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File information
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Language settings
    source_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    target_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Status and progress
    status: Mapped[TranslationStatus] = mapped_column(
        Enum(TranslationStatus, values_callable=lambda x: [e.value for e in x]),
        default=TranslationStatus.PENDING,
        nullable=False,
        index=True,
    )
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # File paths (S3 keys)
    original_file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    result_file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Tone customization
    tone_preset: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    custom_tone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Cost tracking
    translation_cost: Mapped[float | None] = mapped_column(
        nullable=True,
    )
    tone_cost: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=default_expires_at,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="translations",
    )
    blocks: Mapped[list["DocumentBlock"]] = relationship(
        "DocumentBlock",
        back_populates="translation",
        cascade="all, delete-orphan",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_translations_tenant_status", "tenant_id", "status"),
        Index("ix_translations_user_created", "user_id", "created_at"),
        Index("ix_translations_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<Translation {self.id} - {self.status.value}>"


# Import at bottom to avoid circular imports
from app.models.user import User  # noqa: E402
from app.models.document_block import DocumentBlock  # noqa: E402

