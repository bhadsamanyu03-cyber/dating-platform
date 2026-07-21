"""Add persisted user presence."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_22"
down_revision = "20260721_21"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "user_presence",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("status", sa.String(length=10), nullable=False, server_default="online"),
        sa.CheckConstraint("status IN ('online', 'away', 'offline')", name="ck_user_presence_status"),
    )


def downgrade():
    op.drop_table("user_presence")
