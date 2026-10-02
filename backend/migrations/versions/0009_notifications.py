"""add notification templates, policies, channels, and alert queue

Revision ID: 0009_notifications
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_notifications"
down_revision = "0008_monitoring_seed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dt = sa.DateTime(timezone=True)
    op.create_table(
        "notification_templates",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("subject_template", sa.String(300), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", dt, nullable=False),
        sa.Column("updated_at", dt, nullable=False),
    )
    op.create_table(
        "notification_recipients",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(320)),
        sa.Column("phone", sa.String(50)),
        sa.Column("webhook_url", sa.String(1000)),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", dt, nullable=False),
    )
    op.create_table(
        "notification_groups",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "notification_group_members",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("group_id", sa.BigInteger(), sa.ForeignKey("notification_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", sa.BigInteger(), sa.ForeignKey("notification_recipients.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("group_id", "recipient_id"),
    )
    op.create_table(
        "notification_channels",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("channel_type", sa.String(30), nullable=False),
        sa.Column("configuration", sa.JSON()),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", dt, nullable=False),
    )
    op.create_table(
        "notification_policies",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(30)),
        sa.Column("template_id", sa.BigInteger(), sa.ForeignKey("notification_templates.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("recipient_group_id", sa.BigInteger(), sa.ForeignKey("notification_groups.id", ondelete="SET NULL")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", dt, nullable=False),
        sa.Column("updated_at", dt, nullable=False),
    )
    op.create_table(
        "notification_policy_channels",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("policy_id", sa.BigInteger(), sa.ForeignKey("notification_policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), sa.ForeignKey("notification_channels.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("policy_id", "channel_id"),
    )
    op.create_table(
        "alert_notifications",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("alert_id", sa.BigInteger(), sa.ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_id", sa.BigInteger(), sa.ForeignKey("notification_policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), sa.ForeignKey("notification_channels.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("recipient_id", sa.BigInteger(), sa.ForeignKey("notification_recipients.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text()),
        sa.Column("sent_at", dt),
        sa.Column("created_at", dt, nullable=False),
    )
    op.create_index("ix_alert_notifications_alert_status", "alert_notifications", ["alert_id", "status"])
    op.create_index("ix_alert_notifications_status_created", "alert_notifications", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_alert_notifications_status_created", table_name="alert_notifications")
    op.drop_index("ix_alert_notifications_alert_status", table_name="alert_notifications")
    op.drop_table("alert_notifications")
    op.drop_table("notification_policy_channels")
    op.drop_table("notification_policies")
    op.drop_table("notification_channels")
    op.drop_table("notification_group_members")
    op.drop_table("notification_groups")
    op.drop_table("notification_recipients")
    op.drop_table("notification_templates")
