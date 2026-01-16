"""
Signal handlers for the rewards app.

Handles automatic credit grants, badge awards, etc.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .services import CreditService


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def grant_signup_bonus(sender, instance, created, **kwargs):
    """
    Grant signup bonus credits when a new user is created.
    """
    if created:
        # Use transaction.on_commit to avoid issues with user creation flow
        from django.db import transaction
        transaction.on_commit(lambda: CreditService.grant_signup_bonus(instance))
