"""
pytest configuration for CommitQuest.
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    User = get_user_model()
    
    def create_user(
        email=None,
        username=None,
        password='testpass123',
        **kwargs
    ):
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        return User.objects.create_user(
            email=email or f'test_{unique_id}@example.com',
            username=username or f'testuser_{unique_id}',
            password=password,
            **kwargs
        )
    
    return create_user


@pytest.fixture
def admin_user_factory(db):
    """Factory for creating admin users."""
    User = get_user_model()
    
    def create_admin(
        email=None,
        username=None,
        password='adminpass123',
        **kwargs
    ):
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        return User.objects.create_superuser(
            email=email or f'admin_{unique_id}@example.com',
            username=username or f'admin_{unique_id}',
            password=password,
            **kwargs
        )
    
    return create_admin


@pytest.fixture
def authenticated_client(api_client, user_factory):
    """Return an authenticated API client with a test user."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def admin_client(api_client, admin_user_factory):
    """Return an authenticated API client with an admin user."""
    admin = admin_user_factory()
    api_client.force_authenticate(user=admin)
    return api_client, admin


@pytest.fixture
def team_factory(db, user_factory):
    """Factory for creating test teams."""
    from teams.models import Team, TeamMember
    
    def create_team(creator=None, **kwargs):
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        if creator is None:
            creator = user_factory()
        
        team = Team.objects.create(
            name=kwargs.get('name', f'Test Team {unique_id}'),
            description=kwargs.get('description', 'A test team'),
            creator=creator,
            **{k: v for k, v in kwargs.items() if k not in ['name', 'description']}
        )
        
        TeamMember.objects.create(
            team=team,
            user=creator,
            role='owner'
        )
        
        return team
    
    return create_team


@pytest.fixture
def challenge_factory(db, user_factory):
    """Factory for creating test challenges."""
    from challenges.models import Challenge, ChallengeParticipant
    from django.utils import timezone
    from datetime import timedelta
    
    def create_challenge(creator=None, **kwargs):
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        if creator is None:
            creator = user_factory()
        
        now = timezone.now()
        challenge = Challenge.objects.create(
            title=kwargs.get('title', f'Test Challenge {unique_id}'),
            description=kwargs.get('description', 'A test challenge'),
            challenge_type=kwargs.get('challenge_type', 'quantified'),
            status=kwargs.get('status', 'active'),
            visibility=kwargs.get('visibility', 'private'),
            goal=kwargs.get('goal', 'Complete the challenge'),
            target_value=kwargs.get('target_value', 100),
            creator=creator,
            start_date=kwargs.get('start_date', now),
            end_date=kwargs.get('end_date', now + timedelta(days=30)),
            **{k: v for k, v in kwargs.items() if k not in [
                'title', 'description', 'challenge_type', 'status',
                'visibility', 'goal', 'target_value', 'start_date', 'end_date'
            ]}
        )
        
        # Add creator as participant
        ChallengeParticipant.objects.create(
            challenge=challenge,
            user=creator,
            status='active'
        )
        
        return challenge
    
    return create_challenge


@pytest.fixture
def contribution_factory(db, challenge_factory):
    """Factory for creating test contributions."""
    from challenges.models import Contribution, ChallengeParticipant
    from django.utils import timezone
    
    def create_contribution(challenge=None, user=None, **kwargs):
        if challenge is None:
            challenge = challenge_factory()
        
        if user is None:
            user = challenge.creator
        
        # Get or create participation
        participation, _ = ChallengeParticipant.objects.get_or_create(
            challenge=challenge,
            user=user,
            defaults={'status': 'active'}
        )
        
        return Contribution.objects.create(
            participation=participation,
            value=kwargs.get('value', 10),
            note=kwargs.get('note', 'Test contribution'),
            logged_at=kwargs.get('logged_at', timezone.now()),
            status=kwargs.get('status', 'pending'),
        )
    
    return create_contribution


@pytest.fixture
def duel_factory(db, user_factory, challenge_factory):
    """Factory for creating test duels."""
    from challenges.models import Duel
    
    def create_duel(challenger=None, opponent=None, challenge=None, **kwargs):
        if challenger is None:
            challenger = user_factory()
        if opponent is None:
            opponent = user_factory()
        if challenge is None:
            challenge = challenge_factory(
                creator=challenger,
                challenge_type='duel',
                visibility='private'
            )
        
        return Duel.objects.create(
            challenge=challenge,
            challenger=challenger,
            opponent=opponent,
            status=kwargs.get('status', 'pending'),
            **{k: v for k, v in kwargs.items() if k != 'status'}
        )
    
    return create_duel


@pytest.fixture
def badge_factory(db):
    """Factory for creating test badges."""
    from rewards.models import Badge
    
    def create_badge(**kwargs):
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        
        return Badge.objects.create(
            name=kwargs.get('name', f'Test Badge {unique_id}'),
            description=kwargs.get('description', 'A test badge'),
            icon=kwargs.get('icon', '🏆'),
            badge_type=kwargs.get('badge_type', 'milestone'),
            criteria=kwargs.get('criteria', {}),
        )
    
    return create_badge
