"""add physical asset identifiers and location hierarchy

Revision ID: 0005_physical_assets
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_physical_assets"
down_revision = "0004_discovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("qr_code", sa.String(255)))
    op.add_column("assets", sa.Column("barcode", sa.String(255)))
    op.create_unique_constraint("uq_assets_qr_code", "assets", ["qr_code"])
    op.create_unique_constraint("uq_assets_barcode", "assets", ["barcode"])
    op.add_column("locations", sa.Column("parent_id", sa.BigInteger(), sa.ForeignKey("locations.id", ondelete="RESTRICT")))
    op.create_index("ix_locations_parent", "locations", ["parent_id"])


def downgrade() -> None:
    op.drop_index("ix_locations_parent", table_name="locations")
    op.drop_column("locations", "parent_id")
    op.drop_constraint("uq_assets_barcode", "assets", type_="unique")
    op.drop_constraint("uq_assets_qr_code", "assets", type_="unique")
    op.drop_column("assets", "barcode")
    op.drop_column("assets", "qr_code")
