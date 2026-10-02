from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Agent, Asset, AssetNetworkInterface, Metric, MetricDefinition
from app.monitoring.collectors import choose_ping_target, collect_icmp, heartbeat_age_seconds
from app.workers.celery_app import celery_app


def _metric_definition(db, code: str):
    return db.scalar(select(MetricDefinition).where(MetricDefinition.code == code, MetricDefinition.enabled.is_(True)))


def _record_metric(db, asset_id: int, definition, value: float, unit: str | None, resource: str | None, timestamp: datetime) -> None:
    db.add(Metric(
        asset_id=asset_id,
        metric_definition_id=definition.id,
        value=value,
        unit=unit,
        resource_identifier=resource,
        timestamp=timestamp,
    ))


@celery_app.task(name="monitoring.collect_icmp")
def collect_icmp_metrics() -> int:
    now = datetime.now(timezone.utc)
    count = 0
    with SessionLocal() as db:
        definition = _metric_definition(db, "ping_ms")
        if definition is None:
            return 0
        assets = db.scalars(select(Asset).where(Asset.status.not_in(["RETIRED"]))).all()
        for asset in assets:
            interfaces = db.scalars(
                select(AssetNetworkInterface).where(AssetNetworkInterface.asset_id == asset.id)
            ).all()
            target = choose_ping_target(asset, interfaces)
            value = collect_icmp(target) if target else None
            if value is not None:
                _record_metric(db, asset.id, definition, value, "ms", target, now)
                count += 1
        db.commit()
    return count


@celery_app.task(name="monitoring.collect_agent_heartbeat")
def collect_agent_heartbeat_metrics() -> int:
    now = datetime.now(timezone.utc)
    count = 0
    with SessionLocal() as db:
        definition = _metric_definition(db, "agent_heartbeat_age")
        if definition is None:
            return 0
        rows = db.execute(
            select(Agent, Asset).join(Asset, Asset.id == Agent.asset_id).where(Asset.status.not_in(["RETIRED"]))
        ).all()
        for agent, asset in rows:
            age = heartbeat_age_seconds(agent.last_seen, now)
            if age is not None:
                _record_metric(db, asset.id, definition, age, "s", "agent", now)
                count += 1
        db.commit()
    return count
