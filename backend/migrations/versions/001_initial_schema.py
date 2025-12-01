"""Initial schema - Users, Translations, DocumentBlocks, Glossaries

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-12-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create subscription_tier enum
    subscription_tier_enum = postgresql.ENUM(
        "free", "pro", "enterprise",
        name="subscriptiontier",
        create_type=True,
    )
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)

    # Create translation_status enum
    translation_status_enum = postgresql.ENUM(
        "pending", "extracting", "translating", "applying_tone",
        "reconstructing", "completed", "failed",
        name="translationstatus",
        create_type=True,
    )
    translation_status_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("picture_url", sa.String(500), nullable=True),
        sa.Column(
            "subscription_tier",
            postgresql.ENUM("free", "pro", "enterprise", name="subscriptiontier"),
            nullable=False,
            server_default="free",
        ),
        sa.Column("usage_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_google_id", "users", ["google_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_tenant_email", "users", ["tenant_id", "email"])

    # Create translations table
    op.create_table(
        "translations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("source_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("target_language", sa.String(10), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "extracting", "translating", "applying_tone",
                "reconstructing", "completed", "failed",
                name="translationstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("original_file_path", sa.String(500), nullable=False),
        sa.Column("result_file_path", sa.String(500), nullable=True),
        sa.Column("tone_preset", sa.String(50), nullable=True),
        sa.Column("custom_tone", sa.Text(), nullable=True),
        sa.Column("translation_cost", sa.Float(), nullable=True),
        sa.Column("tone_cost", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_translations_tenant_id", "translations", ["tenant_id"])
    op.create_index("ix_translations_user_id", "translations", ["user_id"])
    op.create_index("ix_translations_status", "translations", ["status"])
    op.create_index("ix_translations_tenant_status", "translations", ["tenant_id", "status"])
    op.create_index("ix_translations_user_created", "translations", ["user_id", "created_at"])
    op.create_index("ix_translations_expires", "translations", ["expires_at"])

    # Create document_blocks table
    op.create_table(
        "document_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("translation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_num", sa.Integer(), nullable=False),
        sa.Column("block_num", sa.Integer(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("translated_text", sa.Text(), nullable=True),
        sa.Column("edited_text", sa.Text(), nullable=True),
        sa.Column(
            "coordinates",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
            comment="Bounding box: {x, y, width, height} as percentages",
        ),
        sa.Column("font_size", sa.Float(), nullable=True),
        sa.Column("font_name", sa.Text(), nullable=True),
        sa.Column("is_bold", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_italic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rotation", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["translation_id"],
            ["translations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_blocks_translation_id", "document_blocks", ["translation_id"])
    op.create_index(
        "ix_blocks_translation_page",
        "document_blocks",
        ["translation_id", "page_num"],
    )
    op.create_index(
        "ix_blocks_translation_order",
        "document_blocks",
        ["translation_id", "page_num", "block_num"],
    )

    # Create glossaries table
    op.create_table(
        "glossaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_term", sa.String(500), nullable=False),
        sa.Column("translated_term", sa.String(500), nullable=False),
        sa.Column("source_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("target_language", sa.String(10), nullable=False),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("case_sensitive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_glossaries_tenant_id", "glossaries", ["tenant_id"])
    op.create_index("ix_glossaries_user_id", "glossaries", ["user_id"])
    op.create_index(
        "ix_glossaries_tenant_lang",
        "glossaries",
        ["tenant_id", "source_language", "target_language"],
    )
    op.create_index(
        "ix_glossaries_user_source",
        "glossaries",
        ["user_id", "source_term"],
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("glossaries")
    op.drop_table("document_blocks")
    op.drop_table("translations")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS translationstatus")
    op.execute("DROP TYPE IF EXISTS subscriptiontier")

