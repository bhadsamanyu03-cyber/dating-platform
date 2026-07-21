"""Add rich media processing state and variants."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_20"
down_revision = "20260721_19"
branch_labels = depends_on = None


def upgrade():
    op.add_column("media_assets", sa.Column("aspect_ratio", sa.String(length=32)))
    op.add_column("media_assets", sa.Column("orientation", sa.Integer()))
    op.add_column("media_assets", sa.Column("codec", sa.String(length=100)))
    op.add_column(
        "media_assets",
        sa.Column(
            "processing_state", sa.String(length=20), nullable=False, server_default="UPLOADING"
        ),
    )
    op.create_table(
        "media_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "media_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("media_assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "uq_media_variants_asset_kind", "media_variants", ["media_asset_id", "kind"], unique=True
    )


def downgrade():
    op.drop_table("media_variants")
    op.drop_column("media_assets", "processing_state")
    op.drop_column("media_assets", "codec")
    op.drop_column("media_assets", "orientation")
    op.drop_column("media_assets", "aspect_ratio")
