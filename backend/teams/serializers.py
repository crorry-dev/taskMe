"""
Serializers for the teams app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Team, TeamMember, TeamInvitation

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """Minimal user info for team displays."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = fields


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for team membership."""
    user = UserBriefSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'user', 'user_id', 'team', 'role', 
            'points_contributed', 'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'team', 'points_contributed', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    """Basic team serializer for lists."""
    creator = UserBriefSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'avatar', 'is_public',
            'max_members', 'member_count', 'total_points', 'level',
            'creator', 'is_member', 'user_role', 'created_at'
        ]
        read_only_fields = ['id', 'creator', 'total_points', 'level', 'created_at']
    
    def get_member_count(self, obj):
        return TeamMember.objects.filter(team=obj, is_active=True).count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return TeamMember.objects.filter(
            team=obj, 
            user=request.user,
            is_active=True
        ).exists()
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        membership = TeamMember.objects.filter(
            team=obj, 
            user=request.user,
            is_active=True
        ).first()
        return membership.role if membership else None


class TeamDetailSerializer(TeamSerializer):
    """Detailed team serializer with members."""
    members = serializers.SerializerMethodField()
    admins = UserBriefSerializer(many=True, read_only=True)
    
    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ['members', 'admins']
    
    def get_members(self, obj):
        members = TeamMember.objects.filter(
            team=obj, 
            is_active=True
        ).select_related('user').order_by('-points_contributed')[:20]
        return TeamMemberSerializer(members, many=True).data


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating teams."""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'avatar', 'is_public', 'max_members']
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Team name must be at least 3 characters")
        if Team.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A team with this name already exists")
        return value
    
    def validate_max_members(self, value):
        if value is not None and value < 2:
            raise serializers.ValidationError("Max members must be at least 2")
        return value


class TeamInvitationSerializer(serializers.ModelSerializer):
    """Serializer for team invitations."""
    team = TeamSerializer(read_only=True)
    invited_by = UserBriefSerializer(read_only=True)
    invited_user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = TeamInvitation
        fields = [
            'id', 'team', 'invited_user', 'invited_by',
            'invite_code', 'status', 'created_at', 'expires_at'
        ]
        read_only_fields = fields


class TeamInvitationAcceptSerializer(serializers.Serializer):
    """Serializer for accepting invitations."""
    invite_code = serializers.CharField(max_length=32, required=False)
    invitation_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if not data.get('invite_code') and not data.get('invitation_id'):
            raise serializers.ValidationError(
                "Either invite_code or invitation_id is required"
            )
        return data
