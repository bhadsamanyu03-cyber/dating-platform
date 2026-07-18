"""Create discovery action tables.

Revision ID: 20260718_03
Revises: 20260718_02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260718_03"
down_revision = "20260718_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table, actor, target, name in (
        ("profile_likes", "liker_user_id", "liked_user_id", "uq_profile_like"),
        ("profile_passes", "passer_user_id", "passed_user_id", "uq_profile_pass"),
    ):
        op.create_table(
            table,
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                actor,
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                target,
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint(actor, target, name=name),
        )
        op.create_index(f"ix_{table}_{actor}", table, [actor])
        op.create_index(f"ix_{table}_{target}", table, [target])


def downgrade() -> None:
    op.drop_table("profile_passes")
    op.drop_table("profile_likes")
