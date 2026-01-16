"""
Debug Feedback Views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone

from core.audit import log_audit_event
from .models import DebugFeedback, DebugFeedbackComment, DebugConfig
from .serializers import (
    DebugFeedbackSerializer,
    DebugFeedbackListSerializer,
    DebugFeedbackCreateSerializer,
    DebugFeedbackCommentSerializer,
    DebugConfigSerializer,
    ApproveChangesSerializer,
)
from .services import debug_feedback_service


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read for authenticated, write for admin only."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


class DebugFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for debug feedback CRUD and processing.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Staff sees all, users see their own."""
        if self.request.user.is_staff:
            return DebugFeedback.objects.all()
        return DebugFeedback.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DebugFeedbackCreateSerializer
        if self.action == 'list':
            return DebugFeedbackListSerializer
        return DebugFeedbackSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create new debug feedback.
        
        Accepts text_input and/or voice_memo.
        Automatically processes if AI is available.
        """
        serializer = DebugFeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if debug mode is enabled
        config = DebugConfig.get_config()
        if not config.debug_mode_enabled:
            return Response(
                {'error': 'Debug mode is currently disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create feedback
        feedback = DebugFeedback.objects.create(
            user=request.user,
            text_input=serializer.validated_data.get('text_input', ''),
            voice_memo=serializer.validated_data.get('voice_memo'),
            page_url=serializer.validated_data.get('page_url', ''),
            screenshot=serializer.validated_data.get('screenshot'),
            browser_info=serializer.validated_data.get('browser_info', {}),
            credits_cost=config.feedback_cost,
        )
        
        log_audit_event(
            action='debug_feedback.create',
            request=request,
            resource_type='DebugFeedback',
            resource_id=feedback.id
        )
        
        # Auto-process if AI available
        if debug_feedback_service.is_available():
            result = debug_feedback_service.process_feedback(feedback)
            feedback.refresh_from_db()
        
        return Response(
            DebugFeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Re-analyze feedback."""
        feedback = self.get_object()
        
        if not debug_feedback_service.is_available():
            return Response(
                {'error': 'AI service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        result = debug_feedback_service.analyze_feedback(feedback)
        
        return Response({
            'status': result['status'],
            'analysis': feedback.ai_analysis,
            'suggested_changes': feedback.ai_suggested_changes,
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve and implement suggested changes.
        Admin only.
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = self.get_object()
        
        if feedback.status not in ['analyzed', 'pending']:
            return Response(
                {'error': f'Cannot approve feedback in status: {feedback.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApproveChangesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        changes = serializer.validated_data.get('changes') or feedback.ai_suggested_changes
        
        # Implement changes
        result = debug_feedback_service.implement_changes(feedback, changes)
        
        if result['status'] in ['implemented', 'partial']:
            # Create commit
            commit_message = serializer.validated_data.get('commit_message')
            debug_feedback_service.create_commit(feedback, commit_message)
        
        log_audit_event(
            action='debug_feedback.approve',
            request=request,
            resource_type='DebugFeedback',
            resource_id=feedback.id,
            metadata={'changes_count': len(changes)}
        )
        
        feedback.refresh_from_db()
        return Response(DebugFeedbackSerializer(feedback).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject feedback. Admin only."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = self.get_object()
        feedback.status = 'rejected'
        feedback.save()
        
        log_audit_event(
            action='debug_feedback.reject',
            request=request,
            resource_type='DebugFeedback',
            resource_id=feedback.id
        )
        
        return Response({'status': 'rejected'})
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """List or add comments to feedback."""
        feedback = self.get_object()
        
        if request.method == 'GET':
            comments = feedback.comments.all()
            return Response(
                DebugFeedbackCommentSerializer(comments, many=True).data
            )
        
        # POST - add comment
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'Comment text required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = DebugFeedbackComment.objects.create(
            feedback=feedback,
            user=request.user,
            text=text
        )
        
        return Response(
            DebugFeedbackCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class DebugConfigView(viewsets.ViewSet):
    """
    View for debug configuration.
    Read for all authenticated, write for admin.
    """
    
    permission_classes = [IsAdminOrReadOnly]
    
    def list(self, request):
        """Get current debug config."""
        config = DebugConfig.get_config()
        return Response(DebugConfigSerializer(config).data)
    
    def create(self, request):
        """Update debug config. Admin only."""
        config = DebugConfig.get_config()
        serializer = DebugConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        log_audit_event(
            action='debug_config.update',
            request=request,
            resource_type='DebugConfig',
            resource_id=1,
            metadata=serializer.validated_data
        )
        
        return Response(serializer.data)


class DebugStatsView(viewsets.ViewSet):
    """Debug feedback statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def list(self, request):
        """Get debug feedback statistics."""
        from django.db.models import Count, Avg
        
        stats = {
            'total_feedback': DebugFeedback.objects.count(),
            'by_status': dict(
                DebugFeedback.objects.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            ),
            'by_type': dict(
                DebugFeedback.objects.values('feedback_type')
                .annotate(count=Count('id'))
                .values_list('feedback_type', 'count')
            ),
            'avg_confidence': DebugFeedback.objects.aggregate(
                avg=Avg('ai_confidence')
            )['avg'] or 0,
            'pending_count': DebugFeedback.objects.filter(
                status__in=['pending', 'analyzed']
            ).count(),
        }
        
        return Response(stats)
