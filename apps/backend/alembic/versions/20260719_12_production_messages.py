"""Extend messages with production lifecycle and attachment records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4

revision = "20260719_12"
down_revision = "20260719_07"
branch_labels = depends_on = None


def upgrade():
    op.add_column("messages", sa.Column("delivered_at", sa.DateTime(timezone=True)))
    op.add_column("messages", sa.Column("read_at", sa.DateTime(timezone=True)))
    op.add_column("messages", sa.Column("client_message_id", postgresql.UUID(as_uuid=True)))
    op.create_index("ix_messages_created", "messages", ["created_at"])
    op.create_index(
        "uq_messages_sender_client_message",
        "messages",
        ["sender_user_id", "client_message_id"],
        unique=True,
    )
    op.create_table(
        "message_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "media_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("media_assets.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("ordering", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_message_media_message", "message_media", ["message_id", "ordering"])
    bind = op.get_bind()
    for message_id, asset_id in bind.execute(
        sa.text("SELECT id, media_asset_id FROM messages WHERE media_asset_id IS NOT NULL")
    ):
        bind.execute(
            sa.text(
                "INSERT INTO message_media (id, message_id, media_asset_id, ordering) VALUES (:id, :message_id, :asset_id, 0)"
            ),
            {"id": uuid4(), "message_id": message_id, "asset_id": asset_id},
        )


def downgrade():
    op.drop_table("message_media")
    op.drop_index("uq_messages_sender_client_message", table_name="messages")
    op.drop_index("ix_messages_created", table_name="messages")
    op.drop_column("messages", "client_message_id")
    op.drop_column("messages", "read_at")
    op.drop_column("messages", "delivered_at")
