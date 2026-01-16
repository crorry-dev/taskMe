from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing audit logs.
    
    Security: This is read-only. No add/change/delete permissions.
    """
    
    list_display = [
        'id', 'action', 'user', 'resource_type', 
        'resource_id', 'success', 'created_at'
    ]
    list_filter = ['action', 'success', 'resource_type', 'created_at']
    search_fields = ['user__email', 'resource_id', 'request_id']
    readonly_fields = [
        'id', 'user', 'action', 'request_id', 'ip_address_hash',
        'user_agent', 'resource_type', 'resource_id', 'metadata',
        'success', 'error_message', 'created_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable add - logs are created programmatically only."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable change - logs are immutable."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete - logs must be preserved."""
        return False
