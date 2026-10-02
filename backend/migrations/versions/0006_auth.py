"""add authentication and RBAC persistence

Revision ID: 0006_auth
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_auth"
down_revision = "0005_physical_assets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table("roles",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("code",sa.String(50),nullable=False,unique=True),
        sa.Column("name",sa.String(100),nullable=False), sa.Column("description",sa.Text()))
    op.bulk_insert(sa.table("roles", sa.column("code",sa.String()), sa.column("name",sa.String()), sa.column("description",sa.Text())), [
        {"code":"ADMIN","name":"Administrator","description":"Full platform administration"},
        {"code":"OPERATOR","name":"Operator","description":"Operational asset and monitoring access"},
        {"code":"VIEWER","name":"Viewer","description":"Read-only access"},
    ])
    op.create_table("user_roles",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("user_id",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("role_id",sa.BigInteger(),sa.ForeignKey("roles.id",ondelete="CASCADE"),nullable=False),
        sa.UniqueConstraint("user_id","role_id"))
    op.create_table("refresh_tokens",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("user_id",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
        sa.Column("token_hash",sa.String(255),nullable=False,unique=True), sa.Column("expires_at",dt,nullable=False),
        sa.Column("revoked_at",dt), sa.Column("created_at",dt,nullable=False))


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("user_roles")
    op.drop_table("roles")
