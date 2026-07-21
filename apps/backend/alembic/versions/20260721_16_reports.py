"""Add moderation reports."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_16"
down_revision = "20260721_15"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reporter_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_reports_reporter_created", "reports", ["reporter_id", "created_at", "id"])
    op.execute(
        "CREATE UNIQUE INDEX uq_reports_active_pair ON reports (reporter_id, target_user_id) "
        "WHERE status IN ('OPEN', 'UNDER_REVIEW')"
    )


def downgrade():
    op.drop_table("reports")
