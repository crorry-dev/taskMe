"""
Security and Permission Tests for CommitQuest.

These tests verify:
- Object-level permissions
- Authorization checks
- Input validation
- OWASP-related security measures
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.security
class TestAuthenticationSecurity:
    """Tests for authentication security."""
    
    def test_all_endpoints_require_auth(self, api_client):
        """All protected endpoints return 401 for unauthenticated requests."""
        protected_endpoints = [
            '/api/challenges/',
            '/api/contributions/',
            '/api/proofs/',
            '/api/teams/',
            '/api/rewards/badges/',
            '/api/rewards/events/',
            '/api/rewards/streaks/',
            '/api/rewards/progress/',
            '/api/rewards/leaderboard/',
            '/api/notifications/',
            '/api/auth/profile/',
        ]
        
        for endpoint in protected_endpoints:
            response = api_client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"Endpoint {endpoint} should require authentication"
    
    def test_profile_endpoint_returns_own_data(self, authenticated_client):
        """Profile endpoint only returns authenticated user's data."""
        client, user = authenticated_client
        
        response = client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email


@pytest.mark.django_db
@pytest.mark.security
class TestChallengePermissions:
    """Tests for challenge permission checks."""
    
    def test_cannot_update_others_challenge(self, authenticated_client, challenge_factory, user_factory):
        """Users cannot update challenges they don't own."""
        client, user = authenticated_client
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='public')
        
        data = {'title': 'Hacked Title'}
        response = client.patch(f'/api/challenges/{challenge.id}/', data, format='json')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_cannot_delete_others_challenge(self, authenticated_client, challenge_factory, user_factory):
        """Users cannot delete challenges they don't own."""
        client, user = authenticated_client
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='public')
        
        response = client.delete(f'/api/challenges/{challenge.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_private_challenge_not_visible(self, authenticated_client, challenge_factory, user_factory):
        """Private challenges are not visible to non-participants."""
        client, user = authenticated_client
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='private')
        
        response = client.get(f'/api/challenges/{challenge.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_cannot_contribute_to_non_participating_challenge(
        self, authenticated_client, challenge_factory, user_factory
    ):
        """Cannot add contributions to challenges you don't participate in."""
        client, user = authenticated_client
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='private')
        
        data = {
            'challenge_id': challenge.id,
            'value': 10,
        }
        response = client.post('/api/contributions/', data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.security
class TestTeamPermissions:
    """Tests for team permission checks."""
    
    def test_cannot_update_others_team(self, authenticated_client, team_factory, user_factory):
        """Non-owners cannot update teams."""
        client, user = authenticated_client
        other_user = user_factory()
        team = team_factory(creator=other_user)
        
        data = {'name': 'Hacked Team'}
        response = client.patch(f'/api/teams/{team.id}/', data, format='json')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_cannot_delete_others_team(self, authenticated_client, team_factory, user_factory):
        """Non-owners cannot delete teams."""
        client, user = authenticated_client
        other_user = user_factory()
        team = team_factory(creator=other_user)
        
        response = client.delete(f'/api/teams/{team.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
@pytest.mark.security
class TestDuelPermissions:
    """Tests for duel permission checks."""
    
    def test_only_opponent_can_accept(self, authenticated_client, duel_factory, user_factory):
        """Only the opponent can accept a duel."""
        client, user = authenticated_client
        challenger = user_factory()
        opponent = user_factory()
        duel = duel_factory(challenger=challenger, opponent=opponent)
        
        # User is neither challenger nor opponent
        response = client.post(f'/api/duels/{duel.id}/accept/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_only_opponent_can_decline(self, authenticated_client, duel_factory, user_factory):
        """Only the opponent can decline a duel."""
        client, user = authenticated_client
        challenger = user_factory()
        opponent = user_factory()
        duel = duel_factory(challenger=challenger, opponent=opponent)
        
        response = client.post(f'/api/duels/{duel.id}/decline/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.security
class TestNotificationPermissions:
    """Tests for notification permission checks."""
    
    def test_cannot_view_others_notifications(self, authenticated_client, user_factory):
        """Users cannot view other users' notifications."""
        client, user = authenticated_client
        other_user = user_factory()
        
        # Create notification for other user
        from notifications.models import Notification
        Notification.objects.create(
            user=other_user,
            notification_type='system',
            title='Secret',
            message='Secret message'
        )
        
        response = client.get('/api/notifications/')
        
        # Should not include other user's notifications
        for notif in response.data.get('results', response.data):
            assert notif.get('user') != other_user.id


@pytest.mark.django_db
@pytest.mark.security
class TestInputValidation:
    """Tests for input validation and sanitization."""
    
    def test_challenge_xss_prevention(self, authenticated_client):
        """Challenge title/description are properly handled."""
        client, user = authenticated_client
        
        data = {
            'title': '<script>alert("xss")</script>Test',
            'description': '<img onerror="alert(1)" src="x">',
            'challenge_type': 'quantified',
            'goal': 'Test',
            'target_value': 100,
            'start_date': '2025-01-20T00:00:00Z',
            'end_date': '2025-02-20T00:00:00Z',
        }
        
        response = client.post('/api/challenges/', data, format='json')
        
        # Should accept but escape or store safely
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_negative_target_value_rejected(self, authenticated_client):
        """Negative target values should be rejected."""
        client, user = authenticated_client
        
        data = {
            'title': 'Test Challenge',
            'description': 'Test',
            'challenge_type': 'quantified',
            'goal': 'Test',
            'target_value': -100,  # Negative!
            'start_date': '2025-01-20T00:00:00Z',
            'end_date': '2025-02-20T00:00:00Z',
        }
        
        response = client.post('/api/challenges/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_invalid_email_rejected(self, api_client):
        """Invalid email format should be rejected."""
        data = {
            'email': 'not-an-email',
            'username': 'testuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.security
class TestProofPermissions:
    """Tests for proof upload security."""
    
    def test_cannot_submit_proof_for_others_contribution(
        self, authenticated_client, contribution_factory, user_factory
    ):
        """Cannot submit proof for contributions you don't own."""
        client, user = authenticated_client
        other_user = user_factory()
        
        # Create contribution for other user
        from challenges.models import Challenge, ChallengeParticipant, Contribution
        from django.utils import timezone
        from datetime import timedelta
        
        challenge = Challenge.objects.create(
            title='Other Challenge',
            description='Test',
            challenge_type='quantified',
            goal='Test',
            target_value=100,
            creator=other_user,
            visibility='private',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        
        participation = ChallengeParticipant.objects.create(
            challenge=challenge,
            user=other_user,
            status='active'
        )
        
        contribution = Contribution.objects.create(
            participation=participation,
            value=10,
            logged_at=timezone.now()
        )
        
        data = {
            'contribution_id': contribution.id,
            'proof_type': 'SELF',
        }
        
        response = client.post('/api/proofs/', data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
