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

