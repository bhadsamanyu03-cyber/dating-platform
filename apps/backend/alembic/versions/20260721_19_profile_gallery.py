"""Add primary photo support to the profile gallery."""

from alembic import op
import sqlalchemy as sa

revision = "20260721_19"
down_revision = "20260721_18"
branch_labels = depends_on = None


def upgrade():
    op.add_column(
        "profile_photos", sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_profile_photos_primary ON profile_photos (profile_id) "
        "WHERE is_primary"
    )


def downgrade():
    op.drop_index("uq_profile_photos_primary", table_name="profile_photos")
    op.drop_column("profile_photos", "is_primary")
