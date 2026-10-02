"""seed initial monitoring definitions and alert rules

Revision ID: 0008_monitoring_seed
"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0008_monitoring_seed"
down_revision = "0007_monitoring"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    now = datetime.now(timezone.utc)

    metric_definitions = sa.table(
        "metric_definitions",
        sa.column("id", sa.BigInteger),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("category", sa.String),
        sa.column("value_type", sa.String),
        sa.column("unit", sa.String),
        sa.column("aggregation_type", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    bind.execute(
        sa.insert(metric_definitions).values([
            {
                "code": "ping_ms",
                "name": "ICMP latency",
                "description": "Round-trip ICMP latency from the monitoring worker.",
                "category": "AVAILABILITY",
                "value_type": "NUMBER",
                "unit": "ms",
                "aggregation_type": "AVG",
                "enabled": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "code": "agent_heartbeat_age",
                "name": "Agent heartbeat age",
                "description": "Seconds since the last successful agent heartbeat.",
                "category": "AVAILABILITY",
                "value_type": "NUMBER",
                "unit": "s",
                "aggregation_type": "MAX",
                "enabled": True,
                "created_at": now,
                "updated_at": now,
            },
        ])
    )

    metric_rows = bind.execute(
        sa.select(metric_definitions.c.id, metric_definitions.c.code).where(
            metric_definitions.c.code.in_(["ping_ms", "agent_heartbeat_age"])
        )
    ).fetchall()
    ids = {row.code: row.id for row in metric_rows}

    alert_rules = sa.table(
        "alert_rules",
        sa.column("name", sa.String),
        sa.column("code", sa.String),
        sa.column("metric_definition_id", sa.BigInteger),
        sa.column("operator", sa.String),
        sa.column("threshold", sa.Numeric),
        sa.column("duration_seconds", sa.Integer),
        sa.column("evaluation_window_seconds", sa.Integer),
        sa.column("severity", sa.String),
        sa.column("cooldown_seconds", sa.Integer),
        sa.column("enabled", sa.Boolean),
        sa.column("description", sa.Text),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    bind.execute(
        sa.insert(alert_rules).values([
            {
                "name": "High ICMP latency",
                "code": "PING_HIGH_LATENCY",
                "metric_definition_id": ids["ping_ms"],
                "operator": ">",
                "threshold": 1000,
                "duration_seconds": 0,
                "evaluation_window_seconds": 300,
                "severity": "WARNING",
                "cooldown_seconds": 300,
                "enabled": True,
                "description": "Raise a warning when ICMP latency exceeds 1000 ms.",
                "created_at": now,
                "updated_at": now,
            },
            {
                "name": "Agent heartbeat stale",
                "code": "AGENT_HEARTBEAT_STALE",
                "metric_definition_id": ids["agent_heartbeat_age"],
                "operator": ">",
                "threshold": 300,
                "duration_seconds": 0,
                "evaluation_window_seconds": 300,
                "severity": "CRITICAL",
                "cooldown_seconds": 300,
                "enabled": True,
                "description": "Raise a critical alert when an agent has not checked in for 5 minutes.",
                "created_at": now,
                "updated_at": now,
            },
        ])
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM alert_rules WHERE code IN ('PING_HIGH_LATENCY', 'AGENT_HEARTBEAT_STALE')"))
    bind.execute(sa.text("DELETE FROM metric_definitions WHERE code IN ('ping_ms', 'agent_heartbeat_age')"))
