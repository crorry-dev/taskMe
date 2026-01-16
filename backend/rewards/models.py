from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Reward(models.Model):
    """Reward items that users can earn or redeem."""
    
    REWARD_TYPE_CHOICES = [
        ('badge', 'Badge'),
        ('title', 'Title'),
        ('item', 'Item'),
        ('privilege', 'Privilege'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    icon = models.ImageField(upload_to='rewards/icons/', null=True, blank=True)
    
    # Cost and availability
    points_cost = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Points required to redeem this reward"
    )
    is_available = models.BooleanField(default=True)
    is_redeemable = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rewards'
        ordering = ['points_cost']
    
    def __str__(self):
        return f"{self.name} ({self.reward_type})"


class UserReward(models.Model):
    """User's earned or redeemed rewards."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rewards'
    )
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    
    # Redemption details
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    # Display settings
    is_displayed = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_rewards'
        ordering = ['-earned_at']
        unique_together = [['user', 'reward']]
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"


class Achievement(models.Model):
    """Achievements that users can unlock."""
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/icons/', null=True, blank=True)
    
    # Requirements
    required_tasks = models.IntegerField(default=0)
    required_points = models.IntegerField(default=0)
    required_streak = models.IntegerField(default=0)
    special_conditions = models.JSONField(null=True, blank=True)
    
    # Rewards
    reward_points = models.IntegerField(default=0)
    
    # Metadata
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """User's unlocked achievements."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_achievements'
        ordering = ['-unlocked_at']
        unique_together = [['user', 'achievement']]
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class RewardEvent(models.Model):
    """
    Record of XP/coins/badges awarded to a user.
    
    This creates an immutable log of all rewards for auditing
    and allows reconstruction of user's reward history.
    """
    
    REWARD_REASON_CHOICES = [
        ('contribution_approved', 'Contribution Approved'),
        ('challenge_completed', 'Challenge Completed'),
        ('challenge_won', 'Challenge Won'),
        ('streak_milestone', 'Streak Milestone'),
        ('badge_earned', 'Badge Earned'),
        ('level_up', 'Level Up'),
        ('team_bonus', 'Team Bonus'),
        ('daily_login', 'Daily Login'),
        ('referral', 'Referral Bonus'),
        ('admin_grant', 'Admin Grant'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reward_events'
    )
    
    # What was awarded
    xp_amount = models.IntegerField(default=0)
    coins_amount = models.IntegerField(default=0)
    badge = models.ForeignKey(
        Reward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'reward_type': 'badge'}
    )
    
    # Why it was awarded
    reason = models.CharField(max_length=30, choices=REWARD_REASON_CHOICES)
    reason_detail = models.CharField(max_length=255, blank=True)
    
    # Source reference
    source_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Model name of source (e.g., 'Contribution', 'Challenge')"
    )
    source_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the source object"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reward_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reason']),
            models.Index(fields=['source_type', 'source_id']),
        ]
    
    def __str__(self):
        parts = []
        if self.xp_amount:
            parts.append(f"+{self.xp_amount} XP")
        if self.coins_amount:
            parts.append(f"+{self.coins_amount} coins")
        if self.badge:
            parts.append(f"Badge: {self.badge.name}")
        return f"{self.user.username}: {', '.join(parts)} ({self.reason})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update user's totals on new reward
        if is_new and (self.xp_amount or self.coins_amount):
            self.user.total_points += self.xp_amount
            self.user.save(update_fields=['total_points'])


class Streak(models.Model):
    """
    Track user streaks for habits and challenges.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streaks'
    )
    
    # What the streak is for
    streak_type = models.CharField(max_length=50, db_index=True)
    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of related challenge or habit"
    )
    
    # Streak data
    current_count = models.PositiveIntegerField(default=0)
    best_count = models.PositiveIntegerField(default=0)
    
    # Grace period tracking
    grace_used = models.PositiveIntegerField(
        default=0,
        help_text="Number of grace days used"
    )
    max_grace = models.PositiveIntegerField(
        default=1,
        help_text="Maximum grace days allowed"
    )
    
    # Timestamps
    last_activity_date = models.DateField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'streaks'
        unique_together = [['user', 'streak_type', 'reference_id']]
        indexes = [
            models.Index(fields=['user', 'streak_type']),
            models.Index(fields=['-current_count']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.streak_type} streak ({self.current_count} days)"
    
    def check_in(self, activity_date):
        """
        Record a check-in for the streak.
        Returns True if streak continues, False if broken.
        """
        from datetime import timedelta
        
        if self.last_activity_date is None:
            # First check-in
            self.current_count = 1
            self.last_activity_date = activity_date
            self.save()
            return True
        
        days_diff = (activity_date - self.last_activity_date).days
        
        if days_diff == 0:
            # Same day, no change
            return True
        elif days_diff == 1:
            # Consecutive day
            self.current_count += 1
            self.last_activity_date = activity_date
            if self.current_count > self.best_count:
                self.best_count = self.current_count
            self.save()
            return True
        elif days_diff <= (1 + self.max_grace - self.grace_used):
            # Within grace period
            self.grace_used += days_diff - 1
            self.current_count += 1
            self.last_activity_date = activity_date
            if self.current_count > self.best_count:
                self.best_count = self.current_count
            self.save()
            return True
        else:
            # Streak broken
            self.current_count = 1
            self.grace_used = 0
            self.last_activity_date = activity_date
            self.save()
            return False


class CreditWallet(models.Model):
    """
    User's credit wallet for the token economy.
    
    Each user has one wallet that tracks their credit balance.
    All credit changes are logged in CreditTransaction.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_wallet'
    )
    balance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current credit balance"
    )
    lifetime_earned = models.IntegerField(
        default=0,
        help_text="Total credits earned over lifetime"
    )
    lifetime_spent = models.IntegerField(
        default=0,
        help_text="Total credits spent over lifetime"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_wallets'
    
    def __str__(self):
        return f"{self.user.username}: {self.balance} credits"
    
    def add_credits(self, amount, transaction_type, description='', related_object=None):
        """Add credits to wallet and log transaction."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.balance += amount
        self.lifetime_earned += amount
        self.save()
        
        return CreditTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            description=description,
            related_content_type=related_object.__class__.__name__ if related_object else None,
            related_object_id=related_object.id if related_object else None,
        )
    
    def spend_credits(self, amount, transaction_type, description='', related_object=None):
        """Spend credits from wallet and log transaction."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient credits")
        
        self.balance -= amount
        self.lifetime_spent += amount
        self.save()
        
        return CreditTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=-amount,
            balance_after=self.balance,
            description=description,
            related_content_type=related_object.__class__.__name__ if related_object else None,
            related_object_id=related_object.id if related_object else None,
        )
    
    def can_afford(self, amount):
        """Check if user can afford a purchase."""
        return self.balance >= amount


class CreditTransaction(models.Model):
    """
    Individual credit transaction record.
    
    Provides full audit trail of all credit movements.
    """
    TRANSACTION_TYPES = [
        # Earning (positive)
        ('signup_bonus', 'Signup Bonus'),
        ('challenge_complete', 'Challenge Completed'),
        ('task_complete', 'Task Completed'),
        ('streak_milestone', 'Streak Milestone'),
        ('duel_won', 'Duel Won'),
        ('peer_review', 'Peer Review'),
        ('badge_earned', 'Badge Earned'),
        ('referral_bonus', 'Referral Bonus'),
        ('purchase', 'Credit Purchase'),
        ('admin_grant', 'Admin Grant'),
        ('refund', 'Refund'),
        
        # Spending (negative)
        ('challenge_create', 'Challenge Created'),
        ('task_create', 'Task Created'),
        ('duel_stake', 'Duel Stake'),
        ('feature_unlock', 'Feature Unlock'),
        ('transfer_out', 'Transfer Out'),
        ('expiry', 'Credit Expiry'),
        ('admin_deduct', 'Admin Deduction'),
    ]
    
    wallet = models.ForeignKey(
        CreditWallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(help_text="Positive for earning, negative for spending")
    balance_after = models.IntegerField(help_text="Balance after this transaction")
    description = models.CharField(max_length=500, blank=True)
    
    # Related object (optional)
    related_content_type = models.CharField(max_length=100, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f"{self.wallet.user.username}: {sign}{self.amount} ({self.transaction_type})"


class CreditConfig(models.Model):
    """
    Global credit economy configuration.
    
    Singleton model for economy tuning parameters.
    """
    # Initial credits
    signup_bonus = models.IntegerField(default=100)
    referral_bonus = models.IntegerField(default=25)
    
    # Challenge creation costs
    cost_todo = models.IntegerField(default=5)
    cost_streak = models.IntegerField(default=10)
    cost_quantified = models.IntegerField(default=10)
    cost_duel = models.IntegerField(default=15)
    cost_team = models.IntegerField(default=20)
    cost_community = models.IntegerField(default=50)
    
    # Proof requirement costs
    cost_photo_proof = models.IntegerField(default=5)
    cost_video_proof = models.IntegerField(default=10)
    cost_peer_review = models.IntegerField(default=3)
    
    # Rewards
    reward_task_complete = models.IntegerField(default=3)
    reward_challenge_complete_percent = models.IntegerField(
        default=80,
        help_text="Percent of creation cost returned on completion"
    )
    reward_streak_7 = models.IntegerField(default=10)
    reward_streak_30 = models.IntegerField(default=50)
    reward_streak_100 = models.IntegerField(default=200)
    reward_peer_review = models.IntegerField(default=1)
    reward_badge_common = models.IntegerField(default=5)
    reward_badge_rare = models.IntegerField(default=15)
    reward_badge_epic = models.IntegerField(default=50)
    
    # Economy controls
    total_credits_minted = models.BigIntegerField(default=0)
    total_credits_burned = models.BigIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_config'
        verbose_name = 'Credit Configuration'
        verbose_name_plural = 'Credit Configuration'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get or create the singleton config instance."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config
    
    def __str__(self):
        return "Credit Economy Configuration"
