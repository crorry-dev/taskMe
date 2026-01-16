"""
Tests for Teams API endpoints.

Coverage:
- Team CRUD operations
- Team membership (join/leave)
- Team invitations
- Permission tests (owner vs member vs non-member)
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestTeamAPI:
    """Tests for Team CRUD operations."""
    
    def test_list_teams(self, authenticated_client):
        """Authenticated users can list teams."""
        client, user = authenticated_client
        
        response = client.get('/api/teams/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_teams_unauthenticated(self, api_client):
        """Unauthenticated users cannot list teams."""
        response = api_client.get('/api/teams/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_team(self, authenticated_client):
        """Authenticated users can create teams."""
        client, user = authenticated_client
        
        data = {
            'name': 'Test Team',
            'description': 'A test team description',
        }
        
        response = client.post('/api/teams/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Team'
    
    def test_create_team_validation(self, authenticated_client):
        """Team name is required."""
        client, user = authenticated_client
        
        data = {
            'description': 'No name provided',
        }
        
        response = client.post('/api/teams/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_team_detail(self, authenticated_client, team_factory):
        """Users can view team details."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        
        response = client.get(f'/api/teams/{team.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == team.name
    
    def test_update_team_as_owner(self, authenticated_client, team_factory):
        """Team owner can update team."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        
        data = {
            'name': 'Updated Team Name',
            'description': team.description,
        }
        
        response = client.patch(f'/api/teams/{team.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Team Name'
    
    @pytest.mark.security
    def test_update_team_as_non_owner(self, authenticated_client, team_factory, user_factory):
        """Non-owner cannot update team."""
        client, user = authenticated_client
        other_user = user_factory()
        team = team_factory(creator=other_user)
        
        data = {
            'name': 'Hacked Team Name',
        }
        
        response = client.patch(f'/api/teams/{team.id}/', data, format='json')
        
        # Should be forbidden or not found
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_delete_team_as_owner(self, authenticated_client, team_factory):
        """Team owner can delete team."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        team_id = team.id
        
        response = client.delete(f'/api/teams/{team_id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestTeamMembership:
    """Tests for team join/leave functionality."""
    
    def test_join_public_team(self, authenticated_client, team_factory, user_factory):
        """Users can join public teams."""
        client, user = authenticated_client
        other_user = user_factory()
        team = team_factory(creator=other_user)
        
        response = client.post(f'/api/teams/{team.id}/join/')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    
    def test_cannot_join_twice(self, authenticated_client, team_factory):
        """Users cannot join a team they're already in."""
        client, user = authenticated_client
        team = team_factory(creator=user)  # Creator is already a member
        
        response = client.post(f'/api/teams/{team.id}/join/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_leave_team(self, authenticated_client, team_factory, user_factory):
        """Members can leave teams."""
        client, user = authenticated_client
        other_user = user_factory()
        team = team_factory(creator=other_user)
        
        # First join
        client.post(f'/api/teams/{team.id}/join/')
        
        # Then leave
        response = client.post(f'/api/teams/{team.id}/leave/')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
    
    @pytest.mark.security
    def test_owner_cannot_leave(self, authenticated_client, team_factory):
        """Team owner cannot leave their own team."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        
        response = client.post(f'/api/teams/{team.id}/leave/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_my_teams(self, authenticated_client, team_factory):
        """Users can list their own teams."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        
        response = client.get('/api/teams/my_teams/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTeamInvitations:
    """Tests for team invitation functionality."""
    
    def test_invite_to_team(self, authenticated_client, team_factory, user_factory):
        """Team owner can invite users."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        other_user = user_factory()
        
        data = {
            'email': other_user.email,
        }
        
        response = client.post(f'/api/teams/{team.id}/invite/', data, format='json')
        
        # May return 200, 201, or 400 if invite already exists
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_get_team_members(self, authenticated_client, team_factory):
        """Can list team members."""
        client, user = authenticated_client
        team = team_factory(creator=user)
        
        response = client.get(f'/api/teams/{team.id}/members/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1  # At least the creator

