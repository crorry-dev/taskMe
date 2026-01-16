from django.test import TestCase
from django.contrib.auth import get_user_model

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

