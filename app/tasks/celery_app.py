from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=[
        "app.tasks.tasks"
    ]
)

celery_app.conf.beat_schedule = {
    "luboe-nazvanie": {
        "task": "periodic_task",
        "schedule": 5,  # секунды
        # "schedule": crontab(minute="30", hour="15"),
    }
}