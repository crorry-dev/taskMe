from rest_framework import serializers
from .models import Task, TaskProof
from accounts.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'priority', 'status',
            'commitment_stake', 'reward_points', 'requires_proof', 'proof_type',
            'created_at', 'updated_at', 'due_date', 'completed_at',
            'tags', 'category'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at']
    
    def validate(self, attrs):
        """Custom validation for task creation."""
        if attrs.get('requires_proof') and not attrs.get('proof_type'):
            raise serializers.ValidationError({
                'proof_type': 'Proof type is required when proof is required.'
            })
        return attrs


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'commitment_stake',
            'reward_points', 'requires_proof', 'proof_type',
            'due_date', 'tags', 'category'
        ]
    
    def validate(self, attrs):
        """Custom validation for task creation."""
        if attrs.get('requires_proof') and not attrs.get('proof_type'):
            raise serializers.ValidationError({
                'proof_type': 'Proof type is required when proof is required.'
            })
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'status',
            'due_date', 'tags', 'category'
        ]


class TaskProofSerializer(serializers.ModelSerializer):
    """Serializer for TaskProof model."""
    
    task = TaskSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskProof
        fields = [
            'id', 'task', 'photo', 'video', 'document', 'sensor_data',
            'notes', 'verified_by', 'status', 'rejection_reason',
            'submitted_at', 'reviewed_at'
        ]
        read_only_fields = [
            'id', 'task', 'verified_by', 'status', 'rejection_reason',
            'submitted_at', 'reviewed_at'
        ]


class TaskProofSubmitSerializer(serializers.ModelSerializer):
    """Serializer for submitting task proof."""
    
    class Meta:
        model = TaskProof
        fields = ['photo', 'video', 'document', 'sensor_data', 'notes']
    
    def validate(self, attrs):
        """Ensure at least one proof type is provided."""
        if not any([attrs.get('photo'), attrs.get('video'), attrs.get('document'), attrs.get('sensor_data')]):
            raise serializers.ValidationError('At least one type of proof must be provided.')
        return attrs
