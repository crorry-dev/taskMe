"""
Serializers for the rewards app.
"""
from rest_framework import serializers
from .models import (
    Reward, UserReward, Achievement, UserAchievement, 
    RewardEvent, Streak, CreditWallet, CreditTransaction, CreditConfig
)


class RewardSerializer(serializers.ModelSerializer):
    """Serializer for general rewards."""
    
    class Meta:
        model = Reward
        fields = [
            'id', 'name', 'description', 'reward_type',
            'icon', 'points_cost', 'is_available', 'is_redeemable'
        ]


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer specifically for badges."""
    
    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'icon']


class UserRewardSerializer(serializers.ModelSerializer):
    """Serializer for user's earned rewards."""
    reward = RewardSerializer(read_only=True)
    
    class Meta:
        model = UserReward
        fields = [
            'id', 'reward', 'is_redeemed', 'redeemed_at',
            'earned_at', 'is_displayed'
        ]


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements."""
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon',
            'required_tasks', 'required_points', 'required_streak',
            'reward_points', 'is_hidden'
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for user's unlocked achievements."""
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'unlocked_at', 'progress']


class RewardEventSerializer(serializers.ModelSerializer):
    """Serializer for reward events (XP/coins earned)."""
    badge_name = serializers.CharField(source='badge.name', read_only=True, allow_null=True)
    
    class Meta:
        model = RewardEvent
        fields = [
            'id', 'xp_amount', 'coins_amount', 'badge_name',
            'reason', 'reason_detail', 'created_at'
        ]


class StreakSerializer(serializers.ModelSerializer):
    """Serializer for user streaks."""
    
    class Meta:
        model = Streak
        fields = [
            'id', 'streak_type', 'reference_id',
            'current_count', 'best_count',
            'grace_used', 'max_grace',
            'last_activity_date', 'started_at'
        ]


class UserProgressSerializer(serializers.Serializer):
    """Serializer for user progress overview."""
    
    total_xp = serializers.IntegerField()
    level = serializers.IntegerField()
    weekly_xp = serializers.IntegerField()
    xp_to_next_level = serializers.IntegerField()
    active_streaks = serializers.IntegerField()
    best_streak = serializers.IntegerField()
    badge_count = serializers.IntegerField()


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entries."""
    
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.URLField(allow_null=True)
    total_points = serializers.IntegerField()
    level = serializers.IntegerField()


# ============================================
# Credit Economy Serializers
# ============================================

class CreditWalletSerializer(serializers.ModelSerializer):
    """Serializer for user's credit wallet."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CreditWallet
        fields = [
            'id', 'username', 'balance', 
            'lifetime_earned', 'lifetime_spent',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class CreditTransactionSerializer(serializers.ModelSerializer):
    """Serializer for credit transactions."""
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', 
        read_only=True
    )
    
    class Meta:
        model = CreditTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'amount', 'balance_after', 'description',
            'related_content_type', 'related_object_id',
            'created_at'
        ]
        read_only_fields = fields


class CreditConfigSerializer(serializers.ModelSerializer):
    """Serializer for credit economy configuration (read-only for users)."""
    
    class Meta:
        model = CreditConfig
        fields = [
            'signup_bonus', 'referral_bonus',
            'cost_todo', 'cost_streak', 'cost_quantified',
            'cost_duel', 'cost_team', 'cost_community',
            'cost_photo_proof', 'cost_video_proof', 'cost_peer_review',
            'reward_task_complete', 'reward_challenge_complete_percent',
            'reward_streak_7', 'reward_streak_30', 'reward_streak_100',
            'reward_peer_review',
            'reward_badge_common', 'reward_badge_rare', 'reward_badge_epic',
        ]
        read_only_fields = fields


class CreditBalanceSerializer(serializers.Serializer):
    """Simple serializer for balance check."""
    balance = serializers.IntegerField()
    can_afford = serializers.BooleanField(required=False)


class ChallengeCostSerializer(serializers.Serializer):
    """Serializer for challenge cost calculation."""
    challenge_type = serializers.ChoiceField(
        choices=['todo', 'streak', 'quantified', 'duel', 'team', 'community']
    )
    proof_type = serializers.ChoiceField(
        choices=['SELF', 'PHOTO', 'VIDEO', 'PEER', 'DOCUMENT'],
        required=False,
        allow_null=True
    )


class ChallengeCostResponseSerializer(serializers.Serializer):
    """Response serializer for challenge cost."""
    base_cost = serializers.IntegerField()
    proof_cost = serializers.IntegerField()
    total_cost = serializers.IntegerField()
    can_afford = serializers.BooleanField()
    current_balance = serializers.IntegerField()


class AdminCreditActionSerializer(serializers.Serializer):
    """Serializer for admin credit grant/deduct actions."""
    user_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=500)


class EconomyStatsSerializer(serializers.Serializer):
    """Serializer for economy-wide statistics."""
    total_users_with_wallets = serializers.IntegerField()
    total_credits_in_circulation = serializers.IntegerField()
    total_credits_minted = serializers.IntegerField()
    total_credits_burned = serializers.IntegerField()
    net_inflation = serializers.IntegerField()
