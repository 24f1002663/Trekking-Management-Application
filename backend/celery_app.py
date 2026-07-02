from celery import Celery
from celery.schedules import crontab


def make_celery(app):
    """Create and configure a Celery instance tied to the Flask app."""

    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    )

    # NOTE: broker/backend are already set above. We deliberately do NOT copy
    # the whole Flask config into Celery — that would mix old-style CELERY_*
    # keys with Celery 5's new-style keys and raise ImproperlyConfigured.

    # Periodic beat schedule (replaces APScheduler cron jobs)
    celery.conf.beat_schedule = {
        "send-daily-user-reminders": {
            "task": "scheduler.send_daily_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "send-daily-staff-reminders": {
            "task": "scheduler.send_staff_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "send-monthly-admin-report": {
            "task": "scheduler.send_monthly_report",
            "schedule": crontab(hour=7, minute=0, day_of_month="1"),
        },
    }

    celery.conf.timezone = "Asia/Kolkata"

    # Make every Celery task run inside a Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
