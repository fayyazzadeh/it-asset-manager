"""expand asset inventory domain

Revision ID: 0002_inventory
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_inventory"
down_revision = "0001_asset_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table("hardware",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("manufacturer", sa.String(150)), sa.Column("model", sa.String(150)),
        sa.Column("system_family", sa.String(150)), sa.Column("chassis_type", sa.String(80)),
        sa.Column("motherboard_vendor", sa.String(150)), sa.Column("motherboard_model", sa.String(150)),
        sa.Column("motherboard_serial", sa.String(255)), sa.Column("bios_vendor", sa.String(150)),
        sa.Column("bios_version", sa.String(150)), sa.Column("bios_date", sa.String(50)),
        sa.Column("total_ram_bytes", sa.BigInteger()), sa.Column("gpu_summary", sa.Text()),
        sa.Column("description", sa.Text()), sa.Column("created_at", dt, nullable=False),
        sa.Column("updated_at", dt, nullable=False))
    op.create_table("hardware_processors",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("hardware_id", sa.BigInteger(), sa.ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False),
        sa.Column("socket", sa.String(50), nullable=False), sa.Column("manufacturer", sa.String(100)),
        sa.Column("model", sa.String(150)), sa.Column("architecture", sa.String(80)),
        sa.Column("physical_cores", sa.Integer()), sa.Column("logical_cores", sa.Integer()),
        sa.Column("base_frequency_mhz", sa.Integer()), sa.Column("max_frequency_mhz", sa.Integer()),
        sa.Column("threads", sa.Integer()), sa.Column("serial_number", sa.String(255)), sa.Column("status", sa.String(40)),
        sa.UniqueConstraint("hardware_id","socket"), sa.CheckConstraint("logical_cores IS NULL OR physical_cores IS NULL OR logical_cores >= physical_cores", name="ck_cpu_logical_ge_physical"))
    op.create_table("memory_modules",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("hardware_id", sa.BigInteger(), sa.ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot", sa.String(80), nullable=False), sa.Column("manufacturer", sa.String(100)), sa.Column("part_number", sa.String(150)),
        sa.Column("serial_number", sa.String(255)), sa.Column("capacity_bytes", sa.BigInteger()), sa.Column("memory_type", sa.String(50)),
        sa.Column("speed_mhz", sa.Integer()), sa.Column("configured_speed_mhz", sa.Integer()), sa.Column("ecc", sa.Boolean()),
        sa.Column("rank", sa.String(30)), sa.Column("status", sa.String(40)), sa.Column("first_seen", dt), sa.Column("last_seen", dt),
        sa.UniqueConstraint("hardware_id","slot"))
    op.create_index("ix_memory_serial","memory_modules",["serial_number"])
    op.create_table("storage_devices",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("hardware_id", sa.BigInteger(), sa.ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_name", sa.String(150)), sa.Column("device_path", sa.String(255)), sa.Column("manufacturer", sa.String(150)),
        sa.Column("model", sa.String(150)), sa.Column("serial_number", sa.String(255)), sa.Column("storage_type", sa.String(50)),
        sa.Column("interface_type", sa.String(50)), sa.Column("capacity_bytes", sa.BigInteger()), sa.Column("firmware_version", sa.String(100)),
        sa.Column("health_status", sa.String(40)), sa.Column("smart_supported", sa.Boolean()), sa.Column("smart_status", sa.String(40)),
        sa.Column("first_seen", dt), sa.Column("last_seen", dt), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False))
    op.create_index("ix_storage_serial","storage_devices",["serial_number"])
    op.create_table("storage_partitions",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("storage_device_id", sa.BigInteger(), sa.ForeignKey("storage_devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("partition_name", sa.String(150)), sa.Column("device_path", sa.String(255)), sa.Column("filesystem", sa.String(80)),
        sa.Column("mount_point", sa.String(255)), sa.Column("size_bytes", sa.BigInteger()), sa.Column("used_bytes", sa.BigInteger()),
        sa.Column("free_bytes", sa.BigInteger()), sa.Column("encrypted", sa.Boolean()), sa.Column("status", sa.String(40)),
        sa.Column("first_seen", dt), sa.Column("last_seen", dt))
    op.create_table("hardware_gpus",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("hardware_id", sa.BigInteger(), sa.ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False),
        sa.Column("manufacturer", sa.String(150)), sa.Column("model", sa.String(150)), sa.Column("vendor", sa.String(150)),
        sa.Column("memory_bytes", sa.BigInteger()), sa.Column("driver_version", sa.String(100)), sa.Column("device_id", sa.String(150)),
        sa.Column("status", sa.String(40)), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False))
    op.create_table("operating_systems",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("name", sa.String(150)), sa.Column("version", sa.String(100)), sa.Column("edition", sa.String(100)),
        sa.Column("build", sa.String(100)), sa.Column("architecture", sa.String(50)), sa.Column("kernel", sa.String(150)),
        sa.Column("install_date", dt), sa.Column("last_boot", dt), sa.Column("hostname", sa.String(255)), sa.Column("computer_name", sa.String(255)),
        sa.Column("license_status", sa.String(50)), sa.Column("activation_status", sa.String(50)),
        sa.Column("first_seen", dt), sa.Column("last_seen", dt), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False))
    op.create_table("software",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("publisher", sa.String(200)),
        sa.Column("description", sa.Text()), sa.Column("homepage", sa.String(500)), sa.Column("category", sa.String(100)),
        sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False),
        sa.UniqueConstraint("name","publisher"))
    op.create_index("ix_software_name","software",["name"])
    op.create_table("asset_software",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("software_id", sa.BigInteger(), sa.ForeignKey("software.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version", sa.String(150)), sa.Column("edition", sa.String(100)), sa.Column("architecture", sa.String(50)),
        sa.Column("install_date", dt), sa.Column("last_seen", dt), sa.Column("install_location", sa.String(500)),
        sa.Column("uninstall_string", sa.Text()), sa.Column("discovery_source", sa.String(50)),
        sa.Column("status", sa.String(30), nullable=False, server_default="INSTALLED"), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False),
        sa.UniqueConstraint("asset_id","software_id","version"))
    op.create_index("ix_asset_software_asset","asset_software",["asset_id"])
    op.create_table("service_definitions",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("name", sa.String(150), nullable=False),
        sa.Column("display_name", sa.String(200)), sa.Column("publisher", sa.String(200)), sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("service_type", sa.String(50)), sa.Column("description", sa.Text()), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False),
        sa.UniqueConstraint("platform","name"))
    op.create_table("asset_services",
        sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_definition_id", sa.BigInteger(), sa.ForeignKey("service_definitions.id", ondelete="RESTRICT")),
        sa.Column("service_name", sa.String(150), nullable=False), sa.Column("display_name", sa.String(200)), sa.Column("status", sa.String(40)),
        sa.Column("startup_type", sa.String(40)), sa.Column("account", sa.String(255)), sa.Column("process_id", sa.Integer()), sa.Column("port", sa.Integer()),
        sa.Column("description", sa.Text()), sa.Column("first_seen", dt), sa.Column("last_seen", dt), sa.Column("created_at", dt, nullable=False), sa.Column("updated_at", dt, nullable=False),
        sa.UniqueConstraint("asset_id","service_name"))
    op.create_index("ix_asset_services_status","asset_services",["status"])
    op.create_table("asset_relationships",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("parent_asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("child_asset_id", sa.BigInteger(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False), sa.Column("created_at", dt, nullable=False),
        sa.UniqueConstraint("parent_asset_id","child_asset_id","relationship_type"),
        sa.CheckConstraint("parent_asset_id <> child_asset_id", name="ck_asset_relationship_not_self"))


def downgrade() -> None:
    for table in ["asset_relationships","asset_services","service_definitions","asset_software","software","operating_systems","hardware_gpus","storage_partitions","storage_devices","memory_modules","hardware_processors","hardware"]:
        op.drop_table(table)
