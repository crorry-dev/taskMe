"""
Serializers for notifications.
"""
from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification objects."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'priority',
            'action_url', 'action_label',
            'related_challenge_id', 'related_team_id', 'related_user_id',
            'extra_data', 'is_read', 'read_at', 'created_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'notification_type', 'title', 'message', 'priority',
            'action_url', 'action_label',
            'related_challenge_id', 'related_team_id', 'related_user_id',
            'extra_data', 'created_at', 'expires_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'email_challenge_updates', 'email_team_updates',
            'email_reward_updates', 'email_weekly_digest',
            'push_enabled', 'push_challenge_updates', 'push_team_updates',
            'push_reward_updates',
            'in_app_challenge_updates', 'in_app_team_updates', 'in_app_reward_updates',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]
