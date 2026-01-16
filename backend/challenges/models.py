from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Challenge(models.Model):
    """
    Challenges and duels that users can participate in.
    
    Security: Visibility controls access at object level.
    Default visibility is 'private' for privacy-by-default.
    """
    
    CHALLENGE_TYPE_CHOICES = [
        ('todo', 'One-time Todo'),
        ('streak', 'Habit/Streak'),
        ('program', 'Program (Multi-day)'),
        ('quantified', 'Quantified Goal'),
        ('team', 'Team Challenge'),
        ('duel', 'One-on-One Duel'),
        ('team_vs_team', 'Team vs Team'),
        ('community', 'Community Challenge'),
        ('global', 'Global Challenge'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('team', 'Team Only'),
        ('invite', 'Invite Only'),
        ('public', 'Public'),
    ]
    
    PROOF_TYPE_CHOICES = [
        ('SELF', 'Self Confirmation'),
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('PEER', 'Peer Verification'),
        ('SENSOR', 'Sensor Data'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='private',
        help_text="Who can see this challenge"
    )
    
    # Challenge details
    goal = models.CharField(max_length=255, help_text="What participants need to achieve")
    target_value = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Target number/value to achieve"
    )
    unit = models.CharField(max_length=50, blank=True, help_text="Unit of measurement (e.g., km, reps)")
    
    # Proof requirements (JSONField for SQLite compatibility instead of ArrayField)
    required_proof_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Required proof types for completion (list of SELF, PHOTO, VIDEO, DOCUMENT, PEER, SENSOR)"
    )
    min_peer_approvals = models.PositiveIntegerField(
        default=1,
        help_text="Minimum peer approvals needed for PEER proof"
    )
    proof_deadline_hours = models.PositiveIntegerField(
        default=24,
        help_text="Hours after contribution to submit proof"
    )
    
    # Team (if team challenge)
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='challenges'
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
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        db_table = 'challenges'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-start_date']),
            models.Index(fields=['challenge_type']),
            models.Index(fields=['visibility']),
            models.Index(fields=['creator', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"
    
    def is_visible_to(self, user) -> bool:
        """Check if challenge is visible to a user."""
        if self.visibility == 'public':
            return True
        if self.creator == user:
            return True
        if self.visibility == 'team' and self.team:
            return self.team.members.filter(user=user, is_active=True).exists()
        if self.visibility in ['invite', 'private']:
            return self.participants.filter(id=user.id).exists()
        return False


class ChallengeParticipant(models.Model):
    """
    Participant in a challenge (Participation entity).
    
    Tracks user's progress and status within a challenge.
    """
    
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Progress tracking
    current_progress = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Aggregated progress value"
    )
    streak_current = models.PositiveIntegerField(default=0)
    streak_best = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    
    # Rewards
    points_earned = models.IntegerField(default=0)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    last_contribution_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'challenge_participants'
        unique_together = [['challenge', 'user']]
        ordering = ['-current_progress']
    
    def __str__(self):
        return f"{self.user.username} in {self.challenge.title}"
    
    def update_progress(self):
        """Recalculate progress from contributions."""
        from django.db.models import Sum
        total = self.contributions.filter(
            status='approved'
        ).aggregate(total=Sum('value'))['total'] or 0
        self.current_progress = total
        self.save(update_fields=['current_progress'])


class Contribution(models.Model):
    """
    Individual contribution/entry towards a challenge.
    
    Represents a single logged activity (e.g., one workout, one day abstinent).
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Proof'),
        ('awaiting_review', 'Awaiting Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    participation = models.ForeignKey(
        ChallengeParticipant,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    
    # Contribution data
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Numeric value of this contribution"
    )
    note = models.TextField(blank=True, help_text="Optional note about this contribution")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    logged_at = models.DateTimeField(
        help_text="When the activity was performed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contributions'
        ordering = ['-logged_at']
        indexes = [
            models.Index(fields=['participation', '-logged_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Contribution {self.value} by {self.participation.user.username}"


class Proof(models.Model):
    """
    Proof attached to a contribution.
    
    Security:
    - Files stored in user-isolated paths
    - Server-side MIME validation
    - Size limits enforced
    """
    
    PROOF_TYPE_CHOICES = [
        ('SELF', 'Self Confirmation'),
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('PEER', 'Peer Verification'),
        ('SENSOR', 'Sensor Data'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review'),
    ]
    
    contribution = models.ForeignKey(
        Contribution,
        on_delete=models.CASCADE,
        related_name='proofs'
    )
    
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File references (depending on type)
    image = models.ImageField(
        upload_to='proofs/images/',
        null=True,
        blank=True
    )
    video = models.FileField(
        upload_to='proofs/videos/',
        null=True,
        blank=True
    )
    document = models.FileField(
        upload_to='proofs/documents/',
        null=True,
        blank=True
    )
    
    # Sensor data (JSON)
    sensor_data = models.JSONField(null=True, blank=True)
    
    # Metadata
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Review info
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_proofs'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'proofs'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['contribution', 'proof_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.proof_type} proof for {self.contribution}"


class ProofReview(models.Model):
    """
    Individual review of a proof (for PEER verification).
    
    Multiple reviews may be required based on challenge settings.
    """
    
    VERDICT_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    proof = models.ForeignKey(
        Proof,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proof_reviews'
    )
    
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'proof_reviews'
        unique_together = [['proof', 'reviewer']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reviewer.username} {self.verdict} {self.proof}"


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


class VoiceMemo(models.Model):
    """
    Voice memo for TaskMeMemo feature.
    
    Users record voice memos that are transcribed via Whisper API
    and then parsed by AI to suggest challenge creation.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending Transcription'),
        ('transcribing', 'Transcribing'),
        ('transcribed', 'Transcribed'),
        ('parsing', 'Parsing'),
        ('parsed', 'Parsed'),
        ('challenge_created', 'Challenge Created'),
        ('task_created', 'Task Created'),
        ('dismissed', 'Dismissed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voice_memos'
    )
    
    # Audio file
    audio_file = models.FileField(
        upload_to='voice_memos/%Y/%m/',
        help_text="Audio file (WebM, MP3, WAV, M4A)"
    )
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration of the audio in seconds"
    )
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    # Transcription result
    transcription = models.TextField(
        blank=True,
        help_text="Whisper API transcription result"
    )
    transcription_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score from transcription"
    )
    language_detected = models.CharField(
        max_length=10,
        blank=True,
        help_text="Detected language code (e.g., 'de', 'en')"
    )
    
    # AI parsing result (stored as JSON)
    parsed_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI-parsed challenge/task data"
    )
    ai_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="AI confidence in the parsed result"
    )
    
    # Link to created challenge/task
    created_challenge = models.ForeignKey(
        Challenge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_memos'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    transcribed_at = models.DateTimeField(null=True, blank=True)
    parsed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'voice_memos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"VoiceMemo by {self.user.username} ({self.status})"

