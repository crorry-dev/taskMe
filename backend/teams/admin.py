from django.contrib import admin
from .models import Team, TeamMember, TeamInvitation, CommunityPost, Comment


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    
    list_display = ['name', 'creator', 'total_points', 'level', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    date_hierarchy = 'created_at'
    ordering = ['-total_points']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for TeamMember model."""
    
    list_display = ['user', 'team', 'role', 'points_contributed', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'team__name']


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """Admin interface for TeamInvitation model."""
    
    list_display = ['team', 'inviter', 'invitee', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at']
    search_fields = ['team__name', 'inviter__username', 'invitee__username']


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    """Admin interface for CommunityPost model."""
    
    list_display = ['title', 'author', 'team', 'post_type', 'is_pinned', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""
    
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content', 'post__title']
    date_hierarchy = 'created_at'

