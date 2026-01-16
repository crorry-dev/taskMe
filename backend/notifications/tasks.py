"""
Celery tasks for notifications app.

Background tasks for:
- Notification cleanup
- Email notifications
- Push notification delivery
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='notifications.tasks.cleanup_old_notifications')
def cleanup_old_notifications(days=30):
    """
    Delete notifications older than specified days.
    
    Runs weekly to prevent database bloat.
    """
    from notifications.models import Notification
    
    cutoff = timezone.now() - timedelta(days=days)
    
    # Only delete read notifications
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=cutoff
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old notifications")
    return {'deleted': deleted_count}


@shared_task(name='notifications.tasks.send_notification_email')
def send_notification_email(user_id, notification_id):
    """
    Send email notification to user.
    
    Checks user preferences before sending.
    """
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings
    from notifications.models import Notification, NotificationPreference
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        notification = Notification.objects.get(id=notification_id)
        
        # Check preferences
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        
        # Map notification type to preference
        should_send = False
        if notification.notification_type in ['badge_earned', 'level_up', 'streak_milestone']:
            should_send = prefs.email_reward_updates
        elif notification.notification_type in ['challenge_invite', 'challenge_completed']:
            should_send = prefs.email_challenge_updates
        elif notification.notification_type in ['team_invite']:
            should_send = prefs.email_team_updates
        
        if not should_send:
            logger.info(f"Email notification skipped for user {user_id} (preference)")
            return {'sent': False, 'reason': 'user_preference'}
        
        # Send email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent to {user.email}")
        return {'sent': True, 'user_id': user_id}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'sent': False, 'error': 'user_not_found'}
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'sent': False, 'error': 'notification_not_found'}
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {'sent': False, 'error': str(e)}


@shared_task(name='notifications.tasks.send_streak_reminders')
def send_streak_reminders():
    """
    Send daily reminders to users with active streaks.
    
    Runs in the evening to remind users to maintain their streak.
    """
    from notifications.models import Notification, NotificationPreference
    from rewards.models import Streak
    
    today = timezone.now().date()
    
    # Find users with active streaks who haven't contributed today
    at_risk_streaks = Streak.objects.filter(
        current_count__gt=0,
        last_activity_date__lt=today,
    ).select_related('user')
    
    reminders_sent = 0
    
    for streak in at_risk_streaks:
        # Check if user wants reminders
        prefs, _ = NotificationPreference.objects.get_or_create(user=streak.user)
        
        # Create in-app reminder
        Notification.objects.create(
            user=streak.user,
            notification_type='streak_warning',
            title='Don\'t lose your streak! 🔥',
            message=f'Your {streak.current_count}-day streak is at risk. Complete a task today!',
            priority='high',
            action_url='/challenges',
            action_label='Complete a Task'
        )
        reminders_sent += 1
    
    logger.info(f"Sent {reminders_sent} streak reminders")
    return {'reminders_sent': reminders_sent}
