"""
Management command for daily streak maintenance.
Run via cron or Celery beat: python manage.py check_streaks
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from rewards.models import Streak
from notifications.services import notify_streak_warning, notify_streak_broken


class Command(BaseCommand):
    help = 'Check and update streak status for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Find streaks that might be at risk (no activity yesterday)
        at_risk_streaks = Streak.objects.filter(
            current_count__gt=0,
            last_activity_date__lt=yesterday,
        ).select_related('user')
        
        warned = 0
        broken = 0
        
        for streak in at_risk_streaks:
            days_missed = (today - streak.last_activity_date).days
            
            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Streak {streak.id} for {streak.user.username}: "
                    f"{days_missed} days missed, grace={streak.grace_used}/{streak.max_grace}"
                )
                continue
            
            with transaction.atomic():
                if days_missed == 1 and streak.grace_used < streak.max_grace:
                    # Can still use grace - send warning
                    notify_streak_warning(streak.user, streak.current_count)
                    warned += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warned {streak.user.username} about streak at risk"
                        )
                    )
                elif days_missed > streak.max_grace - streak.grace_used:
                    # Streak is broken
                    old_count = streak.current_count
                    streak.current_count = 0
                    streak.grace_used = 0
                    streak.save()
                    
                    notify_streak_broken(streak.user, old_count)
                    broken += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Streak broken for {streak.user.username}: {old_count} days lost"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Streak check complete: {warned} warnings, {broken} broken"
            )
        )
