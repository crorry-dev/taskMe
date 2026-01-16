"""
Celery configuration for CommitQuest.

This module configures Celery for background task processing.
Tasks include:
- Streak checks
- Notification delivery
- Email sending
- Cleanup jobs
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskme_project.settings')

# Create Celery app
app = Celery('taskme_project')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    # Check streaks daily at 2 AM
    'check-streaks-daily': {
        'task': 'rewards.tasks.check_all_streaks',
        'schedule': crontab(hour=2, minute=0),
    },
    # Clean old notifications weekly
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
    },
    # Update leaderboard cache every hour
    'update-leaderboard-cache': {
        'task': 'rewards.tasks.update_leaderboard_cache',
        'schedule': crontab(minute=0),  # Every hour
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
