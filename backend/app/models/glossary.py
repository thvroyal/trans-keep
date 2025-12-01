"""Glossary model for TransKeep"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Glossary(Base):
    """
    Glossary model for storing user-defined terminology.
    
    Allows users to define custom translations for specific terms
    that will be consistently applied across all their documents.
    Supports multi-tenant architecture for enterprise glossary sharing.
    """

    __tablename__ = "glossaries"

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

    # Term definition
    source_term: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    translated_term: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    source_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    target_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Optional context/notes
    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Case sensitivity
    case_sensitive: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
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

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="glossaries",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_glossaries_tenant_lang", "tenant_id", "source_language", "target_language"),
        Index("ix_glossaries_user_source", "user_id", "source_term"),
    )

    def __repr__(self) -> str:
        return f"<Glossary '{self.source_term}' -> '{self.translated_term}'>"


# Import at bottom to avoid circular imports
from app.models.user import User  # noqa: E402

