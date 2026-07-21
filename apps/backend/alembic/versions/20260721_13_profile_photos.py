"""Create profile photo associations."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_13"
down_revision = "20260719_12"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "profile_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("media_assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ordering", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("uq_profile_photos_profile_asset", "profile_photos", ["profile_id", "media_asset_id"], unique=True)
    op.create_index("ix_profile_photos_profile_ordering", "profile_photos", ["profile_id", "ordering"])


def downgrade():
    op.drop_table("profile_photos")
