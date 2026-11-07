from celery import Celery
from app.config import settings

celery_app = Celery(
    "sourcing",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "check-outreach-escalations": {
            "task": "app.workers.tasks.check_outreach_escalations",
            "schedule": 300.0,  # every 5 minutes
        },
    },
)
