from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Task, TaskProof
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskProofSerializer,
    TaskProofSubmitSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status', 'priority', 'requires_proof', 'category']
    ordering_fields = ['created_at', 'due_date', 'priority', 'reward_points']
    search_fields = ['title', 'description', 'tags']
    
    def get_queryset(self):
        """Return tasks for the current user."""
        return Task.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Create task with current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed."""
        task = self.get_object()
        
        if task.status == 'completed':
            return Response(
                {'error': 'Task is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if task.requires_proof and not hasattr(task, 'proof'):
            return Response(
                {'error': 'Proof is required to complete this task'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        # Award points to user
        request.user.add_points(task.reward_points)
        
        return Response(TaskSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def submit_proof(self, request, pk=None):
        """Submit proof for task completion."""
        task = self.get_object()
        
        if not task.requires_proof:
            return Response(
                {'error': 'This task does not require proof'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(task, 'proof'):
            return Response(
                {'error': 'Proof already submitted for this task'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TaskProofSubmitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task)
            task.status = 'awaiting_proof'
            task.save()
            
            return Response(
                TaskProofSerializer(task.proof).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskProofViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing task proofs."""
    
    serializer_class = TaskProofSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return proofs for current user's tasks."""
        return TaskProof.objects.filter(task__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a task proof (for peer verification)."""
        proof = self.get_object()
        
        if proof.status != 'pending':
            return Response(
                {'error': 'This proof has already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        proof.status = 'approved'
        proof.verified_by = request.user
        proof.reviewed_at = timezone.now()
        proof.save()
        
        # Complete the task and award points
        task = proof.task
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        task.user.add_points(task.reward_points)
        
        return Response(TaskProofSerializer(proof).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a task proof."""
        proof = self.get_object()
        
        if proof.status != 'pending':
            return Response(
                {'error': 'This proof has already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        proof.status = 'rejected'
        proof.verified_by = request.user
        proof.reviewed_at = timezone.now()
        proof.rejection_reason = rejection_reason
        proof.save()
        
        task = proof.task
        task.status = 'failed'
        task.save()
        
        return Response(TaskProofSerializer(proof).data)

