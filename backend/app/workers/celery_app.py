from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "it_asset_manager",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
