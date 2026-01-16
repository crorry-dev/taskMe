"""
Debug Feedback App Configuration
"""
from django.apps import AppConfig


class DebugFeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'debug_feedback'
    verbose_name = 'Debug Feedback System'
