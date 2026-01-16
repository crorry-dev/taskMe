"""
Notification models for in-app notifications.
Supports multiple notification types with read/unread status.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """
    User notification model.
    
    Supports various notification types for challenges, teams, rewards, etc.
    """
    
    NOTIFICATION_TYPES = [
        ('challenge_invite', 'Challenge Invitation'),
        ('challenge_reminder', 'Challenge Reminder'),
        ('challenge_completed', 'Challenge Completed'),
        ('duel_request', 'Duel Request'),
        ('duel_accepted', 'Duel Accepted'),
        ('duel_declined', 'Duel Declined'),
        ('duel_won', 'Duel Won'),
        ('duel_lost', 'Duel Lost'),
        ('proof_approved', 'Proof Approved'),
        ('proof_rejected', 'Proof Rejected'),
        ('proof_review_request', 'Proof Review Request'),
        ('team_invite', 'Team Invitation'),
        ('team_joined', 'Team Member Joined'),
        ('team_left', 'Team Member Left'),
        ('team_nudge', 'Team Nudge'),
        ('badge_earned', 'Badge Earned'),
        ('level_up', 'Level Up'),
        ('streak_milestone', 'Streak Milestone'),
        ('streak_warning', 'Streak At Risk'),
        ('streak_broken', 'Streak Broken'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    
    # Recipient
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Content
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Optional action link
    action_url = models.CharField(max_length=500, blank=True)
    action_label = models.CharField(max_length=50, blank=True)
    
    # Related objects (optional)
    related_challenge_id = models.IntegerField(null=True, blank=True)
    related_team_id = models.IntegerField(null=True, blank=True)
    related_user_id = models.IntegerField(null=True, blank=True)
    
    # Extra data as JSON
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'notification_type']),
        ]
    
    def __str__(self):
        return f"{self.notification_type}: {self.title} -> {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class NotificationPreference(models.Model):
    """
    User notification preferences.
    Controls which notification types user wants to receive.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_challenge_updates = models.BooleanField(default=True)
    email_team_updates = models.BooleanField(default=True)
    email_reward_updates = models.BooleanField(default=True)
    email_weekly_digest = models.BooleanField(default=True)
    
    # Push preferences (for future mobile app)
    push_enabled = models.BooleanField(default=True)
    push_challenge_updates = models.BooleanField(default=True)
    push_team_updates = models.BooleanField(default=True)
    push_reward_updates = models.BooleanField(default=True)
    
    # In-app preferences
    in_app_challenge_updates = models.BooleanField(default=True)
    in_app_team_updates = models.BooleanField(default=True)
    in_app_reward_updates = models.BooleanField(default=True)
    
    # Quiet hours (don't send push during these hours)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Notification preferences"
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
