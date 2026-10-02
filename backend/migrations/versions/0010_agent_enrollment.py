"""add agent enrollment tokens

Revision ID: 0010_agent_enrollment
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_agent_enrollment"
down_revision = "0009_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enrollment_tokens",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
    )
    op.create_index("ix_enrollment_tokens_asset", "enrollment_tokens", ["asset_id"])
    op.create_index("ix_enrollment_tokens_expires", "enrollment_tokens", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_enrollment_tokens_expires", table_name="enrollment_tokens")
    op.drop_index("ix_enrollment_tokens_asset", table_name="enrollment_tokens")
    op.drop_table("enrollment_tokens")
