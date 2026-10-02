from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "it_asset_manager",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.monitoring.tasks"],
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.beat_schedule = {
    "collect-icmp-every-minute": {
        "task": "monitoring.collect_icmp",
        "schedule": 60.0,
    },
    "collect-agent-heartbeat-every-minute": {
        "task": "monitoring.collect_agent_heartbeat",
        "schedule": 60.0,
    },
}
