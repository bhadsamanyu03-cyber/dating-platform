"""Add persisted discovery preferences."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260721_17"
down_revision = "20260721_16"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "discovery_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferred_gender", sa.String(length=100), nullable=False, server_default="All"),
        sa.Column("minimum_age", sa.Integer(), nullable=False, server_default="18"),
        sa.Column("maximum_age", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("maximum_distance_km", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("show_verified_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("show_only_with_photos", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("minimum_age <= maximum_age", name="ck_discovery_preferences_age_range"),
        sa.CheckConstraint("maximum_distance_km BETWEEN 1 AND 10000", name="ck_discovery_preferences_distance"),
        sa.CheckConstraint("preferred_gender IN ('All', 'Woman', 'Man', 'Non-binary', 'Other', 'Prefer not to say')", name="ck_discovery_preferences_gender"),
    )


def downgrade():
    op.drop_table("discovery_preferences")
