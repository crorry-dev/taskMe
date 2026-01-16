"""
Gamification service for awarding XP, badges, and handling level progression.

This service centralizes all reward logic to ensure consistency and auditability.
"""
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import math

from .models import Reward, UserReward, Achievement, UserAchievement, RewardEvent, Streak


# XP Configuration
XP_CONFIG = {
    'contribution_approved': 10,
    'challenge_completed': 50,
    'challenge_won': 100,
    'streak_milestone_7': 25,
    'streak_milestone_30': 100,
    'streak_milestone_100': 500,
    'daily_login': 5,
    'photo_proof': 5,
    'peer_review': 3,
}

# Level thresholds (cumulative XP needed)
def xp_for_level(level: int) -> int:
    """Calculate total XP needed to reach a level."""
    # Exponential curve: Level 1=0, Level 2=100, Level 3=300, etc.
    if level <= 1:
        return 0
    return int(100 * (level - 1) ** 1.5)


def level_from_xp(xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    while xp_for_level(level + 1) <= xp:
        level += 1
    return level


def xp_progress_in_level(xp: int) -> dict:
    """Get current level progress."""
    current_level = level_from_xp(xp)
    current_threshold = xp_for_level(current_level)
    next_threshold = xp_for_level(current_level + 1)
    xp_in_level = xp - current_threshold
    xp_needed = next_threshold - current_threshold
    
    return {
        'level': current_level,
        'xp_in_level': xp_in_level,
        'xp_needed': xp_needed,
        'progress_percent': int((xp_in_level / xp_needed) * 100) if xp_needed > 0 else 100,
        'total_xp': xp,
    }


@transaction.atomic
def award_xp(user, amount: int, reason: str, reason_detail: str = '', 
             related_challenge=None, related_contribution=None):
    """
    Award XP to a user and handle level-ups.
    
    Args:
        user: User instance
        amount: XP amount to award
        reason: One of RewardEvent.REWARD_REASON_CHOICES
        reason_detail: Additional context
        related_challenge: Optional challenge reference
        related_contribution: Optional contribution reference
    
    Returns:
        dict with xp_awarded, new_level, leveled_up, badges_earned
    """
    old_level = user.level
    old_xp = user.total_points
    
    # Award XP
    user.total_points += amount
    new_level = level_from_xp(user.total_points)
    leveled_up = new_level > old_level
    
    if leveled_up:
        user.level = new_level
    
    user.save(update_fields=['total_points', 'level'])
    
    # Create reward event
    RewardEvent.objects.create(
        user=user,
        xp_amount=amount,
        reason=reason,
        reason_detail=reason_detail,
        challenge=related_challenge,
        contribution=related_contribution,
    )
    
    # Check for new badges
    badges_earned = check_and_award_badges(user)
    
    # If leveled up, create a level-up event
    if leveled_up:
        RewardEvent.objects.create(
            user=user,
            xp_amount=0,
            reason='level_up',
            reason_detail=f'Reached level {new_level}',
        )
    
    return {
        'xp_awarded': amount,
        'old_xp': old_xp,
        'new_xp': user.total_points,
        'old_level': old_level,
        'new_level': new_level,
        'leveled_up': leveled_up,
        'badges_earned': badges_earned,
    }


def check_and_award_badges(user) -> list:
    """
    Check if user qualifies for any new badges and award them.
    
    Returns list of newly awarded badge names.
    """
    badges_earned = []
    
    # Define badge criteria
    badge_criteria = [
        {
            'name': 'First Steps',
            'description': 'Complete your first task',
            'check': lambda u: u.total_points >= 10,
        },
        {
            'name': 'Centurion',
            'description': 'Earn 100 XP',
            'check': lambda u: u.total_points >= 100,
        },
        {
            'name': 'Rising Star',
            'description': 'Reach Level 5',
            'check': lambda u: u.level >= 5,
        },
        {
            'name': 'Dedicated',
            'description': 'Reach Level 10',
            'check': lambda u: u.level >= 10,
        },
        {
            'name': 'Streak Master',
            'description': 'Maintain a 7-day streak',
            'check': lambda u: Streak.objects.filter(user=u, current_count__gte=7).exists(),
        },
        {
            'name': 'Marathon Runner',
            'description': 'Maintain a 30-day streak',
            'check': lambda u: Streak.objects.filter(user=u, current_count__gte=30).exists(),
        },
        {
            'name': 'Legend',
            'description': 'Maintain a 100-day streak',
            'check': lambda u: Streak.objects.filter(user=u, current_count__gte=100).exists(),
        },
    ]
    
    for criteria in badge_criteria:
        # Check if user already has this badge
        badge, created = Reward.objects.get_or_create(
            name=criteria['name'],
            reward_type='badge',
            defaults={
                'description': criteria['description'],
                'points_cost': 0,
                'is_redeemable': False,
            }
        )
        
        already_has = UserReward.objects.filter(user=user, reward=badge).exists()
        
        if not already_has and criteria['check'](user):
            UserReward.objects.create(user=user, reward=badge)
            badges_earned.append(criteria['name'])
            
            # Record badge award event
            RewardEvent.objects.create(
                user=user,
                xp_amount=0,
                badge=badge,
                reason='badge_earned',
                reason_detail=f'Earned badge: {criteria["name"]}',
            )
    
    return badges_earned


@transaction.atomic
def update_streak(user, streak_type: str, reference_id: str = None) -> dict:
    """
    Update or create a streak for a user.
    
    Args:
        user: User instance
        streak_type: Type of streak (daily_login, challenge, task, etc.)
        reference_id: Optional ID for challenge/task-specific streaks
    
    Returns:
        dict with streak info and any milestones reached
    """
    today = timezone.now().date()
    
    streak, created = Streak.objects.get_or_create(
        user=user,
        streak_type=streak_type,
        reference_id=reference_id or '',
        defaults={
            'current_count': 0,
            'best_count': 0,
            'last_activity_date': None,
        }
    )
    
    milestones_reached = []
    
    if streak.last_activity_date == today:
        # Already logged today, no change
        return {
            'streak': streak,
            'incremented': False,
            'milestones': [],
        }
    
    if streak.last_activity_date == today - timezone.timedelta(days=1):
        # Consecutive day - increment streak
        old_count = streak.current_count
        streak.current_count += 1
        
        # Check milestones
        for milestone in [7, 30, 100]:
            if old_count < milestone <= streak.current_count:
                milestones_reached.append(milestone)
                xp_key = f'streak_milestone_{milestone}'
                if xp_key in XP_CONFIG:
                    award_xp(user, XP_CONFIG[xp_key], 'streak_milestone',
                            f'{milestone}-day streak reached')
    else:
        # Streak broken or first activity
        if streak.current_count > 0 and streak.grace_used < streak.max_grace:
            # Use grace period
            streak.grace_used += 1
            streak.current_count += 1
        else:
            # Reset streak
            streak.current_count = 1
            streak.grace_used = 0
    
    # Update best count
    if streak.current_count > streak.best_count:
        streak.best_count = streak.current_count
    
    streak.last_activity_date = today
    streak.save()
    
    # Check for streak badges
    check_and_award_badges(user)
    
    return {
        'streak': streak,
        'incremented': True,
        'milestones': milestones_reached,
        'current_count': streak.current_count,
        'best_count': streak.best_count,
    }


def get_user_stats(user) -> dict:
    """Get comprehensive user statistics."""
    from django.db.models import Sum, Count
    from datetime import timedelta
    
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    
    # XP stats
    weekly_xp = RewardEvent.objects.filter(
        user=user, created_at__gte=week_ago
    ).aggregate(total=Sum('xp_amount'))['total'] or 0
    
    monthly_xp = RewardEvent.objects.filter(
        user=user, created_at__gte=month_ago
    ).aggregate(total=Sum('xp_amount'))['total'] or 0
    
    # Level progress
    level_progress = xp_progress_in_level(user.total_points)
    
    # Streaks
    active_streaks = Streak.objects.filter(user=user, current_count__gt=0)
    best_streak = Streak.objects.filter(user=user).order_by('-best_count').first()
    
    # Badges
    badges = UserReward.objects.filter(
        user=user, reward__reward_type='badge'
    ).select_related('reward').order_by('-earned_at')[:10]
    
    # Challenges
    from challenges.models import ChallengeParticipant
    active_challenges = ChallengeParticipant.objects.filter(
        user=user, status='active'
    ).count()
    completed_challenges = ChallengeParticipant.objects.filter(
        user=user, status='completed'
    ).count()
    
    return {
        'xp': {
            'total': user.total_points,
            'weekly': weekly_xp,
            'monthly': monthly_xp,
            **level_progress,
        },
        'streaks': {
            'active_count': active_streaks.count(),
            'current_best': active_streaks.order_by('-current_count').first().current_count if active_streaks.exists() else 0,
            'all_time_best': best_streak.best_count if best_streak else 0,
        },
        'badges': {
            'total': badges.count(),
            'recent': [
                {
                    'name': b.reward.name,
                    'description': b.reward.description,
                    'earned_at': b.earned_at.isoformat(),
                }
                for b in badges[:5]
            ],
        },
        'challenges': {
            'active': active_challenges,
            'completed': completed_challenges,
        },
    }


# ============================================
# Credit Economy Service
# ============================================

class CreditService:
    """
    Service class for managing credits.
    
    All credit operations should go through this service
    to ensure proper validation, logging, and economy controls.
    """
    
    @staticmethod
    def get_or_create_wallet(user):
        """Get or create a user's credit wallet."""
        from .models import CreditWallet
        wallet, created = CreditWallet.objects.get_or_create(user=user)
        return wallet, created
    
    @staticmethod
    def get_balance(user):
        """Get user's current credit balance."""
        wallet, _ = CreditService.get_or_create_wallet(user)
        return wallet.balance
    
    @staticmethod
    @transaction.atomic
    def grant_signup_bonus(user):
        """
        Grant initial signup bonus to new user.
        
        Called from user registration signal.
        """
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, created = CreditService.get_or_create_wallet(user)
        
        # Only grant if wallet was just created
        if created:
            wallet.add_credits(
                amount=config.signup_bonus,
                transaction_type='signup_bonus',
                description=f"Willkommensbonus: {config.signup_bonus} Credits"
            )
            
            # Track total minted
            config.total_credits_minted += config.signup_bonus
            config.save()
            
            return config.signup_bonus
        return 0
    
    @staticmethod
    @transaction.atomic
    def grant_referral_bonus(referrer, referred_user):
        """Grant bonus credits for successful referral."""
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(referrer)
        
        wallet.add_credits(
            amount=config.referral_bonus,
            transaction_type='referral_bonus',
            description=f"Empfehlungsbonus für {referred_user.username}"
        )
        
        config.total_credits_minted += config.referral_bonus
        config.save()
        
        return config.referral_bonus
    
    @staticmethod
    def get_challenge_cost(challenge_type, proof_type=None):
        """
        Calculate the credit cost for creating a challenge.
        
        Args:
            challenge_type: 'todo', 'streak', 'quantified', 'duel', 'team', 'community'
            proof_type: Optional proof requirement affecting cost
            
        Returns:
            Total credit cost
        """
        from .models import CreditConfig
        config = CreditConfig.get_config()
        
        cost_map = {
            'todo': config.cost_todo,
            'task': config.cost_todo,
            'streak': config.cost_streak,
            'quantified': config.cost_quantified,
            'duel': config.cost_duel,
            'team': config.cost_team,
            'community': config.cost_community,
        }
        
        base_cost = cost_map.get(challenge_type.lower(), config.cost_todo)
        
        # Add proof requirement costs
        proof_cost = 0
        if proof_type:
            if proof_type == 'PHOTO':
                proof_cost = config.cost_photo_proof
            elif proof_type == 'VIDEO':
                proof_cost = config.cost_video_proof
            elif proof_type == 'PEER':
                proof_cost = config.cost_peer_review
        
        return base_cost + proof_cost
    
    @staticmethod
    @transaction.atomic
    def charge_for_challenge(user, challenge):
        """
        Charge user for creating a challenge.
        
        Args:
            user: The user creating the challenge
            challenge: The challenge being created
            
        Returns:
            CreditTransaction if successful
            
        Raises:
            ValueError if insufficient credits
        """
        from .models import CreditConfig
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        # Determine challenge type
        challenge_type = getattr(challenge, 'challenge_type', 'todo')
        proof_type = getattr(challenge, 'proof_type', None)
        
        cost = CreditService.get_challenge_cost(challenge_type, proof_type)
        
        if not wallet.can_afford(cost):
            raise ValueError(f"Nicht genügend Credits. Benötigt: {cost}, Verfügbar: {wallet.balance}")
        
        tx = wallet.spend_credits(
            amount=cost,
            transaction_type='challenge_create',
            description=f"Challenge erstellt: {challenge.title[:50]}",
            related_object=challenge
        )
        
        # Track burned credits
        config = CreditConfig.get_config()
        config.total_credits_burned += cost
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def reward_task_completion(user, task):
        """Reward user for completing a task."""
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        tx = wallet.add_credits(
            amount=config.reward_task_complete,
            transaction_type='task_complete',
            description=f"Aufgabe erledigt: {task.title[:50]}",
            related_object=task
        )
        
        config.total_credits_minted += config.reward_task_complete
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def reward_challenge_completion(user, challenge):
        """
        Reward user for completing a challenge.
        
        Returns a percentage of the creation cost.
        """
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        # Calculate reward based on original cost
        challenge_type = getattr(challenge, 'challenge_type', 'todo')
        original_cost = CreditService.get_challenge_cost(challenge_type)
        reward = int(original_cost * config.reward_challenge_complete_percent / 100)
        
        if reward > 0:
            tx = wallet.add_credits(
                amount=reward,
                transaction_type='challenge_complete',
                description=f"Challenge abgeschlossen: {challenge.title[:50]}",
                related_object=challenge
            )
            
            config.total_credits_minted += reward
            config.save()
            
            return tx
        return None
    
    @staticmethod
    @transaction.atomic
    def reward_streak_milestone(user, streak, milestone):
        """
        Reward user for reaching a streak milestone.
        
        Args:
            milestone: 7, 30, or 100 days
        """
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        reward_map = {
            7: config.reward_streak_7,
            30: config.reward_streak_30,
            100: config.reward_streak_100,
        }
        
        reward = reward_map.get(milestone, 0)
        if reward > 0:
            tx = wallet.add_credits(
                amount=reward,
                transaction_type='streak_milestone',
                description=f"Streak Milestone: {milestone} Tage!",
                related_object=streak
            )
            
            config.total_credits_minted += reward
            config.save()
            
            return tx
        return None
    
    @staticmethod
    @transaction.atomic
    def reward_peer_review(reviewer, proof):
        """Reward user for submitting a peer review."""
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(reviewer)
        
        tx = wallet.add_credits(
            amount=config.reward_peer_review,
            transaction_type='peer_review',
            description="Peer Review eingereicht",
            related_object=proof
        )
        
        config.total_credits_minted += config.reward_peer_review
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def reward_duel_winner(winner, duel, loser_stake=None):
        """
        Reward the winner of a duel.
        
        Winner gets their stake back plus a portion of loser's stake.
        """
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(winner)
        
        # Winner gets their stake back plus 80% of opponent's
        stake = loser_stake or config.cost_duel
        winnings = stake + int(stake * 0.8)
        
        tx = wallet.add_credits(
            amount=winnings,
            transaction_type='duel_won',
            description=f"Duel gewonnen! Gewinn: {winnings} Credits",
            related_object=duel
        )
        
        # Only the new credits minted (winner's original stake not counted)
        config.total_credits_minted += int(stake * 0.8)
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def reward_badge(user, badge):
        """Reward user for earning a badge."""
        from .models import CreditConfig
        config = CreditConfig.get_config()
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        rarity = getattr(badge, 'rarity', 'common').lower()
        reward_map = {
            'common': config.reward_badge_common,
            'rare': config.reward_badge_rare,
            'epic': config.reward_badge_epic,
            'legendary': config.reward_badge_epic * 2,
        }
        
        reward = reward_map.get(rarity, config.reward_badge_common)
        
        tx = wallet.add_credits(
            amount=reward,
            transaction_type='badge_earned',
            description=f"Badge verdient: {badge.name}",
            related_object=badge
        )
        
        config.total_credits_minted += reward
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def admin_grant(user, amount, reason, admin_user):
        """Admin grants credits to a user."""
        from .models import CreditConfig
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        tx = wallet.add_credits(
            amount=amount,
            transaction_type='admin_grant',
            description=f"Admin Grant von {admin_user.username}: {reason}"
        )
        
        config = CreditConfig.get_config()
        config.total_credits_minted += amount
        config.save()
        
        return tx
    
    @staticmethod
    @transaction.atomic
    def admin_deduct(user, amount, reason, admin_user):
        """Admin deducts credits from a user."""
        from .models import CreditConfig
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        if not wallet.can_afford(amount):
            raise ValueError(f"User only has {wallet.balance} credits")
        
        tx = wallet.spend_credits(
            amount=amount,
            transaction_type='admin_deduct',
            description=f"Admin Abzug von {admin_user.username}: {reason}"
        )
        
        config = CreditConfig.get_config()
        config.total_credits_burned += amount
        config.save()
        
        return tx
    
    @staticmethod
    def get_economy_stats():
        """Get overall economy statistics."""
        from django.db.models import Sum
        from .models import CreditWallet, CreditConfig
        
        config = CreditConfig.get_config()
        
        total_wallets = CreditWallet.objects.count()
        total_balance = CreditWallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        
        return {
            'total_users_with_wallets': total_wallets,
            'total_credits_in_circulation': total_balance,
            'total_credits_minted': config.total_credits_minted,
            'total_credits_burned': config.total_credits_burned,
            'net_inflation': config.total_credits_minted - config.total_credits_burned,
        }
