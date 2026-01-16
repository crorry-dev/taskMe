from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Task(models.Model):
    """Task model with commitment-based features."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('awaiting_proof', 'Awaiting Proof'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Task details
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Commitment features
    commitment_stake = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points user commits to stake on completion"
    )
    reward_points = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Points earned upon successful completion"
    )
    
    # Proof requirements
    requires_proof = models.BooleanField(default=False)
    proof_type = models.CharField(
        max_length=20,
        choices=[
            ('photo', 'Photo'),
            ('video', 'Video'),
            ('document', 'Document'),
            ('peer', 'Peer Verification'),
            ('sensor', 'Sensor Data'),
        ],
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Tags and categories
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    category = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"


class TaskProof(models.Model):
    """Proof submission for task completion."""
    
    PROOF_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='proof')
    
    # Proof content
    photo = models.ImageField(upload_to='proofs/photos/', null=True, blank=True)
    video = models.FileField(upload_to='proofs/videos/', null=True, blank=True)
    document = models.FileField(upload_to='proofs/documents/', null=True, blank=True)
    sensor_data = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Peer verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_proofs'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=PROOF_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_proofs'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Proof for {self.task.title}"

