"""
Debug Feedback Serializers
"""
from rest_framework import serializers
from .models import DebugFeedback, DebugFeedbackComment, DebugConfig


class DebugFeedbackCreateSerializer(serializers.Serializer):
    """Serializer for creating new feedback."""
    
    text_input = serializers.CharField(required=False, allow_blank=True)
    voice_memo = serializers.FileField(required=False)
    page_url = serializers.URLField(required=False, allow_blank=True)
    screenshot = serializers.ImageField(required=False)
    browser_info = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        if not data.get('text_input') and not data.get('voice_memo'):
            raise serializers.ValidationError(
                "Either text_input or voice_memo is required"
            )
        return data


class DebugFeedbackSerializer(serializers.ModelSerializer):
    """Full feedback serializer."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    input_text = serializers.CharField(read_only=True)
    
    class Meta:
        model = DebugFeedback
        fields = [
            'id',
            'username',
            'text_input',
            'voice_memo',
            'voice_transcription',
            'input_text',
            'feedback_type',
            'priority',
            'status',
            'ai_analysis',
            'ai_suggested_changes',
            'ai_confidence',
            'affected_files',
            'commit_hash',
            'commit_message',
            'credits_cost',
            'credits_charged',
            'page_url',
            'screenshot',
            'browser_info',
            'created_at',
            'analyzed_at',
            'implemented_at',
            'committed_at',
        ]
        read_only_fields = [
            'id', 'username', 'voice_transcription', 'input_text',
            'status', 'ai_analysis', 'ai_suggested_changes', 'ai_confidence',
            'affected_files', 'commit_hash', 'commit_message',
            'credits_charged', 'created_at', 'analyzed_at',
            'implemented_at', 'committed_at',
        ]


class DebugFeedbackListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = DebugFeedback
        fields = [
            'id',
            'username',
            'summary',
            'feedback_type',
            'priority',
            'status',
            'ai_confidence',
            'credits_cost',
            'created_at',
        ]
    
    def get_summary(self, obj):
        text = obj.input_text or ''
        return text[:100] + '...' if len(text) > 100 else text


class DebugFeedbackCommentSerializer(serializers.ModelSerializer):
    """Serializer for feedback comments."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DebugFeedbackComment
        fields = ['id', 'username', 'text', 'is_ai_generated', 'created_at']
        read_only_fields = ['id', 'username', 'is_ai_generated', 'created_at']


class DebugConfigSerializer(serializers.ModelSerializer):
    """Serializer for debug configuration."""
    
    class Meta:
        model = DebugConfig
        fields = [
            'debug_mode_enabled',
            'auto_implement',
            'auto_commit',
            'require_approval',
            'feedback_cost',
            'ai_model',
            'unlimited_credit_usernames',
        ]


class ApproveChangesSerializer(serializers.Serializer):
    """Serializer for approving suggested changes."""
    
    changes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Modified changes to implement (optional)"
    )
    commit_message = serializers.CharField(
        required=False,
        help_text="Custom commit message"
    )
