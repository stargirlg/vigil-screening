from celery import Celery
from app.config import settings

celery_app = Celery(
    "vigil",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.batch_screening",
        "app.tasks.sanction_sync",
    ],
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
    task_routes={
        "app.tasks.batch_screening.*": {"queue": "screening"},
        "app.tasks.sanction_sync.*":   {"queue": "sync"},
    },
    beat_schedule={
        "sync-ofac-daily": {
            "task": "app.tasks.sanction_sync.sync_ofac_list",
            "schedule": 86400,
        },
        "check-sla-hourly": {
            "task": "app.tasks.sla_monitor.check_sla_breaches",
            "schedule": 3600,
        },
    },
)
