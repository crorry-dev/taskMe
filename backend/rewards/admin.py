from django.contrib import admin
from .models import (
    Reward, UserReward, Achievement, UserAchievement,
    CreditWallet, CreditTransaction, CreditConfig
)


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


# ============================================
# Credit Economy Admin
# ============================================

@admin.register(CreditWallet)
class CreditWalletAdmin(admin.ModelAdmin):
    """Admin interface for CreditWallet model."""
    
    list_display = ['user', 'balance', 'lifetime_earned', 'lifetime_spent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['lifetime_earned', 'lifetime_spent', 'created_at', 'updated_at']
    ordering = ['-balance']
    
    def has_add_permission(self, request):
        # Wallets are created automatically
        return False


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    """Admin interface for CreditTransaction model."""
    
    list_display = ['wallet', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__username', 'description']
    readonly_fields = ['wallet', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # Transactions are created through the service
        return False
    
    def has_change_permission(self, request, obj=None):
        # Transactions are immutable
        return False


@admin.register(CreditConfig)
class CreditConfigAdmin(admin.ModelAdmin):
    """Admin interface for CreditConfig singleton."""
    
    list_display = ['__str__', 'signup_bonus', 'cost_todo', 'cost_duel', 'updated_at']
    readonly_fields = ['total_credits_minted', 'total_credits_burned', 'updated_at']
    
    fieldsets = (
        ('Initial Credits', {
            'fields': ('signup_bonus', 'referral_bonus'),
        }),
        ('Challenge Creation Costs', {
            'fields': ('cost_todo', 'cost_streak', 'cost_quantified', 
                      'cost_duel', 'cost_team', 'cost_community'),
        }),
        ('Proof Requirement Costs', {
            'fields': ('cost_photo_proof', 'cost_video_proof', 'cost_peer_review'),
        }),
        ('Completion Rewards', {
            'fields': ('reward_task_complete', 'reward_challenge_complete_percent',
                      'reward_streak_7', 'reward_streak_30', 'reward_streak_100',
                      'reward_peer_review'),
        }),
        ('Badge Rewards', {
            'fields': ('reward_badge_common', 'reward_badge_rare', 'reward_badge_epic'),
        }),
        ('Economy Statistics', {
            'fields': ('total_credits_minted', 'total_credits_burned', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # Singleton - only one config allowed
        return not CreditConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

