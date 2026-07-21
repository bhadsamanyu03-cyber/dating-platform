"""Complete message media attachment metadata."""

from alembic import op
import sqlalchemy as sa

revision = "20260721_21"
down_revision = "20260721_20"
branch_labels = depends_on = None


def upgrade():
    op.add_column(
        "message_media",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.execute(
        "UPDATE media_assets SET processing_state = 'READY' WHERE upload_status = 'UPLOADED'"
    )


def downgrade():
    op.drop_column("message_media", "created_at")
