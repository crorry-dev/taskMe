"""
Debug Feedback URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DebugFeedbackViewSet, DebugConfigView, DebugStatsView

router = DefaultRouter()
router.register(r'feedback', DebugFeedbackViewSet, basename='debug-feedback')
router.register(r'config', DebugConfigView, basename='debug-config')
router.register(r'stats', DebugStatsView, basename='debug-stats')

urlpatterns = [
    path('', include(router.urls)),
]
