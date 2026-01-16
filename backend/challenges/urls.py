"""
URL configuration for challenges app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ChallengeViewSet, ContributionViewSet,
    ProofViewSet, DuelViewSet, VoiceMemoViewSet
)

router = DefaultRouter()
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'contributions', ContributionViewSet, basename='contribution')
router.register(r'proofs', ProofViewSet, basename='proof')
router.register(r'duels', DuelViewSet, basename='duel')
router.register(r'voice-memos', VoiceMemoViewSet, basename='voicememo')

urlpatterns = [
    path('', include(router.urls)),
]
