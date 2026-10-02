"""add discovery and agent tables

Revision ID: 0004_discovery
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_discovery"
down_revision = "0003_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table("discovery_runs",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("source",sa.String(50),nullable=False),
        sa.Column("started_at",dt,nullable=False), sa.Column("finished_at",dt), sa.Column("status",sa.String(30),nullable=False),
        sa.Column("total_observations",sa.Integer(),nullable=False,server_default="0"), sa.Column("new_assets",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("matched_assets",sa.Integer(),nullable=False,server_default="0"), sa.Column("changed_assets",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("ambiguous_assets",sa.Integer(),nullable=False,server_default="0"), sa.Column("failed_observations",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("error_message",sa.Text()))
    op.create_table("discovery_observations",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("source",sa.String(50),nullable=False),
        sa.Column("source_run_id",sa.BigInteger(),sa.ForeignKey("discovery_runs.id",ondelete="SET NULL")), sa.Column("observed_at",dt,nullable=False),
        sa.Column("ip_address",postgresql.INET()), sa.Column("mac_address",sa.String(50)), sa.Column("hostname",sa.String(255)),
        sa.Column("fqdn",sa.String(255)), sa.Column("computer_name",sa.String(255)), sa.Column("serial_number",sa.String(255)),
        sa.Column("bios_uuid",sa.String(255)), sa.Column("machine_uuid",sa.String(255)), sa.Column("agent_id",sa.String(255)),
        sa.Column("ad_domain",sa.String(255)), sa.Column("ad_computer_name",sa.String(255)), sa.Column("manufacturer",sa.String(150)),
        sa.Column("model",sa.String(150)), sa.Column("os_name",sa.String(150)), sa.Column("os_version",sa.String(100)),
        sa.Column("raw_data",postgresql.JSONB()), sa.Column("confidence",sa.Float()), sa.Column("match_status",sa.String(30)),
        sa.Column("matched_asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="SET NULL")))
    for n,c in [("ix_discovery_obs_source_time",["source","observed_at"]),("ix_discovery_obs_agent",["agent_id"]),("ix_discovery_obs_serial",["serial_number"]),("ix_discovery_obs_ip",["ip_address"])]:
        op.create_index(n,"discovery_observations",c)
    op.create_table("agents",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("agent_id",sa.String(255),nullable=False,unique=True), sa.Column("version",sa.String(50)),
        sa.Column("status",sa.String(30),nullable=False,server_default="ACTIVE"), sa.Column("last_seen",dt),
        sa.Column("ip_address",postgresql.INET()), sa.Column("os",sa.String(150)), sa.Column("installed_at",dt))
    op.create_table("agent_tokens",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("agent_id",sa.BigInteger(),sa.ForeignKey("agents.id",ondelete="CASCADE"),nullable=False),
        sa.Column("token_hash",sa.String(255),nullable=False), sa.Column("expires_at",dt), sa.Column("created_at",dt,nullable=False), sa.Column("revoked_at",dt))
    op.create_index("ix_agent_tokens_agent","agent_tokens",["agent_id"])


def downgrade() -> None:
    op.drop_table("agent_tokens")
    op.drop_table("agents")
    op.drop_table("discovery_observations")
    op.drop_table("discovery_runs")
