"""
Core app models.
Re-export from __init__.py for convenience.
"""
from django.db import models
from django.conf import settings
import uuid


class AuditLog(models.Model):
    """
    Immutable audit log for security-critical events.
    
    Security: This model follows append-only pattern.
    Never update or delete records in production.
    """
    
    ACTION_TYPES = [
        # Authentication
        ('auth.login', 'User Login'),
        ('auth.logout', 'User Logout'),
        ('auth.login_failed', 'Login Failed'),
        ('auth.password_reset_request', 'Password Reset Request'),
        ('auth.password_reset_complete', 'Password Reset Complete'),
        ('auth.password_change', 'Password Change'),
        ('auth.mfa_enable', 'MFA Enabled'),
        ('auth.mfa_disable', 'MFA Disabled'),
        
        # User management
        ('user.create', 'User Created'),
        ('user.update', 'User Updated'),
        ('user.delete', 'User Deleted'),
        ('user.deactivate', 'User Deactivated'),
        
        # Team actions
        ('team.create', 'Team Created'),
        ('team.update', 'Team Updated'),
        ('team.delete', 'Team Deleted'),
        ('team.member_add', 'Member Added to Team'),
        ('team.member_remove', 'Member Removed from Team'),
        ('team.role_change', 'Member Role Changed'),
        
        # Challenge actions
        ('challenge.create', 'Challenge Created'),
        ('challenge.update', 'Challenge Updated'),
        ('challenge.delete', 'Challenge Deleted'),
        ('challenge.visibility_change', 'Challenge Visibility Changed'),
        ('challenge.join', 'Joined Challenge'),
        ('challenge.leave', 'Left Challenge'),
        
        # Proof actions
        ('proof.submit', 'Proof Submitted'),
        ('proof.approve', 'Proof Approved'),
        ('proof.reject', 'Proof Rejected'),
        ('proof.flag', 'Proof Flagged'),
        
        # Admin actions
        ('admin.user_suspend', 'User Suspended by Admin'),
        ('admin.content_remove', 'Content Removed by Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Actor (who performed the action)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action details
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    
    # Request context
    request_id = models.UUIDField(null=True, blank=True, db_index=True)
    ip_address_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash of IP for privacy"
    )
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Affected resource
    resource_type = models.CharField(max_length=50, blank=True, db_index=True)
    resource_id = models.CharField(max_length=100, blank=True)
    
    # Additional context (JSON)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
        # Prevent updates and deletes at model level
        managed = True
    
    def __str__(self):
        return f"{self.action} by {self.user_id or 'anonymous'} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Only allow creation, not updates
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("AuditLog entries cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        raise ValueError("AuditLog entries cannot be deleted")


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
