from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Challenge(models.Model):
    """Challenges and duels that users can participate in."""
    
    CHALLENGE_TYPE_CHOICES = [
        ('global', 'Global Challenge'),
        ('duel', 'One-on-One Duel'),
        ('team', 'Team Challenge'),
        ('community', 'Community Challenge'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Challenge details
    goal = models.CharField(max_length=255, help_text="What participants need to achieve")
    target_value = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Target number/value to achieve"
    )
    
    # Participants
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_challenges'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChallengeParticipant',
        related_name='participated_challenges'
    )
    max_participants = models.IntegerField(null=True, blank=True)
    
    # Rewards
    reward_points = models.IntegerField(default=0)
    winner_reward_multiplier = models.FloatField(default=1.5)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        db_table = 'challenges'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-start_date']),
            models.Index(fields=['challenge_type']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"


class ChallengeParticipant(models.Model):
    """Participant in a challenge."""
    
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Progress tracking
    current_progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    
    # Rewards
    points_earned = models.IntegerField(default=0)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'challenge_participants'
        unique_together = [['challenge', 'user']]
        ordering = ['-current_progress']
    
    def __str__(self):
        return f"{self.user.username} in {self.challenge.title}"


class Duel(models.Model):
    """One-on-one duel between two users."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Acceptance'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    challenge = models.OneToOneField(
        Challenge,
        on_delete=models.CASCADE,
        related_name='duel',
        limit_choices_to={'challenge_type': 'duel'}
    )
    
    challenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_duels'
    )
    opponent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_duels'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_duels'
    )
    
    # Stakes
    stake_points = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'duels'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Duel: {self.challenger.username} vs {self.opponent.username}"

