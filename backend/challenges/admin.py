from django.contrib import admin
from .models import Challenge, ChallengeParticipant, Duel


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    """Admin interface for Challenge model."""
    
    list_display = ['title', 'challenge_type', 'status', 'creator', 'start_date', 'end_date']
    list_filter = ['challenge_type', 'status', 'start_date']
    search_fields = ['title', 'description', 'creator__username']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    """Admin interface for ChallengeParticipant model."""
    
    list_display = ['user', 'challenge', 'current_progress', 'completed', 'rank', 'points_earned']
    list_filter = ['completed', 'joined_at']
    search_fields = ['user__username', 'challenge__title']


@admin.register(Duel)
class DuelAdmin(admin.ModelAdmin):
    """Admin interface for Duel model."""
    
    list_display = ['challenger', 'opponent', 'status', 'winner', 'stake_points', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['challenger__username', 'opponent__username']
    date_hierarchy = 'created_at'

