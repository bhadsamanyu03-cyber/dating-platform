"""Create posts and post media."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_07"
down_revision = "20260719_06"
branch_labels = depends_on = None


def upgrade():
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "author_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("caption", sa.Text),
        sa.Column("visibility", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "post_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "post_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "media_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("media_assets.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer, nullable=False),
        sa.UniqueConstraint("media_asset_id", name="uq_post_media_asset"),
        sa.UniqueConstraint("post_id", "position", name="uq_post_media_position"),
    )
    op.create_index("ix_posts_timeline", "posts", ["created_at", "id"])
    op.create_index("ix_posts_author", "posts", ["author_user_id"])
    op.create_index("ix_posts_visibility", "posts", ["visibility"])


def downgrade():
    op.drop_table("post_media")
    op.drop_table("posts")
