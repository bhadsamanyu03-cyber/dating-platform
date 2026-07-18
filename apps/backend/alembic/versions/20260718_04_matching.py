"""Create matching domain tables.

Revision ID: 20260718_04
Revises: 20260718_03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260718_04"
down_revision = "20260718_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_one_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_two_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
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
        sa.CheckConstraint("user_one_id < user_two_id", name="ck_matches_canonical_order"),
        sa.UniqueConstraint("user_one_id", "user_two_id", name="uq_matches_pair"),
    )
    op.create_index("ix_matches_user_one_created", "matches", ["user_one_id", "created_at", "id"])
    op.create_index("ix_matches_user_two_created", "matches", ["user_two_id", "created_at", "id"])


def downgrade() -> None:
    op.drop_table("matches")
