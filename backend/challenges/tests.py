"""
Tests for Challenge API endpoints.

Security tests cover:
- Object-level permissions
- Visibility rules
- Input validation
"""
import pytest
from django.test import TestCase
from rest_framework import status


@pytest.mark.django_db
class TestChallengeAPI:
    """Tests for Challenge CRUD operations."""
    
    def test_list_challenges_authenticated(self, authenticated_client, challenge_factory):
        """Authenticated users can list their visible challenges."""
        client, user = authenticated_client
        
        # Create a challenge for this user
        challenge = challenge_factory(creator=user)
        
        response = client.get('/api/challenges/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_challenges_unauthenticated(self, api_client):
        """Unauthenticated users cannot list challenges."""
        response = api_client.get('/api/challenges/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_challenge_authenticated(self, authenticated_client):
        """Authenticated users can create challenges."""
        client, user = authenticated_client
        
        data = {
            'title': 'New Challenge',
            'description': 'Test description',
            'challenge_type': 'quantified',
            'goal': 'Complete 100 reps',
            'target_value': 100,
            'start_date': '2025-01-20T00:00:00Z',
            'end_date': '2025-02-20T00:00:00Z',
        }
        
        response = client.post('/api/challenges/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Challenge'
        assert response.data['visibility'] == 'private'  # default
    
    def test_create_challenge_invalid_dates(self, authenticated_client):
        """Cannot create challenge with end_date before start_date."""
        client, user = authenticated_client
        
        data = {
            'title': 'Invalid Challenge',
            'description': 'Test',
            'challenge_type': 'quantified',
            'goal': 'Test',
            'target_value': 100,
            'start_date': '2025-02-20T00:00:00Z',
            'end_date': '2025-01-20T00:00:00Z',  # Before start
        }
        
        response = client.post('/api/challenges/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.security
    def test_cannot_view_private_challenge(self, authenticated_client, challenge_factory, user_factory):
        """Users cannot view private challenges they don't participate in."""
        client, user = authenticated_client
        
        # Create private challenge by another user
        other_user = user_factory()
        private_challenge = challenge_factory(
            creator=other_user,
            visibility='private'
        )
        
        response = client.get(f'/api/challenges/{private_challenge.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.security
    def test_can_view_public_challenge(self, authenticated_client, challenge_factory, user_factory):
        """Users can view public challenges."""
        client, user = authenticated_client
        
        other_user = user_factory()
        public_challenge = challenge_factory(
            creator=other_user,
            visibility='public'
        )
        
        response = client.get(f'/api/challenges/{public_challenge.id}/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_join_challenge(self, authenticated_client, challenge_factory, user_factory):
        """Users can join public challenges."""
        client, user = authenticated_client
        
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='public')
        
        response = client.post(f'/api/challenges/{challenge.id}/join/')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == user.id
    
    def test_cannot_join_twice(self, authenticated_client, challenge_factory):
        """Users cannot join the same challenge twice."""
        client, user = authenticated_client
        
        # User is already creator (and participant) of this challenge
        challenge = challenge_factory(creator=user)
        
        response = client.post(f'/api/challenges/{challenge.id}/join/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.security
    def test_creator_cannot_leave(self, authenticated_client, challenge_factory):
        """Challenge creator cannot leave their own challenge."""
        client, user = authenticated_client
        
        challenge = challenge_factory(creator=user)
        
        response = client.post(f'/api/challenges/{challenge.id}/leave/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestContributionAPI:
    """Tests for Contribution endpoints."""
    
    def test_create_contribution(self, authenticated_client, challenge_factory):
        """Users can log contributions to their challenges."""
        client, user = authenticated_client
        challenge = challenge_factory(creator=user)
        
        data = {
            'challenge_id': challenge.id,
            'value': 10,
            'note': 'Completed 10 reps',
            'logged_at': '2025-01-16T10:00:00Z',
        }
        
        response = client.post('/api/contributions/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data['value']) == 10.0
    
    @pytest.mark.security
    def test_cannot_contribute_to_others_challenge(
        self, authenticated_client, challenge_factory, user_factory
    ):
        """Users cannot log contributions to challenges they don't participate in."""
        client, user = authenticated_client
        
        other_user = user_factory()
        challenge = challenge_factory(creator=other_user, visibility='private')
        
        data = {
            'challenge_id': challenge.id,
            'value': 10,
            'logged_at': '2025-01-16T10:00:00Z',
        }
        
        response = client.post('/api/contributions/', data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_cannot_log_future_contribution(self, authenticated_client, challenge_factory):
        """Cannot log contributions for the future."""
        client, user = authenticated_client
        challenge = challenge_factory(creator=user)
        
        data = {
            'challenge_id': challenge.id,
            'value': 10,
            'logged_at': '2030-01-16T10:00:00Z',  # Future date
        }
        
        response = client.post('/api/contributions/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLeaderboard:
    """Tests for leaderboard functionality."""
    
    def test_challenge_leaderboard(self, authenticated_client, challenge_factory):
        """Can retrieve challenge leaderboard."""
        client, user = authenticated_client
        challenge = challenge_factory(creator=user)
        
        response = client.get(f'/api/challenges/{challenge.id}/leaderboard/')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
