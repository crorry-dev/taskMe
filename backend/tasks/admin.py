from django.contrib import admin
from .models import Task, TaskProof


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    
    list_display = ['title', 'user', 'status', 'priority', 'reward_points', 'requires_proof', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'requires_proof', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'title', 'description')}),
        ('Task Details', {'fields': ('priority', 'status', 'category', 'tags')}),
        ('Commitment', {'fields': ('commitment_stake', 'reward_points')}),
        ('Proof Requirements', {'fields': ('requires_proof', 'proof_type')}),
        ('Dates', {'fields': ('due_date', 'completed_at')}),
    )


@admin.register(TaskProof)
class TaskProofAdmin(admin.ModelAdmin):
    """Admin interface for TaskProof model."""
    
    list_display = ['task', 'status', 'verified_by', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['task__title', 'task__user__username', 'notes']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']

