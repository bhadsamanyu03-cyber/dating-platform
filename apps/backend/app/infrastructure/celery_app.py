from celery import Celery
from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "dating_platform",
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
    include=["app.domain.media.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=10,
    task_annotations={"media.process": {"max_retries": 3}},
    beat_schedule={"recover-stale-media": {"task": "media.recover_stale", "schedule": 300.0}},
)
