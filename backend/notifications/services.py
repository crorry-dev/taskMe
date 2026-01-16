"""
Notification service for creating and managing notifications.
"""
from django.utils import timezone
from .models import Notification, NotificationPreference


def get_or_create_preferences(user):
    """Get or create notification preferences for a user."""
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def should_send_notification(user, notification_type):
    """Check if user wants to receive this type of notification."""
    prefs = get_or_create_preferences(user)
    
    # Map notification types to preference fields
    challenge_types = ['challenge_invite', 'challenge_reminder', 'challenge_completed',
                       'duel_request', 'duel_accepted', 'duel_declined', 'duel_won', 'duel_lost']
    team_types = ['team_invite', 'team_joined', 'team_left', 'team_nudge']
    reward_types = ['badge_earned', 'level_up', 'streak_milestone', 'streak_warning', 'streak_broken',
                    'proof_approved', 'proof_rejected']
    
    if notification_type in challenge_types:
        return prefs.in_app_challenge_updates
    elif notification_type in team_types:
        return prefs.in_app_team_updates
    elif notification_type in reward_types:
        return prefs.in_app_reward_updates
    
    return True  # System notifications always sent


def create_notification(
    user,
    notification_type,
    title,
    message,
    priority='normal',
    action_url='',
    action_label='',
    related_challenge_id=None,
    related_team_id=None,
    related_user_id=None,
    extra_data=None,
    expires_at=None,
):
    """
    Create a notification for a user.
    
    Respects user notification preferences.
    """
    if not should_send_notification(user, notification_type):
        return None
    
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url,
        action_label=action_label,
        related_challenge_id=related_challenge_id,
        related_team_id=related_team_id,
        related_user_id=related_user_id,
        extra_data=extra_data or {},
        expires_at=expires_at,
    )
    
    return notification


def notify_badge_earned(user, badge_name, badge_icon='🏆'):
    """Send notification when user earns a badge."""
    return create_notification(
        user=user,
        notification_type='badge_earned',
        title='New Badge Earned! 🎉',
        message=f'Congratulations! You earned the "{badge_name}" badge!',
        priority='high',
        action_url='/profile#badges',
        action_label='View Badges',
        extra_data={'badge_name': badge_name, 'badge_icon': badge_icon}
    )


def notify_level_up(user, new_level):
    """Send notification when user levels up."""
    return create_notification(
        user=user,
        notification_type='level_up',
        title=f'Level Up! 🚀 You are now Level {new_level}',
        message=f'Amazing progress! You\'ve reached Level {new_level}. Keep going!',
        priority='high',
        action_url='/profile',
        action_label='View Profile',
        extra_data={'new_level': new_level}
    )


def notify_streak_milestone(user, streak_count, streak_type='daily'):
    """Send notification for streak milestones."""
    return create_notification(
        user=user,
        notification_type='streak_milestone',
        title=f'{streak_count}-Day Streak! 🔥',
        message=f'Incredible! You\'ve maintained a {streak_count}-day streak. You\'re on fire!',
        priority='high',
        extra_data={'streak_count': streak_count, 'streak_type': streak_type}
    )


def notify_streak_warning(user, streak_count):
    """Warn user their streak is at risk."""
    return create_notification(
        user=user,
        notification_type='streak_warning',
        title='Streak at Risk! ⚠️',
        message=f'Your {streak_count}-day streak is about to break! Complete a task today to keep it going.',
        priority='high',
        action_url='/challenges',
        action_label='Complete a Task',
        extra_data={'streak_count': streak_count}
    )


def notify_streak_broken(user, lost_streak_count):
    """Notify user their streak was broken."""
    return create_notification(
        user=user,
        notification_type='streak_broken',
        title='Streak Broken 💔',
        message=f'Your {lost_streak_count}-day streak has ended. Start a new one today!',
        priority='normal',
        action_url='/challenges',
        action_label='Start Fresh',
        extra_data={'lost_streak_count': lost_streak_count}
    )


def notify_proof_approved(user, challenge_title):
    """Notify user their proof was approved."""
    return create_notification(
        user=user,
        notification_type='proof_approved',
        title='Proof Approved! ✅',
        message=f'Your proof for "{challenge_title}" was approved. XP awarded!',
        priority='normal',
        extra_data={'challenge_title': challenge_title}
    )


def notify_proof_rejected(user, challenge_title, reason=''):
    """Notify user their proof was rejected."""
    return create_notification(
        user=user,
        notification_type='proof_rejected',
        title='Proof Needs Revision',
        message=f'Your proof for "{challenge_title}" was not approved. {reason}',
        priority='normal',
        extra_data={'challenge_title': challenge_title, 'reason': reason}
    )


def notify_duel_request(user, challenger_name, challenge_title, duel_id):
    """Notify user of a duel challenge."""
    return create_notification(
        user=user,
        notification_type='duel_request',
        title='Duel Challenge! ⚔️',
        message=f'{challenger_name} has challenged you to "{challenge_title}"',
        priority='high',
        action_url=f'/challenges/duel/{duel_id}',
        action_label='View Duel',
        related_user_id=duel_id,
        extra_data={'challenger_name': challenger_name, 'challenge_title': challenge_title}
    )


def notify_team_invite(user, team_name, inviter_name, team_id):
    """Notify user of a team invitation."""
    return create_notification(
        user=user,
        notification_type='team_invite',
        title='Team Invitation 👥',
        message=f'{inviter_name} invited you to join "{team_name}"',
        priority='normal',
        action_url=f'/teams/{team_id}',
        action_label='View Team',
        related_team_id=team_id,
        extra_data={'team_name': team_name, 'inviter_name': inviter_name}
    )


def notify_challenge_completed(user, challenge_title, xp_earned, challenge_id):
    """Notify user they completed a challenge."""
    return create_notification(
        user=user,
        notification_type='challenge_completed',
        title='Challenge Complete! 🏆',
        message=f'You completed "{challenge_title}" and earned {xp_earned} XP!',
        priority='high',
        action_url=f'/challenges/{challenge_id}',
        action_label='View Challenge',
        related_challenge_id=challenge_id,
        extra_data={'challenge_title': challenge_title, 'xp_earned': xp_earned}
    )


def get_unread_count(user):
    """Get count of unread notifications for a user."""
    return Notification.objects.filter(user=user, is_read=False).count()


def mark_all_as_read(user):
    """Mark all notifications as read for a user."""
    Notification.objects.filter(user=user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )


def delete_old_notifications(user, days=30):
    """Delete notifications older than specified days."""
    cutoff = timezone.now() - timezone.timedelta(days=days)
    Notification.objects.filter(user=user, created_at__lt=cutoff).delete()
