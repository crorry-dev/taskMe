"""
Debug Feedback Models

QA/Testing Feedback System for capturing voice/text feedback
that gets analyzed by AI and automatically implemented.
"""
from django.db import models
from django.conf import settings


class DebugFeedback(models.Model):
    """
    Captures debug/QA feedback from users during testing.
    
    Can be voice memo or text input. AI analyzes the feedback
    and suggests/implements changes automatically.
    """
    
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('ui_change', 'UI/Design Change'),
        ('improvement', 'General Improvement'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('analyzing', 'AI Analyzing'),
        ('analyzed', 'Analysis Complete'),
        ('implementing', 'Implementing'),
        ('implemented', 'Implemented'),
        ('committed', 'Committed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Core fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debug_feedbacks'
    )
    
    # Input
    text_input = models.TextField(
        blank=True,
        help_text="Text description of the feedback"
    )
    voice_memo = models.FileField(
        upload_to='debug_feedback/voice/',
        blank=True,
        null=True,
        help_text="Voice memo recording"
    )
    voice_transcription = models.TextField(
        blank=True,
        help_text="Transcription of voice memo"
    )
    
    # Classification
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='improvement'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # AI Analysis
    ai_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI analysis of the feedback"
    )
    ai_suggested_changes = models.JSONField(
        default=list,
        blank=True,
        help_text="AI suggested file changes"
    )
    ai_confidence = models.FloatField(
        default=0.0,
        help_text="AI confidence in analysis (0-1)"
    )
    
    # Implementation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    affected_files = models.JSONField(
        default=list,
        blank=True,
        help_text="List of files that were/will be changed"
    )
    commit_hash = models.CharField(
        max_length=40,
        blank=True,
        help_text="Git commit hash if committed"
    )
    commit_message = models.TextField(
        blank=True,
        help_text="Git commit message"
    )
    
    # Cost
    credits_cost = models.IntegerField(
        default=1,
        help_text="Credits charged for this feedback"
    )
    credits_charged = models.BooleanField(
        default=False,
        help_text="Whether credits have been charged"
    )
    
    # Context
    page_url = models.URLField(
        blank=True,
        help_text="Page URL where feedback was submitted"
    )
    screenshot = models.ImageField(
        upload_to='debug_feedback/screenshots/',
        blank=True,
        null=True
    )
    browser_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Browser/device info"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Debug Feedback'
        verbose_name_plural = 'Debug Feedbacks'
    
    def __str__(self):
        return f"{self.feedback_type}: {self.text_input[:50] or self.voice_transcription[:50]}..."
    
    @property
    def input_text(self):
        """Get the input text (transcription or direct text)."""
        return self.voice_transcription or self.text_input


class DebugFeedbackComment(models.Model):
    """Comments/updates on debug feedback."""
    
    feedback = models.ForeignKey(
        DebugFeedback,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class DebugConfig(models.Model):
    """
    Singleton configuration for Debug Feedback system.
    """
    
    # Feature flags
    debug_mode_enabled = models.BooleanField(
        default=True,
        help_text="Whether debug feedback is enabled globally"
    )
    auto_implement = models.BooleanField(
        default=False,
        help_text="Automatically implement AI suggestions"
    )
    auto_commit = models.BooleanField(
        default=False,
        help_text="Automatically commit implemented changes"
    )
    require_approval = models.BooleanField(
        default=True,
        help_text="Require admin approval before implementing"
    )
    
    # Costs
    feedback_cost = models.IntegerField(
        default=1,
        help_text="Credits cost per feedback submission"
    )
    
    # AI Settings
    ai_model = models.CharField(
        max_length=50,
        default='gpt-4o-mini',
        help_text="AI model to use for analysis"
    )
    
    # Admin users with unlimited credits
    unlimited_credit_usernames = models.JSONField(
        default=list,
        help_text="Usernames that have unlimited credits (e.g., ['crorry'])"
    )
    
    class Meta:
        verbose_name = 'Debug Configuration'
        verbose_name_plural = 'Debug Configuration'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get or create the singleton config."""
        config, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'unlimited_credit_usernames': ['crorry']
            }
        )
        return config
    
    @classmethod
    def user_has_unlimited_credits(cls, user):
        """Check if user has unlimited credits."""
        config = cls.get_config()
        return user.username in config.unlimited_credit_usernames
