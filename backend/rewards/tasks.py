"""
Celery tasks for rewards app.

Background tasks for:
- Streak verification
- Leaderboard cache updates
- Badge verification
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task(name='rewards.tasks.check_all_streaks')
def check_all_streaks():
    """
    Check all active streaks and update status.
    
    Runs daily to:
    - Send warnings for at-risk streaks
    - Break streaks that have exceeded grace period
    """
    from rewards.models import Streak
    from notifications.services import notify_streak_warning, notify_streak_broken
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Find streaks at risk
    at_risk_streaks = Streak.objects.filter(
        current_count__gt=0,
        last_activity_date__lt=yesterday,
    ).select_related('user')
    
    warned = 0
    broken = 0
    
    for streak in at_risk_streaks:
        days_missed = (today - streak.last_activity_date).days
        
        with transaction.atomic():
            if days_missed == 1 and streak.grace_used < streak.max_grace:
                # Can still use grace - send warning
                notify_streak_warning(streak.user, streak.current_count)
                warned += 1
                logger.info(f"Warned {streak.user.username} about streak at risk")
                
            elif days_missed > streak.max_grace - streak.grace_used:
                # Streak is broken
                old_count = streak.current_count
                streak.current_count = 0
                streak.grace_used = 0
                streak.save()
                
                notify_streak_broken(streak.user, old_count)
                broken += 1
                logger.info(f"Streak broken for {streak.user.username}: {old_count} days lost")
    
    logger.info(f"Streak check complete: {warned} warnings, {broken} broken")
    return {'warned': warned, 'broken': broken}


@shared_task(name='rewards.tasks.update_leaderboard_cache')
def update_leaderboard_cache():
    """
    Update cached leaderboard data.
    
    Pre-computes leaderboard rankings for faster API responses.
    """
    from django.core.cache import cache
    from django.contrib.auth import get_user_model
    from django.db.models import Sum
    
    User = get_user_model()
    
    # Global leaderboard (top 100)
    global_leaders = list(
        User.objects.filter(is_active=True)
        .order_by('-total_points')
        .values('id', 'username', 'total_points', 'level')[:100]
    )
    cache.set('leaderboard:global', global_leaders, timeout=3600)
    
    # Weekly leaderboard
    from rewards.models import RewardEvent
    week_ago = timezone.now() - timedelta(days=7)
    
    weekly_stats = (
        RewardEvent.objects.filter(created_at__gte=week_ago)
        .values('user_id', 'user__username')
        .annotate(weekly_points=Sum('points'))
        .order_by('-weekly_points')[:100]
    )
    cache.set('leaderboard:weekly', list(weekly_stats), timeout=3600)
    
    logger.info("Leaderboard cache updated")
    return {'global_count': len(global_leaders), 'weekly_count': len(weekly_stats)}


@shared_task(name='rewards.tasks.award_xp_async')
def award_xp_async(user_id, amount, reason, reason_detail=''):
    """
    Award XP to a user asynchronously.
    
    Useful for bulk operations or when immediate response not needed.
    """
    from django.contrib.auth import get_user_model
    from rewards.services import award_xp
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        award_xp(user, amount=amount, reason=reason, reason_detail=reason_detail)
        logger.info(f"Awarded {amount} XP to user {user_id}")
        return {'success': True, 'user_id': user_id, 'amount': amount}
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for XP award")
        return {'success': False, 'error': 'User not found'}


@shared_task(name='rewards.tasks.check_badges_async')
def check_badges_async(user_id):
    """
    Check and award badges for a user asynchronously.
    """
    from django.contrib.auth import get_user_model
    from rewards.services import check_and_award_badges
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        check_and_award_badges(user)
        logger.info(f"Checked badges for user {user_id}")
        return {'success': True, 'user_id': user_id}
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for badge check")
        return {'success': False, 'error': 'User not found'}
