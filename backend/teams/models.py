from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator


class Team(models.Model):
    """Team model for collaborative challenges and community features."""
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='teams/avatars/', null=True, blank=True)
    
    # Team settings
    is_public = models.BooleanField(default=True)
    max_members = models.IntegerField(null=True, blank=True)
    
    # Team stats
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    # Leadership
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_teams'
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='admin_teams',
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['-total_points']
        indexes = [
            models.Index(fields=['-total_points']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    def add_points(self, points):
        """Add points to team and update level."""
        self.total_points += points
        # Simple leveling: 500 points per level
        self.level = (self.total_points // 500) + 1
        self.save(update_fields=['total_points', 'level'])


class TeamMember(models.Model):
    """Team membership with roles and contributions."""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    points_contributed = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_members'
        unique_together = [['team', 'user']]
        ordering = ['-points_contributed']
    
    def __str__(self):
        return f"{self.user.username} in {self.team.name}"


class TeamInvitation(models.Model):
    """Team invitation system."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_invitations'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'team_invitations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.invitee.username} for {self.team.name}"


class CommunityPost(models.Model):
    """Community posts for team discussions and updates."""
    
    POST_TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('discussion', 'Discussion'),
        ('achievement', 'Achievement'),
        ('help', 'Help Request'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts'
    )
    
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Engagement
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )
    
    # Settings
    is_pinned = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'community_posts'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['team', '-created_at']),
        ]
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comments on community posts."""
    
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

