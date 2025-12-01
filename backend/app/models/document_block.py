"""DocumentBlock model for TransKeep"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentBlock(Base):
    """
    DocumentBlock model for storing extracted text blocks from PDFs.
    
    Each block represents a text element with its position coordinates,
    original text, and translated text. Used for synchronized highlighting
    in the side-by-side review panel.
    """

    __tablename__ = "document_blocks"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Translation reference
    translation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("translations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Block position
    page_num: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    block_num: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Text content
    original_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    translated_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    edited_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Coordinates (normalized percentages 0-100)
    coordinates: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Bounding box: {x, y, width, height} as percentages",
    )

    # Font information
    font_size: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    font_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_bold: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    is_italic: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    rotation: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    translation: Mapped["Translation"] = relationship(
        "Translation",
        back_populates="blocks",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_blocks_translation_page", "translation_id", "page_num"),
        Index("ix_blocks_translation_order", "translation_id", "page_num", "block_num"),
    )

    def __repr__(self) -> str:
        return f"<DocumentBlock page={self.page_num} block={self.block_num}>"


# Import at bottom to avoid circular imports
from app.models.translation import Translation  # noqa: E402

