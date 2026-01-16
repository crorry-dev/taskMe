from django.contrib import admin
from .models import Reward, UserReward, Achievement, UserAchievement


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """Admin interface for Reward model."""
    
    list_display = ['name', 'reward_type', 'points_cost', 'is_available', 'is_redeemable']
    list_filter = ['reward_type', 'is_available', 'is_redeemable']
    search_fields = ['name', 'description']
    ordering = ['points_cost']


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    """Admin interface for UserReward model."""
    
    list_display = ['user', 'reward', 'is_redeemed', 'earned_at', 'redeemed_at']
    list_filter = ['is_redeemed', 'earned_at']
    search_fields = ['user__username', 'reward__name']
    date_hierarchy = 'earned_at'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin interface for Achievement model."""
    
    list_display = ['name', 'required_tasks', 'required_points', 'reward_points', 'is_hidden']
    list_filter = ['is_hidden', 'created_at']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin interface for UserAchievement model."""
    
    list_display = ['user', 'achievement', 'progress', 'unlocked_at']
    list_filter = ['unlocked_at']
    search_fields = ['user__username', 'achievement__name']
    date_hierarchy = 'unlocked_at'

