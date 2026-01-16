"""
Tests for Accounts API endpoints.

Security tests cover:
- Authentication
- Rate limiting awareness
- Input validation
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_user_creation(self):
        """Test creating a user."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str(self):
        """Test user string representation."""
        self.assertEqual(str(self.user), 'test@example.com')

    def test_add_points(self):
        """Test adding points to user."""
        initial_points = self.user.total_points
        self.user.add_points(50)
        self.assertEqual(self.user.total_points, initial_points + 50)

    def test_level_calculation(self):
        """Test level calculation based on points."""
        self.user.add_points(250)
        # 250 points / 100 points per level = level 3 (starting from 1)
        self.assertEqual(self.user.level, 3)


@pytest.mark.django_db
class TestAuthAPI:
    """Tests for authentication endpoints."""
    
    def test_register_user(self, api_client):
        """Users can register with valid data."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
    
    def test_register_duplicate_email(self, api_client, user_factory):
        """Cannot register with duplicate email."""
        existing_user = user_factory(email='existing@example.com')
        
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'SecureP@ss123',
            'password_confirm': 'SecureP@ss123',
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client):
        """Cannot register with weak password."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': '123',
            'password_confirm': '123',
        }
        
        response = api_client.post('/api/auth/register/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_valid_credentials(self, api_client, user_factory):
        """Users can login with valid credentials."""
        user = user_factory(password='testpass123')
        
        data = {
            'email': user.email,
            'password': 'testpass123',
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        # SimpleJWT returns 'access' and 'refresh' tokens directly
        assert 'access' in response.data or 'tokens' in response.data
    
    def test_login_invalid_credentials(self, api_client, user_factory):
        """Cannot login with invalid credentials."""
        user = user_factory(password='testpass123')
        
        data = {
            'email': user.email,
            'password': 'wrongpassword',
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, authenticated_client):
        """Authenticated users can get their profile."""
        client, user = authenticated_client
        
        response = client.get('/api/auth/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Unauthenticated users cannot get profile."""
        response = api_client.get('/api/auth/me/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Tests for user profile management."""
    
    def test_update_profile(self, authenticated_client):
        """Users can update their profile."""
        client, user = authenticated_client
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        
        response = client.patch('/api/auth/me/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
    
    @pytest.mark.security
    def test_cannot_change_email_to_existing(self, authenticated_client, user_factory):
        """Cannot change email to one that already exists."""
        client, user = authenticated_client
        other_user = user_factory(email='taken@example.com')
        
        data = {'email': 'taken@example.com'}
        
        response = client.patch('/api/auth/me/', data, format='json')
        
        # Should either fail with 400 (validation) or succeed but not allow duplicate
        # The exact behavior depends on the serializer implementation
        if response.status_code == status.HTTP_200_OK:
            # If update succeeds, email should NOT have changed to duplicate
            user.refresh_from_db()
            assert user.email != 'taken@example.com' or response.status_code == status.HTTP_400_BAD_REQUEST
        else:
            assert response.status_code == status.HTTP_400_BAD_REQUEST

