"""
Tests for Notifications API endpoints.

Coverage:
- Notification listing
- Mark as read
- Preferences management
- Permission tests
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestNotificationAPI:
    """Tests for Notification CRUD operations."""
    
    def test_list_notifications(self, authenticated_client):
        """Authenticated users can list their notifications."""
        client, user = authenticated_client
        
        response = client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_notifications_unauthenticated(self, api_client):
        """Unauthenticated users cannot list notifications."""
        response = api_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_unread_count(self, authenticated_client):
        """Users can get unread notification count."""
        client, user = authenticated_client
        
        response = client.get('/api/notifications/unread_count/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_mark_notification_read(self, authenticated_client):
        """Users can mark a notification as read."""
        client, user = authenticated_client
        
        # Create a notification
        from notifications.models import Notification
        notification = Notification.objects.create(
            user=user,
            notification_type='system',
            title='Test Notification',
            message='This is a test'
        )
        
        response = client.post(f'/api/notifications/{notification.id}/mark_read/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it's marked as read
        notification.refresh_from_db()
        assert notification.is_read is True
    
    def test_mark_all_read(self, authenticated_client):
        """Users can mark all notifications as read."""
        client, user = authenticated_client
        
        # Create multiple notifications
        from notifications.models import Notification
        for i in range(3):
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=f'Test Notification {i}',
                message='This is a test'
            )
        
        response = client.post('/api/notifications/mark_all_read/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify all are read
        unread = Notification.objects.filter(user=user, is_read=False).count()
        assert unread == 0
    
    @pytest.mark.security
    def test_cannot_mark_other_user_notification(self, authenticated_client, user_factory):
        """Users cannot mark other users' notifications as read."""
        client, user = authenticated_client
        other_user = user_factory()
        
        # Create notification for other user
        from notifications.models import Notification
        notification = Notification.objects.create(
            user=other_user,
            notification_type='system',
            title='Other User Notification',
            message='This is a test'
        )
        
        response = client.post(f'/api/notifications/{notification.id}/mark_read/')
        
        # Should be not found (filtered by user)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_clear_all_notifications(self, authenticated_client):
        """Users can clear all their notifications."""
        client, user = authenticated_client
        
        # Create notifications
        from notifications.models import Notification
        Notification.objects.create(
            user=user,
            notification_type='system',
            title='Test',
            message='Test'
        )
        
        response = client.post('/api/notifications/clear_all/')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


@pytest.mark.django_db
class TestNotificationPreferences:
    """Tests for notification preferences."""
    
    def test_get_preferences(self, authenticated_client):
        """Users can get their notification preferences."""
        client, user = authenticated_client
        
        response = client.get('/api/notifications/preferences/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_preferences(self, authenticated_client):
        """Users can update their notification preferences."""
        client, user = authenticated_client
        
        data = {
            'in_app_challenge_updates': False,
        }
        
        response = client.patch('/api/notifications/preferences/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestNotificationServices:
    """Tests for notification service functions."""
    
    def test_create_notification(self, user_factory):
        """create_notification creates notification correctly."""
        from notifications.services import create_notification
        
        user = user_factory()
        
        notification = create_notification(
            user=user,
            notification_type='system',
            title='Test Title',
            message='Test Message',
            priority='high'
        )
        
        assert notification is not None
        assert notification.title == 'Test Title'
        assert notification.priority == 'high'
    
    def test_notify_badge_earned(self, user_factory):
        """notify_badge_earned creates correct notification."""
        from notifications.services import notify_badge_earned
        
        user = user_factory()
        
        notification = notify_badge_earned(user, 'First Steps', '🎯')
        
        assert notification is not None
        assert 'First Steps' in notification.message
    
    def test_notify_level_up(self, user_factory):
        """notify_level_up creates correct notification."""
        from notifications.services import notify_level_up
        
        user = user_factory()
        
        notification = notify_level_up(user, 5)
        
        assert notification is not None
        assert '5' in notification.title or '5' in notification.message
    
    def test_get_unread_count(self, user_factory):
        """get_unread_count returns correct count."""
        from notifications.services import get_unread_count
        from notifications.models import Notification
        
        user = user_factory()
        
        # Create some notifications
        for i in range(3):
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=f'Test {i}',
                message='Test'
            )
        
        count = get_unread_count(user)
        
        assert count == 3
    
    def test_mark_all_as_read(self, user_factory):
        """mark_all_as_read marks all notifications."""
        from notifications.services import mark_all_as_read
        from notifications.models import Notification
        
        user = user_factory()
        
        # Create notifications
        for i in range(3):
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=f'Test {i}',
                message='Test'
            )
        
        mark_all_as_read(user)
        
        unread = Notification.objects.filter(user=user, is_read=False).count()
        assert unread == 0
