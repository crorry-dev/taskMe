"""
Challenge API serializers.
Security: Validate all input, enforce visibility rules.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import (
    Challenge, ChallengeParticipant, Contribution,
    Proof, ProofReview, Duel, VoiceMemo
)


class ProofSerializer(serializers.ModelSerializer):
    """Serializer for proof submissions."""
    
    reviewer_name = serializers.CharField(
        source='reviewed_by.username',
        read_only=True
    )
    
    class Meta:
        model = Proof
        fields = [
            'id', 'proof_type', 'status', 'image', 'video', 'document',
            'sensor_data', 'original_filename', 'file_size', 'mime_type',
            'reviewed_by', 'reviewer_name', 'reviewed_at', 'rejection_reason',
            'submitted_at'
        ]
        read_only_fields = [
            'id', 'status', 'file_size', 'mime_type', 'reviewed_by',
            'reviewed_at', 'rejection_reason', 'submitted_at'
        ]
    
    def validate(self, data):
        """Validate proof based on type."""
        proof_type = data.get('proof_type')
        
        if proof_type == 'PHOTO' and not data.get('image'):
            raise serializers.ValidationError({
                'image': 'Image is required for PHOTO proof type.'
            })
        elif proof_type == 'VIDEO' and not data.get('video'):
            raise serializers.ValidationError({
                'video': 'Video file is required for VIDEO proof type.'
            })
        elif proof_type == 'DOCUMENT' and not data.get('document'):
            raise serializers.ValidationError({
                'document': 'Document is required for DOCUMENT proof type.'
            })
        elif proof_type == 'SENSOR' and not data.get('sensor_data'):
            raise serializers.ValidationError({
                'sensor_data': 'Sensor data is required for SENSOR proof type.'
            })
        
        return data


class ProofCreateSerializer(serializers.Serializer):
    """Serializer for creating proofs with file upload."""
    
    proof_type = serializers.ChoiceField(choices=[
        ('SELF', 'Self'),
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
        ('PEER', 'Peer'),
        ('SENSOR', 'Sensor'),
    ])
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class ProofReviewSerializer(serializers.ModelSerializer):
    """Serializer for proof reviews."""
    
    reviewer_name = serializers.CharField(
        source='reviewer.username',
        read_only=True
    )
    
    class Meta:
        model = ProofReview
        fields = ['id', 'proof', 'reviewer', 'reviewer_name', 'verdict', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']


class ContributionSerializer(serializers.ModelSerializer):
    """Serializer for contributions."""
    
    proofs = ProofSerializer(many=True, read_only=True)
    user_name = serializers.CharField(
        source='participation.user.username',
        read_only=True
    )
    
    class Meta:
        model = Contribution
        fields = [
            'id', 'participation', 'user_name', 'value', 'note',
            'status', 'logged_at', 'created_at', 'proofs'
        ]
        read_only_fields = ['id', 'status', 'created_at']
    
    def validate_logged_at(self, value):
        """Ensure logged_at is not in the future."""
        if value > timezone.now():
            raise serializers.ValidationError(
                "Cannot log a contribution for the future."
            )
        return value


class ContributionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contributions with optional inline proof."""
    
    class Meta:
        model = Contribution
        fields = ['value', 'note', 'logged_at']
    
    def validate_logged_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "Cannot log a contribution for the future."
            )
        return value


class ChallengeParticipantSerializer(serializers.ModelSerializer):
    """Serializer for challenge participants."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    class Meta:
        model = ChallengeParticipant
        fields = [
            'id', 'user', 'username', 'avatar', 'status',
            'current_progress', 'streak_current', 'streak_best',
            'completed', 'rank', 'points_earned',
            'joined_at', 'last_contribution_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'current_progress', 'streak_current', 'streak_best',
            'completed', 'rank', 'points_earned',
            'joined_at', 'last_contribution_at', 'completed_at'
        ]


class ChallengeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for challenge lists."""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    participant_count = serializers.SerializerMethodField()
    is_participating = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'challenge_type', 'status',
            'visibility', 'goal', 'target_value', 'unit',
            'reward_points', 'creator', 'creator_name',
            'participant_count', 'is_participating',
            'start_date', 'end_date', 'created_at'
        ]
    
    def get_participant_count(self, obj):
        return obj.participations.filter(status='active').count()
    
    def get_is_participating(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.participants.filter(id=request.user.id).exists()


class ChallengeDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for single challenge view."""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    participants = ChallengeParticipantSerializer(
        source='participations',
        many=True,
        read_only=True
    )
    is_creator = serializers.SerializerMethodField()
    is_participating = serializers.SerializerMethodField()
    my_participation = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'challenge_type', 'status',
            'visibility', 'goal', 'target_value', 'unit',
            'required_proof_types', 'min_peer_approvals', 'proof_deadline_hours',
            'team', 'creator', 'creator_name',
            'max_participants', 'reward_points', 'winner_reward_multiplier',
            'start_date', 'end_date', 'created_at', 'updated_at',
            'participants', 'is_creator', 'is_participating', 'my_participation'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']
    
    def get_is_creator(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.creator == request.user
    
    def get_is_participating(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.participants.filter(id=request.user.id).exists()
    
    def get_my_participation(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            participation = obj.participations.get(user=request.user)
            return ChallengeParticipantSerializer(participation).data
        except ChallengeParticipant.DoesNotExist:
            return None


class ChallengeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating challenges."""
    
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'challenge_type', 'visibility',
            'goal', 'target_value', 'unit',
            'required_proof_types', 'min_peer_approvals', 'proof_deadline_hours',
            'team', 'max_participants', 'reward_points', 'winner_reward_multiplier',
            'start_date', 'end_date'
        ]
    
    def validate(self, data):
        """Validate challenge data."""
        # Ensure end_date is after start_date
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        
        # Validate proof types
        proof_types = data.get('required_proof_types', [])
        valid_types = ['SELF', 'PHOTO', 'VIDEO', 'DOCUMENT', 'PEER', 'SENSOR']
        for pt in proof_types:
            if pt not in valid_types:
                raise serializers.ValidationError({
                    'required_proof_types': f'Invalid proof type: {pt}'
                })
        
        # PEER proof requires min_peer_approvals >= 1
        if 'PEER' in proof_types and data.get('min_peer_approvals', 1) < 1:
            raise serializers.ValidationError({
                'min_peer_approvals': 'At least 1 peer approval required for PEER proof.'
            })
        
        return data
    
    def create(self, validated_data):
        # Set creator from request context
        validated_data['creator'] = self.context['request'].user
        
        # Default to draft status
        validated_data['status'] = 'draft'
        
        challenge = Challenge.objects.create(**validated_data)
        
        # Auto-add creator as participant
        ChallengeParticipant.objects.create(
            challenge=challenge,
            user=challenge.creator,
            status='active'
        )
        
        return challenge


class DuelSerializer(serializers.ModelSerializer):
    """Serializer for duels."""
    
    challenger_name = serializers.CharField(
        source='challenger.username',
        read_only=True
    )
    opponent_name = serializers.CharField(
        source='opponent.username',
        read_only=True
    )
    winner_name = serializers.CharField(
        source='winner.username',
        read_only=True
    )
    challenge_title = serializers.CharField(
        source='challenge.title',
        read_only=True
    )
    
    class Meta:
        model = Duel
        fields = [
            'id', 'challenge', 'challenge_title',
            'challenger', 'challenger_name',
            'opponent', 'opponent_name',
            'status', 'winner', 'winner_name',
            'stake_points',
            'created_at', 'accepted_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'winner', 'created_at',
            'accepted_at', 'completed_at'
        ]


# ============================================
# Voice Memo Serializers
# ============================================

class VoiceMemoUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading voice memos."""
    
    class Meta:
        model = VoiceMemo
        fields = ['audio_file', 'duration_seconds']
    
    def validate_audio_file(self, value):
        """Validate audio file type and size."""
        # Max 10MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Datei zu groß. Maximum: {max_size // (1024*1024)}MB"
            )
        
        # Check file extension
        allowed_extensions = ['.webm', '.mp3', '.wav', '.m4a', '.ogg', '.mp4']
        ext = value.name.lower().split('.')[-1] if '.' in value.name else ''
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Ungültiges Dateiformat. Erlaubt: {', '.join(allowed_extensions)}"
            )
        
        return value


class VoiceMemoSerializer(serializers.ModelSerializer):
    """Full serializer for voice memos."""
    
    class Meta:
        model = VoiceMemo
        fields = [
            'id', 'status', 'audio_file', 'duration_seconds',
            'transcription', 'language_detected',
            'parsed_data', 'ai_confidence',
            'created_challenge', 'error_message',
            'created_at', 'transcribed_at', 'parsed_at'
        ]
        read_only_fields = [
            'id', 'status', 'transcription', 'language_detected',
            'parsed_data', 'ai_confidence', 'created_challenge',
            'error_message', 'created_at', 'transcribed_at', 'parsed_at'
        ]


class VoiceMemoCreateChallengeSerializer(serializers.Serializer):
    """Serializer for creating a challenge from parsed voice memo."""
    
    # Override fields from parsed_data
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    challenge_type = serializers.ChoiceField(
        choices=['todo', 'streak', 'quantified', 'duel', 'team', 'community'],
        required=False
    )
    target_value = serializers.IntegerField(min_value=1, required=False)
    unit = serializers.CharField(max_length=50, required=False, allow_blank=True)
    duration_days = serializers.IntegerField(min_value=1, max_value=365, required=False)
    proof_type = serializers.ChoiceField(
        choices=['SELF', 'PHOTO', 'VIDEO', 'PEER'],
        required=False
    )
