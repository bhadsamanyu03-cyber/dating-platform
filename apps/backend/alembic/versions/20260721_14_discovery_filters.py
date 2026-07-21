"""Add profile discovery visibility and blocking state."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_14"
down_revision = "20260721_13"
branch_labels = depends_on = None


def upgrade():
    op.add_column("user_profiles", sa.Column("is_discoverable", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("profile_blocks", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("blocker_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("blocked_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_profile_blocks_blocker_user_id", "profile_blocks", ["blocker_user_id"])
    op.create_index("ix_profile_blocks_blocked_user_id", "profile_blocks", ["blocked_user_id"])
    op.create_unique_constraint("uq_profile_block", "profile_blocks", ["blocker_user_id", "blocked_user_id"])


def downgrade():
    op.drop_table("profile_blocks")
    op.drop_column("user_profiles", "is_discoverable")
