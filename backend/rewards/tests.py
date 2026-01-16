"""
Tests for Rewards API endpoints.

Coverage:
- Badge listing and earning
- XP events history
- Streak tracking
- Leaderboard functionality
- Progress endpoint
- Service functions
"""
import pytest
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestBadgeAPI:
    """Tests for Badge endpoints."""
    
    def test_list_all_badges(self, authenticated_client):
        """Authenticated users can list all available badges."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/badges/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_badges_unauthenticated(self, api_client):
        """Unauthenticated users cannot access badges."""
        response = api_client.get('/api/rewards/badges/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_earned_badges(self, authenticated_client):
        """Users can list their earned badges."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/badges/earned/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestXPEventsAPI:
    """Tests for XP Events history."""
    
    def test_list_xp_events(self, authenticated_client):
        """Users can view their XP event history."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/events/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_xp_events_only_own(self, authenticated_client, user_factory):
        """Users only see their own XP events."""
        client, user = authenticated_client
        other_user = user_factory()
        
        # Create XP event for other user
        from rewards.models import RewardEvent
        RewardEvent.objects.create(
            user=other_user,
            event_type='contribution_approved',
            points=10,
            description='Test event'
        )
        
        response = client.get('/api/rewards/events/')
        
        assert response.status_code == status.HTTP_200_OK
        # Should not contain other user's events
        for event in response.data.get('results', response.data):
            assert event.get('user') != other_user.id


@pytest.mark.django_db
class TestStreakAPI:
    """Tests for Streak endpoints."""
    
    def test_list_streaks(self, authenticated_client):
        """Users can view their active streaks."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/streaks/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProgressAPI:
    """Tests for Progress/Stats endpoint."""
    
    def test_get_progress(self, authenticated_client):
        """Users can view their progress summary."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/progress/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert isinstance(data, dict)


@pytest.mark.django_db
class TestLeaderboardAPI:
    """Tests for Leaderboard functionality."""
    
    def test_global_leaderboard(self, authenticated_client):
        """Users can view global leaderboard."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/leaderboard/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_weekly_leaderboard(self, authenticated_client):
        """Users can view weekly leaderboard."""
        client, user = authenticated_client
        
        response = client.get('/api/rewards/leaderboard/?period=weekly')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRewardServices:
    """Tests for reward service functions."""
    
    def test_award_xp(self, user_factory):
        """award_xp correctly adds XP and handles level-ups."""
        from rewards.services import award_xp
        
        user = user_factory()
        initial_xp = user.total_points
        
        award_xp(user, amount=50, reason='test', reason_detail='Test XP award')
        
        user.refresh_from_db()
        assert user.total_points == initial_xp + 50
    
    def test_award_xp_level_up(self, user_factory):
        """award_xp triggers level-up when threshold reached."""
        from rewards.services import award_xp, xp_for_level
        
        user = user_factory()
        user.total_points = 0
        user.level = 1
        user.save()
        
        # Award enough XP to level up
        xp_needed = xp_for_level(2) + 1
        award_xp(user, amount=xp_needed, reason='test', reason_detail='Level up test')
        
        user.refresh_from_db()
        assert user.level >= 2
    
    def test_update_streak(self, user_factory, challenge_factory):
        """update_streak correctly tracks consecutive days."""
        from rewards.services import update_streak
        from rewards.models import Streak
        
        user = user_factory()
        challenge = challenge_factory(creator=user)
        
        # First streak update
        update_streak(user, 'daily', challenge.id)
        
        streak = Streak.objects.filter(user=user, streak_type='daily').first()
        assert streak is not None
        assert streak.current_count >= 1
    
    def test_check_and_award_badges(self, user_factory):
        """check_and_award_badges runs without error."""
        from rewards.services import check_and_award_badges
        
        user = user_factory()
        
        # Should not error
        check_and_award_badges(user)
    
    def test_get_user_stats(self, user_factory):
        """get_user_stats returns comprehensive stats."""
        from rewards.services import get_user_stats
        
        user = user_factory()
        
        stats = get_user_stats(user)
        
        assert 'total_xp' in stats
        assert 'level' in stats
        assert 'badges_count' in stats


@pytest.mark.django_db
class TestXPCalculations:
    """Tests for XP calculation functions."""
    
    def test_xp_for_level_progression(self):
        """XP requirements increase with level."""
        from rewards.services import xp_for_level
        
        level_1_xp = xp_for_level(1)
        level_2_xp = xp_for_level(2)
        level_10_xp = xp_for_level(10)
        
        assert level_1_xp == 0  # Level 1 requires 0 XP
        assert level_2_xp > level_1_xp
        assert level_10_xp > level_2_xp
    
    def test_calculate_level_from_xp(self):
        """calculate_level correctly determines level from XP."""
        from rewards.services import calculate_level
        
        # 0 XP = level 1
        assert calculate_level(0) == 1
        
        # High XP = high level
        assert calculate_level(10000) > 1

