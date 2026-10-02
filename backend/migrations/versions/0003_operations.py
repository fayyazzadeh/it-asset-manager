"""add physical asset, lifecycle, custody and audit tables

Revision ID: 0003_operations
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_operations"
down_revision = "0002_inventory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table("users",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("username",sa.String(100),nullable=False,unique=True),
        sa.Column("email",sa.String(320),nullable=False,unique=True), sa.Column("full_name",sa.String(200)),
        sa.Column("password_hash",sa.String(255),nullable=False), sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("created_at",dt,nullable=False), sa.Column("updated_at",dt,nullable=False))
    op.create_table("departments",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("name",sa.String(150),nullable=False,unique=True),
        sa.Column("code",sa.String(50),unique=True), sa.Column("description",sa.Text()),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_table("asset_custody",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="CASCADE"),nullable=False),
        sa.Column("user_id",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="RESTRICT")), sa.Column("department_id",sa.BigInteger(),sa.ForeignKey("departments.id",ondelete="RESTRICT")),
        sa.Column("assigned_at",dt,nullable=False), sa.Column("returned_at",dt), sa.Column("notes",sa.Text()))
    op.create_index("ix_asset_custody_asset_active","asset_custody",["asset_id","returned_at"])
    op.create_table("asset_photos",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="CASCADE"),nullable=False),
        sa.Column("file_path",sa.String(1000),nullable=False), sa.Column("caption",sa.String(300)),
        sa.Column("is_primary",sa.Boolean(),nullable=False,server_default=sa.false()), sa.Column("created_at",dt,nullable=False))
    op.create_table("asset_lifecycle_history",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("old_status",sa.String(40)), sa.Column("new_status",sa.String(40),nullable=False),
        sa.Column("changed_by",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="RESTRICT")),
        sa.Column("reason",sa.Text()), sa.Column("changed_at",dt,nullable=False))
    op.create_index("ix_lifecycle_asset_time","asset_lifecycle_history",["asset_id","changed_at"])
    op.create_table("audit_logs",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT")),
        sa.Column("user_id",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="RESTRICT")), sa.Column("action",sa.String(80),nullable=False),
        sa.Column("entity",sa.String(100),nullable=False), sa.Column("field_name",sa.String(100)), sa.Column("old_value",sa.Text()),
        sa.Column("new_value",sa.Text()), sa.Column("description",sa.Text()), sa.Column("created_at",dt,nullable=False))
    op.create_index("ix_audit_entity_time","audit_logs",["entity","created_at"])
    op.create_table("asset_change_history",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("change_type",sa.String(80),nullable=False), sa.Column("entity",sa.String(100),nullable=False),
        sa.Column("field_name",sa.String(100)), sa.Column("old_value",sa.Text()), sa.Column("new_value",sa.Text()),
        sa.Column("description",sa.Text()), sa.Column("changed_at",dt,nullable=False))
    op.create_index("ix_asset_change_asset_time","asset_change_history",["asset_id","changed_at"])
    op.create_table("asset_identity_changes",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("field_name",sa.String(100),nullable=False), sa.Column("old_value",sa.Text()), sa.Column("new_value",sa.Text()),
        sa.Column("reason",sa.Text()), sa.Column("description",sa.Text()),
        sa.Column("requested_by",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="RESTRICT")),
        sa.Column("requested_at",dt,nullable=False), sa.Column("approved_by",sa.BigInteger(),sa.ForeignKey("users.id",ondelete="RESTRICT")),
        sa.Column("approved_at",dt), sa.Column("status",sa.String(30),nullable=False,server_default="PENDING"))
    op.create_index("ix_identity_change_asset_status","asset_identity_changes",["asset_id","status"])
    op.create_table("custom_asset_fields",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="CASCADE"),nullable=False),
        sa.Column("field_name",sa.String(100),nullable=False), sa.Column("field_value",sa.Text()),
        sa.Column("value_type",sa.String(30),nullable=False,server_default="TEXT"), sa.Column("metadata",postgresql.JSONB()),
        sa.Column("created_at",dt,nullable=False), sa.Column("updated_at",dt,nullable=False),
        sa.UniqueConstraint("asset_id","field_name"))


def downgrade() -> None:
    for t in ["custom_asset_fields","asset_identity_changes","asset_change_history","audit_logs","asset_lifecycle_history","asset_photos","asset_custody","departments","users"]:
        op.drop_table(t)
