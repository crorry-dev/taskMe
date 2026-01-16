"""
URL configuration for rewards app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BadgeViewSet, RewardEventViewSet, StreakViewSet,
    UserProgressView, LeaderboardView,
    # Credit views
    CreditWalletView, CreditBalanceView, CreditTransactionListView,
    ChallengeCostView, CreditConfigView, CreditPurchaseView,
    AdminCreditGrantView, AdminCreditDeductView, EconomyStatsView
)

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'events', RewardEventViewSet, basename='reward-event')
router.register(r'streaks', StreakViewSet, basename='streak')

urlpatterns = [
    path('', include(router.urls)),
    path('progress/', UserProgressView.as_view(), name='user-progress'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    
    # Credit Economy endpoints
    path('credits/', CreditWalletView.as_view(), name='credit-wallet'),
    path('credits/balance/', CreditBalanceView.as_view(), name='credit-balance'),
    path('credits/transactions/', CreditTransactionListView.as_view(), name='credit-transactions'),
    path('credits/cost/', ChallengeCostView.as_view(), name='challenge-cost'),
    path('credits/config/', CreditConfigView.as_view(), name='credit-config'),
    path('credits/add/', CreditPurchaseView.as_view(), name='credit-purchase'),
    
    # Admin credit management
    path('credits/admin/grant/', AdminCreditGrantView.as_view(), name='admin-credit-grant'),
    path('credits/admin/deduct/', AdminCreditDeductView.as_view(), name='admin-credit-deduct'),
    path('credits/admin/stats/', EconomyStatsView.as_view(), name='economy-stats'),
]
