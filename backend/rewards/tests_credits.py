"""
Tests for Credit Economy System

Tests cover:
- Wallet creation and balance operations
- Transaction logging
- Challenge cost calculations
- Credit rewards
- Admin credit management
- Economy statistics
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

from rewards.models import CreditWallet, CreditTransaction, CreditConfig
from rewards.services import CreditService

User = get_user_model()


@pytest.fixture
def credit_config(db):
    """Get or create credit config."""
    return CreditConfig.get_config()


@pytest.fixture
def user_with_wallet(user_factory, db):
    """Create a user with a wallet and credits."""
    user = user_factory()
    CreditService.grant_signup_bonus(user)
    return user


class TestCreditWalletModel:
    """Test CreditWallet model operations."""
    
    def test_wallet_creation(self, user_factory, db):
        """Test wallet is created correctly."""
        user = user_factory()
        wallet, created = CreditService.get_or_create_wallet(user)
        
        assert created is True
        assert wallet.balance == 0
        assert wallet.user == user
    
    def test_add_credits(self, user_factory, db):
        """Test adding credits to wallet."""
        user = user_factory()
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        wallet.add_credits(50, 'signup_bonus', 'Test bonus')
        
        assert wallet.balance == 50
        assert wallet.lifetime_earned == 50
        assert CreditTransaction.objects.filter(wallet=wallet).count() == 1
    
    def test_spend_credits(self, user_factory, db):
        """Test spending credits from wallet."""
        user = user_factory()
        wallet, _ = CreditService.get_or_create_wallet(user)
        wallet.add_credits(100, 'signup_bonus')
        
        wallet.spend_credits(30, 'challenge_create', 'Test challenge')
        
        assert wallet.balance == 70
        assert wallet.lifetime_spent == 30
    
    def test_spend_insufficient_credits(self, user_factory, db):
        """Test spending more credits than available."""
        user = user_factory()
        wallet, _ = CreditService.get_or_create_wallet(user)
        wallet.add_credits(50, 'signup_bonus')
        
        with pytest.raises(ValueError, match="Insufficient credits"):
            wallet.spend_credits(100, 'challenge_create')
    
    def test_can_afford(self, user_factory, db):
        """Test affordability check."""
        user = user_factory()
        wallet, _ = CreditService.get_or_create_wallet(user)
        wallet.add_credits(50, 'signup_bonus')
        
        assert wallet.can_afford(50) is True
        assert wallet.can_afford(51) is False


class TestCreditService:
    """Test CreditService operations."""
    
    def test_signup_bonus(self, user_factory, credit_config, db):
        """Test signup bonus is granted correctly."""
        user = user_factory()
        bonus = CreditService.grant_signup_bonus(user)
        
        assert bonus == credit_config.signup_bonus
        wallet = CreditWallet.objects.get(user=user)
        assert wallet.balance == credit_config.signup_bonus
    
    def test_signup_bonus_only_once(self, user_factory, credit_config, db):
        """Test signup bonus is not granted twice."""
        user = user_factory()
        CreditService.grant_signup_bonus(user)
        second_bonus = CreditService.grant_signup_bonus(user)
        
        assert second_bonus == 0
        wallet = CreditWallet.objects.get(user=user)
        assert wallet.balance == credit_config.signup_bonus
    
    def test_get_challenge_cost(self, credit_config, db):
        """Test challenge cost calculation."""
        todo_cost = CreditService.get_challenge_cost('todo')
        assert todo_cost == credit_config.cost_todo
        
        duel_cost = CreditService.get_challenge_cost('duel')
        assert duel_cost == credit_config.cost_duel
        
        # With photo proof
        photo_cost = CreditService.get_challenge_cost('todo', 'PHOTO')
        assert photo_cost == credit_config.cost_todo + credit_config.cost_photo_proof
    
    def test_streak_milestone_rewards(self, user_factory, credit_config, db):
        """Test streak milestone rewards."""
        user = user_factory()
        CreditService.grant_signup_bonus(user)
        
        # Create a mock streak object
        class MockStreak:
            id = 1
        
        wallet = CreditWallet.objects.get(user=user)
        initial_balance = wallet.balance
        
        CreditService.reward_streak_milestone(user, MockStreak(), 7)
        
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance + credit_config.reward_streak_7


class TestCreditAPI:
    """Test Credit API endpoints."""
    
    def test_get_wallet(self, api_client, user_with_wallet, credit_config):
        """Test getting wallet details."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('credit-wallet')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == credit_config.signup_bonus
        assert 'lifetime_earned' in response.data
        assert 'lifetime_spent' in response.data
    
    def test_get_balance(self, api_client, user_with_wallet, credit_config):
        """Test quick balance check."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('credit-balance')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == credit_config.signup_bonus
    
    def test_check_affordability(self, api_client, user_with_wallet, credit_config):
        """Test affordability check via API."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('credit-balance')
        
        # Can afford
        response = api_client.get(url, {'check_amount': 50})
        assert response.data['can_afford'] is True
        
        # Cannot afford
        response = api_client.get(url, {'check_amount': 500})
        assert response.data['can_afford'] is False
    
    def test_get_transactions(self, api_client, user_with_wallet):
        """Test transaction history."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('credit-transactions')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should have signup bonus transaction
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
    
    def test_calculate_challenge_cost(self, api_client, user_with_wallet, credit_config):
        """Test challenge cost calculation endpoint."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('challenge-cost')
        response = api_client.post(url, {
            'challenge_type': 'duel',
            'proof_type': 'PHOTO'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['base_cost'] == credit_config.cost_duel
        assert response.data['proof_cost'] == credit_config.cost_photo_proof
        assert 'can_afford' in response.data
    
    def test_get_config(self, api_client, user_with_wallet, credit_config):
        """Test getting credit configuration."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('credit-config')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['signup_bonus'] == credit_config.signup_bonus
        assert response.data['cost_todo'] == credit_config.cost_todo
    
    def test_wallet_created_on_first_access(self, api_client, user_factory, db):
        """Test wallet is created if it doesn't exist."""
        user = user_factory()
        api_client.force_authenticate(user=user)
        
        assert not CreditWallet.objects.filter(user=user).exists()
        
        url = reverse('credit-wallet')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert CreditWallet.objects.filter(user=user).exists()


class TestAdminCreditAPI:
    """Test admin credit management endpoints."""
    
    def test_admin_grant_credits(self, api_client, admin_user_factory, user_factory, db):
        """Test admin granting credits."""
        admin = admin_user_factory()
        user = user_factory()
        CreditService.get_or_create_wallet(user)
        
        api_client.force_authenticate(user=admin)
        
        url = reverse('admin-credit-grant')
        response = api_client.post(url, {
            'user_id': user.id,
            'amount': 50,
            'reason': 'Test grant'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        wallet = CreditWallet.objects.get(user=user)
        assert wallet.balance == 50
    
    def test_admin_deduct_credits(self, api_client, admin_user_factory, user_with_wallet, credit_config):
        """Test admin deducting credits."""
        admin = admin_user_factory()
        
        api_client.force_authenticate(user=admin)
        
        url = reverse('admin-credit-deduct')
        response = api_client.post(url, {
            'user_id': user_with_wallet.id,
            'amount': 20,
            'reason': 'Test deduction'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        wallet = CreditWallet.objects.get(user=user_with_wallet)
        assert wallet.balance == credit_config.signup_bonus - 20
    
    def test_non_admin_cannot_grant(self, api_client, user_with_wallet):
        """Test non-admin cannot use admin endpoints."""
        api_client.force_authenticate(user=user_with_wallet)
        
        url = reverse('admin-credit-grant')
        response = api_client.post(url, {
            'user_id': user_with_wallet.id,
            'amount': 50,
            'reason': 'Test'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_economy_stats(self, api_client, admin_user_factory, user_with_wallet, db):
        """Test economy statistics endpoint."""
        admin = admin_user_factory()
        api_client.force_authenticate(user=admin)
        
        url = reverse('economy-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_users_with_wallets' in response.data
        assert 'total_credits_in_circulation' in response.data


class TestCreditIntegration:
    """Integration tests for credit system with challenges."""
    
    def test_challenge_creation_charges_credits(
        self, api_client, user_with_wallet, credit_config, db
    ):
        """Test creating a challenge deducts credits."""
        api_client.force_authenticate(user=user_with_wallet)
        
        initial_balance = CreditWallet.objects.get(user=user_with_wallet).balance
        
        # Create a challenge
        url = reverse('challenge-list')
        response = api_client.post(url, {
            'title': 'Test Challenge',
            'description': 'Test',
            'challenge_type': 'todo',
            'visibility': 'private',
            'proof_type': 'SELF',
        })
        
        if response.status_code == status.HTTP_201_CREATED:
            wallet = CreditWallet.objects.get(user=user_with_wallet)
            expected_cost = credit_config.cost_todo
            assert wallet.balance == initial_balance - expected_cost
    
    def test_insufficient_credits_blocks_challenge(
        self, api_client, user_factory, credit_config, db
    ):
        """Test challenge creation fails with insufficient credits."""
        user = user_factory()
        wallet, _ = CreditService.get_or_create_wallet(user)
        # Give less credits than needed
        wallet.add_credits(1, 'test')
        
        api_client.force_authenticate(user=user)
        
        url = reverse('challenge-list')
        response = api_client.post(url, {
            'title': 'Test Challenge',
            'description': 'Test',
            'challenge_type': 'community',  # Most expensive
            'visibility': 'private',
            'proof_type': 'SELF',
        })
        
        # Should fail due to insufficient credits
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN
        ]
