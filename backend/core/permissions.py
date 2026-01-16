"""
Custom permissions for object-level access control.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    Assumes the model has a 'user' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit.
    Read-only for others (if visible).
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsTeamMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the team.
    Assumes the object has a 'team' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'team'):
            return False
        return obj.team.members.filter(user=request.user, is_active=True).exists()


class IsTeamAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the team.
    """
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'team'):
            return False
        return obj.team.members.filter(
            user=request.user,
            is_active=True,
            role__in=['owner', 'admin']
        ).exists()


class IsChallengeParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in the challenge.
    """
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'challenge'):
            challenge = obj.challenge
        elif hasattr(obj, 'participation'):
            challenge = obj.participation.challenge
        else:
            challenge = obj
        
        return challenge.participants.filter(id=request.user.id).exists()


class CanReviewProof(permissions.BasePermission):
    """
    Permission to check if user can review a proof.
    
    Rules:
    - User must be a participant in the same challenge
    - User cannot review their own proof
    - Challenge must allow peer review
    """
    
    def has_object_permission(self, request, view, obj):
        proof = obj
        
        # Cannot review own proof
        if proof.contribution.participation.user == request.user:
            return False
        
        challenge = proof.contribution.participation.challenge
        
        # Must be a participant
        if not challenge.participants.filter(id=request.user.id).exists():
            return False
        
        # Challenge must require peer proof
        return 'PEER' in challenge.required_proof_types
