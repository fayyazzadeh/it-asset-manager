"""add monitoring metrics events and alerts

Revision ID: 0007_monitoring
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_monitoring"
down_revision = "0006_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table("metric_definitions",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("code",sa.String(80),nullable=False,unique=True),
        sa.Column("name",sa.String(150),nullable=False), sa.Column("description",sa.Text()), sa.Column("category",sa.String(50),nullable=False),
        sa.Column("value_type",sa.String(30),nullable=False,server_default="NUMBER"), sa.Column("unit",sa.String(30)),
        sa.Column("aggregation_type",sa.String(30)), sa.Column("enabled",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("created_at",dt,nullable=False), sa.Column("updated_at",dt,nullable=False))
    op.create_table("monitoring_profiles",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("name",sa.String(150),nullable=False),
        sa.Column("code",sa.String(80),nullable=False,unique=True), sa.Column("description",sa.Text()),
        sa.Column("asset_type_id",sa.BigInteger(),sa.ForeignKey("asset_types.id",ondelete="RESTRICT")),
        sa.Column("asset_subtype_id",sa.BigInteger(),sa.ForeignKey("asset_subtypes.id",ondelete="RESTRICT")),
        sa.Column("enabled",sa.Boolean(),nullable=False,server_default=sa.true()), sa.Column("created_at",dt,nullable=False), sa.Column("updated_at",dt,nullable=False))
    op.create_table("monitoring_profile_metrics",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("profile_id",sa.BigInteger(),sa.ForeignKey("monitoring_profiles.id",ondelete="CASCADE"),nullable=False),
        sa.Column("metric_definition_id",sa.BigInteger(),sa.ForeignKey("metric_definitions.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("enabled",sa.Boolean(),nullable=False,server_default=sa.true()), sa.Column("collection_interval_seconds",sa.Integer(),nullable=False,server_default="60"),
        sa.Column("timeout_seconds",sa.Integer(),nullable=False,server_default="10"), sa.Column("retry_count",sa.Integer(),nullable=False,server_default="2"),
        sa.UniqueConstraint("profile_id","metric_definition_id"))
    op.create_table("metrics",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="CASCADE"),nullable=False),
        sa.Column("metric_definition_id",sa.BigInteger(),sa.ForeignKey("metric_definitions.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("value",sa.Numeric(20,6),nullable=False), sa.Column("unit",sa.String(30)), sa.Column("resource_identifier",sa.String(255)),
        sa.Column("timestamp",dt,nullable=False))
    for n,c in [("ix_metrics_asset_time",["asset_id","timestamp"]),("ix_metrics_definition_time",["metric_definition_id","timestamp"]),("ix_metrics_asset_metric_time",["asset_id","metric_definition_id","timestamp"])]:
        op.create_index(n,"metrics",c)
    op.create_table("events",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="SET NULL")),
        sa.Column("event_type",sa.String(80),nullable=False), sa.Column("severity",sa.String(30),nullable=False), sa.Column("message",sa.Text(),nullable=False),
        sa.Column("source",sa.String(50),nullable=False), sa.Column("timestamp",dt,nullable=False), sa.Column("acknowledged",sa.Boolean(),nullable=False,server_default=sa.false()))
    op.create_index("ix_events_asset_time","events",["asset_id","timestamp"])
    op.create_table("alert_rules",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("name",sa.String(150),nullable=False), sa.Column("code",sa.String(80),nullable=False,unique=True),
        sa.Column("metric_definition_id",sa.BigInteger(),sa.ForeignKey("metric_definitions.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("operator",sa.String(10),nullable=False), sa.Column("threshold",sa.Numeric(20,6),nullable=False),
        sa.Column("duration_seconds",sa.Integer(),nullable=False,server_default="0"), sa.Column("evaluation_window_seconds",sa.Integer(),nullable=False,server_default="300"),
        sa.Column("severity",sa.String(30),nullable=False), sa.Column("cooldown_seconds",sa.Integer(),nullable=False,server_default="300"),
        sa.Column("enabled",sa.Boolean(),nullable=False,server_default=sa.true()), sa.Column("description",sa.Text()),
        sa.Column("created_at",dt,nullable=False), sa.Column("updated_at",dt,nullable=False))
    op.create_table("alerts",
        sa.Column("id",sa.BigInteger(),primary_key=True), sa.Column("asset_id",sa.BigInteger(),sa.ForeignKey("assets.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("alert_rule_id",sa.BigInteger(),sa.ForeignKey("alert_rules.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("event_id",sa.BigInteger(),sa.ForeignKey("events.id",ondelete="SET NULL")),
        sa.Column("severity",sa.String(30),nullable=False), sa.Column("status",sa.String(30),nullable=False,server_default="TRIGGERED"),
        sa.Column("message",sa.Text(),nullable=False), sa.Column("fingerprint",sa.String(255),nullable=False),
        sa.Column("triggered_at",dt,nullable=False), sa.Column("acknowledged_at",dt), sa.Column("resolved_at",dt))
    op.create_index("ix_alerts_asset_status","alerts",["asset_id","status"])
    op.create_index("ix_alerts_fingerprint_status","alerts",["fingerprint","status"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("alert_rules")
    op.drop_table("events")
    op.drop_table("metrics")
    op.drop_table("monitoring_profile_metrics")
    op.drop_table("monitoring_profiles")
    op.drop_table("metric_definitions")
