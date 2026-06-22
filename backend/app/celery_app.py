from celery import Celery
from .core.config import REDIS_URL

celery_app = Celery(
    "getsmart",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.app.tasks.skill_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
