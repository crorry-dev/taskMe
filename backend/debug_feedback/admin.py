"""
Debug Feedback Admin Configuration
"""
from django.contrib import admin
from .models import DebugFeedback, DebugFeedbackComment, DebugConfig


@admin.register(DebugFeedback)
class DebugFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'feedback_type', 'priority', 'status',
        'ai_confidence', 'credits_charged', 'created_at'
    ]
    list_filter = ['status', 'feedback_type', 'priority', 'credits_charged']
    search_fields = ['text_input', 'voice_transcription', 'user__username']
    readonly_fields = [
        'voice_transcription', 'ai_analysis', 'ai_suggested_changes',
        'ai_confidence', 'affected_files', 'commit_hash',
        'analyzed_at', 'implemented_at', 'committed_at'
    ]
    
    fieldsets = (
        ('Input', {
            'fields': ('user', 'text_input', 'voice_memo', 'voice_transcription')
        }),
        ('Classification', {
            'fields': ('feedback_type', 'priority', 'status')
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis', 'ai_suggested_changes', 'ai_confidence'),
            'classes': ('collapse',)
        }),
        ('Implementation', {
            'fields': ('affected_files', 'commit_hash', 'commit_message'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('page_url', 'screenshot', 'browser_info'),
            'classes': ('collapse',)
        }),
        ('Credits', {
            'fields': ('credits_cost', 'credits_charged')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'analyzed_at', 'implemented_at', 'committed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DebugFeedbackComment)
class DebugFeedbackCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'feedback', 'user', 'is_ai_generated', 'created_at']
    list_filter = ['is_ai_generated']
    search_fields = ['text', 'user__username']


@admin.register(DebugConfig)
class DebugConfigAdmin(admin.ModelAdmin):
    list_display = [
        'debug_mode_enabled', 'auto_implement', 'auto_commit',
        'require_approval', 'feedback_cost'
    ]
    
    fieldsets = (
        ('Feature Flags', {
            'fields': (
                'debug_mode_enabled', 'auto_implement',
                'auto_commit', 'require_approval'
            )
        }),
        ('Costs', {
            'fields': ('feedback_cost',)
        }),
        ('AI Settings', {
            'fields': ('ai_model',)
        }),
        ('Special Users', {
            'fields': ('unlimited_credit_usernames',),
            'description': 'Usernames with unlimited credits (e.g., ["crorry"])'
        }),
    )
    
    def has_add_permission(self, request):
        # Only one config allowed
        return not DebugConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
