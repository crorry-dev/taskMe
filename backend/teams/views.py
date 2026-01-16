"""
Views for the teams app.
Handles team CRUD, membership, and invitations.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404

from core.audit import log_audit_event
from .models import Team, TeamMember, TeamInvitation
from .serializers import (
    TeamSerializer, TeamDetailSerializer, TeamCreateSerializer,
    TeamMemberSerializer, TeamInvitationSerializer
)


class IsTeamAdminOrReadOnly(permissions.BasePermission):
    """Allow write access only to team admins."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is team admin or owner
        if hasattr(obj, 'team'):
            team = obj.team
        else:
            team = obj
        
        return TeamMember.objects.filter(
            team=team,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists()


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team operations.
    
    Supports: list, create, retrieve, update, delete
    Custom actions: join, leave, invite, members, leaderboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Users can see public teams or teams they're members of
        return Team.objects.filter(
            Q(is_public=True) | 
            Q(members__user=user, members__is_active=True)
        ).select_related('creator').prefetch_related(
            'members__user'
        ).distinct().order_by('-total_points')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamSerializer
    
    def perform_create(self, serializer):
        team = serializer.save(creator=self.request.user)
        
        # Add creator as owner
        TeamMember.objects.create(
            team=team,
            user=self.request.user,
            role='owner'
        )
        
        log_audit_event(
            action='team.create',
            request=self.request,
            resource_type='Team',
            resource_id=team.id
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a public team."""
        team = self.get_object()
        
        if not team.is_public:
            return Response(
                {'error': 'This team requires an invitation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check max members
        if team.max_members:
            current_count = TeamMember.objects.filter(team=team, is_active=True).count()
            if current_count >= team.max_members:
                return Response(
                    {'error': 'Team is full'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if already member
        existing = TeamMember.objects.filter(team=team, user=request.user).first()
        if existing:
            if existing.is_active:
                return Response(
                    {'error': 'Already a member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                existing.is_active = True
                existing.save()
        else:
            TeamMember.objects.create(team=team, user=request.user, role='member')
        
        log_audit_event(
            action='team.member_add',
            request=request,
            resource_type='Team',
            resource_id=team.id
        )
        
        return Response({'status': 'joined'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a team."""
        team = self.get_object()
        
        membership = TeamMember.objects.filter(
            team=team,
            user=request.user,
            is_active=True
        ).first()
        
        if not membership:
            return Response(
                {'error': 'Not a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if membership.role == 'owner':
            # Transfer ownership or disband
            other_admins = TeamMember.objects.filter(
                team=team,
                role='admin',
                is_active=True
            ).exclude(user=request.user).first()
            
            if other_admins:
                other_admins.role = 'owner'
                other_admins.save()
            else:
                # No other admins, check for other members
                other_member = TeamMember.objects.filter(
                    team=team,
                    is_active=True
                ).exclude(user=request.user).first()
                
                if other_member:
                    other_member.role = 'owner'
                    other_member.save()
        
        membership.is_active = False
        membership.save()
        
        log_audit_event(
            action='team.member_remove',
            request=request,
            resource_type='Team',
            resource_id=team.id
        )
        
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members."""
        team = self.get_object()
        members = TeamMember.objects.filter(team=team, is_active=True).select_related('user')
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Create an invitation link or invite a specific user."""
        team = self.get_object()
        
        # Check permission
        if not TeamMember.objects.filter(
            team=team,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists():
            return Response(
                {'error': 'Only admins can invite'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invited_user_id = request.data.get('user_id')
        
        if invited_user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            invited_user = get_object_or_404(User, pk=invited_user_id)
            
            invitation, created = TeamInvitation.objects.get_or_create(
                team=team,
                invited_user=invited_user,
                defaults={'invited_by': request.user}
            )
            
            if not created and invitation.status == 'pending':
                return Response(
                    {'error': 'Invitation already pending'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = TeamInvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Create link-based invitation
        import uuid
        invitation = TeamInvitation.objects.create(
            team=team,
            invited_by=request.user,
            invite_code=str(uuid.uuid4())[:8]
        )
        
        serializer = TeamInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_teams(self, request):
        """Get teams the current user is a member of."""
        memberships = TeamMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('team')
        
        teams = [m.team for m in memberships]
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing team members.
    Only team admins can modify roles.
    """
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamAdminOrReadOnly]
    
    def get_queryset(self):
        team_id = self.kwargs.get('team_pk')
        if team_id:
            return TeamMember.objects.filter(team_id=team_id, is_active=True)
        return TeamMember.objects.none()
