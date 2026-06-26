from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "symptomap_agents",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.agents.summarizer", "app.agents.triage", "app.agents.forecaster"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Configure periodic tasks (CRON) for the forecaster
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "daily-epidemiological-forecast": {
        "task": "app.agents.forecaster.generate_daily_briefing",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 AM UTC
    },
}
