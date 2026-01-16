"""
Challenges API views.
Security: Object-level permissions, audit logging for sensitive actions.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from core.audit import log_audit_event
from core.permissions import IsOwner, IsChallengeParticipant, CanReviewProof
from rewards.services import award_xp, update_streak, check_and_award_badges

from .models import (
    Challenge, ChallengeParticipant, Contribution,
    Proof, ProofReview, Duel, VoiceMemo
)
from .serializers import (
    ChallengeListSerializer, ChallengeDetailSerializer,
    ChallengeCreateSerializer, ChallengeParticipantSerializer,
    ContributionSerializer, ContributionCreateSerializer,
    ProofSerializer, ProofCreateSerializer, ProofReviewSerializer, DuelSerializer,
    VoiceMemoUploadSerializer, VoiceMemoSerializer, VoiceMemoCreateChallengeSerializer
)


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Challenge CRUD operations.
    
    Security:
    - List returns only visible challenges
    - Detail checks visibility
    - Create/Update/Delete restricted to owner
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter challenges based on visibility rules."""
        user = self.request.user
        
        # Base queryset with optimized loading
        queryset = Challenge.objects.select_related(
            'creator', 'team'
        ).prefetch_related(
            'participations__user'
        )
        
        # Filter based on visibility
        # User can see: public, their own, team (if member), or participating
        queryset = queryset.filter(
            Q(visibility='public') |
            Q(creator=user) |
            Q(participants=user) |
            Q(visibility='team', team__members__user=user, team__members__is_active=True)
        ).distinct()
        
        # Optional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(challenge_type=type_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChallengeListSerializer
        elif self.action == 'create':
            return ChallengeCreateSerializer
        return ChallengeDetailSerializer
    
    def perform_create(self, serializer):
        """Create challenge and charge credits."""
        from rewards.services import CreditService
        
        user = self.request.user
        
        # Get challenge type and proof type from request data
        challenge_type = self.request.data.get('challenge_type', 'todo')
        proof_type = self.request.data.get('proof_type')
        
        # Calculate cost and check affordability
        cost = CreditService.get_challenge_cost(challenge_type, proof_type)
        wallet, _ = CreditService.get_or_create_wallet(user)
        
        if not wallet.can_afford(cost):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                detail=f"Nicht genügend Credits. Benötigt: {cost}, Verfügbar: {wallet.balance}"
            )
        
        # Save challenge first
        challenge = serializer.save()
        
        # Charge credits
        try:
            CreditService.charge_for_challenge(user, challenge)
        except ValueError:
            # Rollback challenge creation if payment fails
            challenge.delete()
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(detail="Credit-Abzug fehlgeschlagen")
        
        # Audit log
        log_audit_event(
            action='challenge.create',
            request=self.request,
            resource_type='Challenge',
            resource_id=challenge.id,
            metadata={
                'title': challenge.title,
                'type': challenge.challenge_type,
                'visibility': challenge.visibility,
                'credit_cost': cost
            }
        )
    
    def perform_update(self, serializer):
        old_visibility = serializer.instance.visibility
        challenge = serializer.save()
        
        # Log visibility changes
        if old_visibility != challenge.visibility:
            log_audit_event(
                action='challenge.visibility_change',
                request=self.request,
                resource_type='Challenge',
                resource_id=challenge.id,
                metadata={
                    'old_visibility': old_visibility,
                    'new_visibility': challenge.visibility
                }
            )
    
    def perform_destroy(self, instance):
        challenge_id = instance.id
        title = instance.title
        
        instance.delete()
        
        log_audit_event(
            action='challenge.delete',
            request=self.request,
            resource_type='Challenge',
            resource_id=challenge_id,
            metadata={'title': title}
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge."""
        challenge = self.get_object()
        
        # Check if already participating
        if ChallengeParticipant.objects.filter(
            challenge=challenge,
            user=request.user
        ).exists():
            return Response(
                {'error': 'Already participating in this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check max participants
        if challenge.max_participants:
            current_count = challenge.participations.filter(
                status='active'
            ).count()
            if current_count >= challenge.max_participants:
                return Response(
                    {'error': 'Challenge is full'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create participation
        participation = ChallengeParticipant.objects.create(
            challenge=challenge,
            user=request.user,
            status='active'
        )
        
        log_audit_event(
            action='challenge.join',
            request=request,
            resource_type='Challenge',
            resource_id=challenge.id
        )
        
        return Response(
            ChallengeParticipantSerializer(participation).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a challenge."""
        challenge = self.get_object()
        
        try:
            participation = ChallengeParticipant.objects.get(
                challenge=challenge,
                user=request.user
            )
        except ChallengeParticipant.DoesNotExist:
            return Response(
                {'error': 'Not participating in this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot leave if you're the creator and only participant
        if challenge.creator == request.user:
            return Response(
                {'error': 'Creator cannot leave the challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participation.status = 'withdrawn'
        participation.save()
        
        log_audit_event(
            action='challenge.leave',
            request=request,
            resource_type='Challenge',
            resource_id=challenge.id
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get challenge leaderboard."""
        challenge = self.get_object()
        
        participants = challenge.participations.filter(
            status__in=['active', 'completed']
        ).order_by('-current_progress', 'joined_at')
        
        serializer = ChallengeParticipantSerializer(participants, many=True)
        return Response(serializer.data)


class ContributionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for logging contributions to challenges.
    
    Security: Users can only manage their own contributions.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return user's contributions, optionally filtered by challenge."""
        queryset = Contribution.objects.filter(
            participation__user=self.request.user
        ).select_related(
            'participation__challenge',
            'participation__user'
        ).prefetch_related('proofs')
        
        challenge_id = self.request.query_params.get('challenge')
        if challenge_id:
            queryset = queryset.filter(
                participation__challenge_id=challenge_id
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContributionCreateSerializer
        return ContributionSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a contribution for a challenge."""
        challenge_id = request.data.get('challenge_id')
        
        if not challenge_id:
            return Response(
                {'error': 'challenge_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get participation
        try:
            participation = ChallengeParticipant.objects.get(
                challenge_id=challenge_id,
                user=request.user,
                status='active'
            )
        except ChallengeParticipant.DoesNotExist:
            return Response(
                {'error': 'Not an active participant in this challenge'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create contribution
        contribution = Contribution.objects.create(
            participation=participation,
            **serializer.validated_data
        )
        
        # Determine initial status based on proof requirements
        challenge = participation.challenge
        if not challenge.required_proof_types or challenge.required_proof_types == ['SELF']:
            contribution.status = 'approved'
            contribution.save()
            participation.update_progress()
        else:
            contribution.status = 'pending'
            contribution.save()
        
        # Update last contribution time
        participation.last_contribution_at = timezone.now()
        participation.save(update_fields=['last_contribution_at'])
        
        return Response(
            ContributionSerializer(contribution).data,
            status=status.HTTP_201_CREATED
        )


class ProofViewSet(viewsets.ModelViewSet):
    """
    ViewSet for proof submissions.
    
    Security: 
    - Users can only submit proofs for their own contributions
    - File validation performed server-side
    """
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # File upload constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    ALLOWED_DOC_TYPES = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    
    def get_queryset(self):
        """Return proofs for user's contributions."""
        return Proof.objects.filter(
            contribution__participation__user=self.request.user
        ).select_related(
            'contribution__participation__challenge',
            'reviewed_by'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProofCreateSerializer
        return ProofSerializer
    
    def validate_uploaded_file(self, file, proof_type):
        """Validate uploaded file type and size."""
        if not file:
            return
        
        # Check file size
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(
                f'File too large. Maximum size is {self.MAX_FILE_SIZE // (1024*1024)} MB'
            )
        
        # Check content type
        content_type = file.content_type
        if proof_type == 'PHOTO':
            if content_type not in self.ALLOWED_IMAGE_TYPES:
                raise ValidationError(
                    f'Invalid image type. Allowed: JPEG, PNG, GIF, WebP'
                )
        elif proof_type == 'DOCUMENT':
            if content_type not in self.ALLOWED_DOC_TYPES:
                raise ValidationError(
                    f'Invalid document type. Allowed: PDF, DOC, DOCX'
                )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Submit a proof for a contribution."""
        contribution_id = request.data.get('contribution_id')
        
        if not contribution_id:
            return Response(
                {'error': 'contribution_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify ownership
        try:
            contribution = Contribution.objects.get(
                id=contribution_id,
                participation__user=request.user
            )
        except Contribution.DoesNotExist:
            return Response(
                {'error': 'Contribution not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate file if present
        proof_type = serializer.validated_data.get('proof_type', 'SELF')
        proof_file = request.FILES.get('proof_file')
        
        if proof_type in ['PHOTO', 'DOCUMENT'] and not proof_file:
            return Response(
                {'error': f'{proof_type} proof requires a file upload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            self.validate_uploaded_file(proof_file, proof_type)
        except ValidationError as e:
            return Response(
                {'error': str(e.message)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        proof = Proof.objects.create(
            contribution=contribution,
            proof_file=proof_file,
            **serializer.validated_data
        )
        
        # Award XP for photo proof
        if proof_type == 'PHOTO':
            award_xp(
                request.user,
                amount=5,
                reason='photo_proof',
                reason_detail=f'Photo proof submitted for contribution',
                related_contribution=contribution
            )
        
        # Update contribution status
        contribution.status = 'awaiting_review'
        contribution.save()
        
        log_audit_event(
            action='proof.submit',
            request=request,
            resource_type='Proof',
            resource_id=proof.id,
            metadata={
                'proof_type': proof.proof_type,
                'contribution_id': contribution_id
            }
        )
        
        return Response(
            ProofSerializer(proof).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[CanReviewProof])
    def review(self, request, pk=None):
        """Review a proof (approve/reject)."""
        proof = self.get_object()
        
        verdict = request.data.get('verdict')
        if verdict not in ['approved', 'rejected']:
            return Response(
                {'error': 'verdict must be approved or rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create review
        review, created = ProofReview.objects.update_or_create(
            proof=proof,
            reviewer=request.user,
            defaults={
                'verdict': verdict,
                'comment': request.data.get('comment', '')
            }
        )
        
        # Award XP to reviewer for peer review
        if created:
            award_xp(
                request.user,
                amount=3,
                reason='peer_review',
                reason_detail='Peer review completed',
            )
        
        # Check if enough approvals
        challenge = proof.contribution.participation.challenge
        user = proof.contribution.participation.user
        
        if verdict == 'approved':
            approval_count = proof.reviews.filter(verdict='approved').count()
            if approval_count >= challenge.min_peer_approvals:
                proof.status = 'approved'
                proof.reviewed_by = request.user
                proof.reviewed_at = timezone.now()
                proof.save()
                
                # Update contribution
                contribution = proof.contribution
                contribution.status = 'approved'
                contribution.save()
                contribution.participation.update_progress()
                
                # Award XP for approved contribution
                award_xp(
                    user,
                    amount=10,
                    reason='contribution_approved',
                    reason_detail=f'Contribution approved for challenge: {challenge.title}',
                    related_challenge=challenge,
                    related_contribution=contribution
                )
                
                # Update streak and check badges
                update_streak(user, 'daily', challenge.id)
                check_and_award_badges(user)
                
        elif verdict == 'rejected':
            rejection_count = proof.reviews.filter(verdict='rejected').count()
            # If more rejections than possible remaining approvals
            remaining_reviewers = challenge.min_peer_approvals - proof.reviews.count()
            if rejection_count > remaining_reviewers:
                proof.status = 'rejected'
                proof.reviewed_by = request.user
                proof.reviewed_at = timezone.now()
                proof.rejection_reason = request.data.get('comment', '')
                proof.save()
                
                contribution = proof.contribution
                contribution.status = 'rejected'
                contribution.save()
        
        log_audit_event(
            action=f'proof.{verdict.replace("ed", "")}',
            request=request,
            resource_type='Proof',
            resource_id=proof.id,
            metadata={
                'verdict': verdict,
                'review_id': review.id
            }
        )
        
        return Response(ProofSerializer(proof).data)


class DuelViewSet(viewsets.ModelViewSet):
    """ViewSet for duels."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DuelSerializer
    
    def get_queryset(self):
        """Return duels involving the user."""
        return Duel.objects.filter(
            Q(challenger=self.request.user) |
            Q(opponent=self.request.user)
        ).select_related(
            'challenge', 'challenger', 'opponent', 'winner'
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a duel invitation."""
        duel = self.get_object()
        
        if duel.opponent != request.user:
            return Response(
                {'error': 'Only the opponent can accept the duel'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if duel.status != 'pending':
            return Response(
                {'error': 'Duel is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        duel.status = 'active'
        duel.accepted_at = timezone.now()
        duel.save()
        
        # Activate the challenge
        duel.challenge.status = 'active'
        duel.challenge.save()
        
        return Response(DuelSerializer(duel).data)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a duel invitation."""
        duel = self.get_object()
        
        if duel.opponent != request.user:
            return Response(
                {'error': 'Only the opponent can decline the duel'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if duel.status != 'pending':
            return Response(
                {'error': 'Duel is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        duel.status = 'cancelled'
        duel.save()
        
        duel.challenge.status = 'cancelled'
        duel.challenge.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete a duel and determine the winner.
        Called when challenge end date is reached or manually by participants.
        """
        duel = self.get_object()
        
        if duel.status != 'active':
            return Response(
                {'error': 'Duel is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only challenger, opponent, or challenge creator can complete
        if request.user not in [duel.challenger, duel.opponent, duel.challenge.creator]:
            return Response(
                {'error': 'Not authorized to complete this duel'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get participants' progress
        challenger_participant = ChallengeParticipant.objects.filter(
            challenge=duel.challenge,
            user=duel.challenger
        ).first()
        
        opponent_participant = ChallengeParticipant.objects.filter(
            challenge=duel.challenge,
            user=duel.opponent
        ).first()
        
        challenger_progress = challenger_participant.current_progress if challenger_participant else 0
        opponent_progress = opponent_participant.current_progress if opponent_participant else 0
        
        # Determine winner
        with transaction.atomic():
            if challenger_progress > opponent_progress:
                duel.winner = duel.challenger
                winner = duel.challenger
                loser = duel.opponent
            elif opponent_progress > challenger_progress:
                duel.winner = duel.opponent
                winner = duel.opponent
                loser = duel.challenger
            else:
                # It's a tie - no winner
                duel.winner = None
                winner = None
                loser = None
            
            duel.status = 'completed'
            duel.completed_at = timezone.now()
            duel.save()
            
            # Update challenge
            duel.challenge.status = 'completed'
            duel.challenge.save()
            
            # Award XP and Credits
            from rewards.services import CreditService
            
            if winner:
                # Winner gets 100 XP
                award_xp(
                    winner,
                    amount=100,
                    reason='challenge_won',
                    reason_detail=f'Won duel: {duel.challenge.title}',
                    related_challenge=duel.challenge
                )
                # Loser gets 25 XP for participating
                award_xp(
                    loser,
                    amount=25,
                    reason='challenge_completed',
                    reason_detail=f'Completed duel: {duel.challenge.title}',
                    related_challenge=duel.challenge
                )
                
                # Credit rewards for duel winner
                try:
                    CreditService.reward_duel_winner(winner, duel)
                except Exception:
                    pass  # Don't fail completion if credit reward fails
                
                # Send notifications
                from notifications.services import notify_challenge_completed
                notify_challenge_completed(winner, duel.challenge.title, 100, duel.challenge.id)
                notify_challenge_completed(loser, duel.challenge.title, 25, duel.challenge.id)
            else:
                # Tie - both get 50 XP
                award_xp(
                    duel.challenger,
                    amount=50,
                    reason='challenge_completed',
                    reason_detail=f'Tied in duel: {duel.challenge.title}',
                    related_challenge=duel.challenge
                )
                award_xp(
                    duel.opponent,
                    amount=50,
                    reason='challenge_completed',
                    reason_detail=f'Tied in duel: {duel.challenge.title}',
                    related_challenge=duel.challenge
                )
            
            # Check badges for all participants
            check_and_award_badges(duel.challenger)
            check_and_award_badges(duel.opponent)
        
        log_audit_event(
            action='duel.complete',
            request=request,
            resource_type='Duel',
            resource_id=duel.id,
            metadata={
                'winner': duel.winner.username if duel.winner else 'tie',
                'challenger_progress': challenger_progress,
                'opponent_progress': opponent_progress
            }
        )
        
        return Response(DuelSerializer(duel).data)


# ============================================
# Voice Memo ViewSet (TaskMeMemo Feature)
# ============================================

class VoiceMemoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for voice memo (TaskMeMemo) feature.
    
    Allows users to:
    - Upload voice recordings
    - Get transcription and AI-parsed challenge data
    - Create challenges from parsed data
    """
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Users can only see their own memos."""
        return VoiceMemo.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VoiceMemoUploadSerializer
        return VoiceMemoSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Upload a new voice memo.
        
        The memo is saved and queued for processing.
        """
        serializer = VoiceMemoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        memo = VoiceMemo.objects.create(
            user=request.user,
            audio_file=serializer.validated_data['audio_file'],
            duration_seconds=serializer.validated_data.get('duration_seconds'),
            status='pending'
        )
        
        log_audit_event(
            action='voicememo.upload',
            request=request,
            resource_type='VoiceMemo',
            resource_id=memo.id
        )
        
        return Response(
            VoiceMemoSerializer(memo).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process a voice memo: transcribe and parse.
        
        This runs synchronously for now.
        Could be made async with Celery for better UX.
        """
        memo = self.get_object()
        
        if memo.status not in ['pending', 'failed']:
            return Response(
                {'error': 'Memo already processed or processing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .voice_service import voice_memo_service
        
        if not voice_memo_service.is_available():
            return Response(
                {'error': 'Voice processing service not available. OPENAI_API_KEY not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        result = voice_memo_service.process_memo(memo)
        
        if result['status'] == 'failed':
            return Response(
                {'error': result.get('error', 'Processing failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        log_audit_event(
            action='voicememo.process',
            request=request,
            resource_type='VoiceMemo',
            resource_id=memo.id,
            metadata={
                'transcription_length': len(memo.transcription),
                'ai_confidence': memo.ai_confidence
            }
        )
        
        return Response(VoiceMemoSerializer(memo).data)
    
    @action(detail=True, methods=['post'])
    def create_challenge(self, request, pk=None):
        """
        Create a challenge from the parsed voice memo data.
        
        Accepts optional overrides for the parsed data.
        """
        memo = self.get_object()
        
        if memo.status != 'parsed':
            return Response(
                {'error': 'Memo must be parsed before creating a challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if memo.created_challenge:
            return Response(
                {'error': 'Challenge already created from this memo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate overrides
        serializer = VoiceMemoCreateChallengeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        overrides = serializer.validated_data
        
        from .voice_service import voice_memo_service
        
        try:
            challenge = voice_memo_service.create_challenge_from_memo(
                memo=memo,
                user=request.user,
                overrides=overrides
            )
            
            log_audit_event(
                action='voicememo.create_challenge',
                request=request,
                resource_type='VoiceMemo',
                resource_id=memo.id,
                metadata={
                    'challenge_id': challenge.id,
                    'challenge_type': challenge.challenge_type
                }
            )
            
            return Response({
                'memo': VoiceMemoSerializer(memo).data,
                'challenge': ChallengeDetailSerializer(challenge).data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a voice memo without creating a challenge."""
        memo = self.get_object()
        
        memo.status = 'dismissed'
        memo.save()
        
        return Response({'status': 'dismissed'})

