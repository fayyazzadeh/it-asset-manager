"""create asset core tables

Revision ID: 0001_asset_core
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_asset_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asset_types",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_asset_types_is_active", "asset_types", ["is_active"])

    op.create_table(
        "asset_subtypes",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_type_id", sa.BigInteger(), sa.ForeignKey("asset_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("asset_type_id", "code"),
    )

    op.create_table(
        "networks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False, unique=True),
        sa.Column("network_address", postgresql.INET()),
        sa.Column("cidr", sa.Integer(), nullable=False),
        sa.Column("gateway", postgresql.INET()),
        sa.Column("network_type", sa.String(50)),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("cidr >= 0 AND cidr <= 128", name="ck_network_cidr"),
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("building", sa.String(100)),
        sa.Column("floor", sa.String(50)),
        sa.Column("room", sa.String(50)),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", "building", "floor", "room"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_tag", sa.String(100), nullable=False, unique=True),
        sa.Column("asset_type_id", sa.BigInteger(), sa.ForeignKey("asset_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("asset_subtype_id", sa.BigInteger(), sa.ForeignKey("asset_subtypes.id", ondelete="RESTRICT")),
        sa.Column("network_id", sa.BigInteger(), sa.ForeignKey("networks.id", ondelete="RESTRICT")),
        sa.Column("location_id", sa.BigInteger(), sa.ForeignKey("locations.id", ondelete="RESTRICT")),
        sa.Column("status", sa.String(40), nullable=False, server_default="DISCOVERED"),
        sa.Column("computer_name", sa.String(255)),
        sa.Column("hostname", sa.String(255)),
        sa.Column("fqdn", sa.String(255)),
        sa.Column("domain", sa.String(255)),
        sa.Column("manufacturer", sa.String(150)),
        sa.Column("model", sa.String(150)),
        sa.Column("serial_number", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("first_seen", sa.DateTime(timezone=True)),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for name, column in [
        ("ix_assets_status", "status"),
        ("ix_assets_hostname", "hostname"),
        ("ix_assets_fqdn", "fqdn"),
        ("ix_assets_serial_number", "serial_number"),
        ("ix_assets_last_seen", "last_seen"),
    ]:
        op.create_index(name, "assets", [column])

    op.create_table(
        "asset_identifiers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("identifier_type", sa.String(50), nullable=False),
        sa.Column("identifier_value", sa.String(255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("first_seen", sa.DateTime(timezone=True)),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("identifier_type", "identifier_value"),
    )
    op.create_index("ix_asset_identifiers_asset", "asset_identifiers", ["asset_id"])
    op.create_index("ix_asset_identifiers_type_value", "asset_identifiers", ["identifier_type", "identifier_value"])

    op.create_table(
        "asset_network_interfaces",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("network_id", sa.BigInteger(), sa.ForeignKey("networks.id", ondelete="RESTRICT")),
        sa.Column("interface_name", sa.String(150)),
        sa.Column("mac_address", postgresql.MACADDR()),
        sa.Column("ip_address", postgresql.INET()),
        sa.Column("ip_version", sa.Integer()),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("speed", sa.BigInteger()),
        sa.Column("status", sa.String(40)),
        sa.Column("first_seen", sa.DateTime(timezone=True)),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for name, column in [
        ("ix_asset_nic_asset", "asset_id"),
        ("ix_asset_nic_ip", "ip_address"),
        ("ix_asset_nic_mac", "mac_address"),
        ("ix_asset_nic_last_seen", "last_seen"),
    ]:
        op.create_index(name, "asset_network_interfaces", [column])


def downgrade() -> None:
    op.drop_table("asset_network_interfaces")
    op.drop_table("asset_identifiers")
    op.drop_table("assets")
    op.drop_table("locations")
    op.drop_table("networks")
    op.drop_table("asset_subtypes")
    op.drop_index("ix_asset_types_is_active", table_name="asset_types")
    op.drop_table("asset_types")