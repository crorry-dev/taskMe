"""
Audit logging utilities.

Usage:
    from core.audit import log_audit_event
    
    log_audit_event(
        request=request,
        action='challenge.create',
        resource_type='Challenge',
        resource_id=str(challenge.id),
        metadata={'title': challenge.title}
    )
"""
import hashlib
import uuid
from typing import Optional

from django.http import HttpRequest
from django.conf import settings


def get_request_id(request: Optional[HttpRequest] = None) -> uuid.UUID:
    """Get or generate request ID for tracing."""
    if request and hasattr(request, 'request_id'):
        return request.request_id
    return uuid.uuid4()


def hash_ip_address(ip: str) -> str:
    """Hash IP address for privacy-compliant logging."""
    # Use SHA256 with a salt from settings
    salt = getattr(settings, 'AUDIT_IP_SALT', 'commitquest-audit')
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP from request, considering proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP (client IP)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def log_audit_event(
    action: str,
    request: Optional[HttpRequest] = None,
    user=None,
    resource_type: str = '',
    resource_id: str = '',
    metadata: Optional[dict] = None,
    success: bool = True,
    error_message: str = ''
):
    """
    Log a security-relevant event to the audit log.
    
    Args:
        action: Action type (must be in AuditLog.ACTION_TYPES)
        request: HTTP request object (optional)
        user: User performing the action (optional, extracted from request if available)
        resource_type: Type of resource affected (e.g., 'Challenge', 'Team')
        resource_id: ID of the affected resource
        metadata: Additional context as dict
        success: Whether the action succeeded
        error_message: Error message if action failed
    """
    # Import here to avoid circular imports
    from core.models import AuditLog
    
    # Extract user from request if not provided
    if user is None and request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    
    # Extract request context
    request_id = None
    ip_hash = ''
    user_agent = ''
    
    if request:
        request_id = get_request_id(request)
        ip_hash = hash_ip_address(get_client_ip(request))
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    AuditLog.objects.create(
        user=user,
        action=action,
        request_id=request_id,
        ip_address_hash=ip_hash,
        user_agent=user_agent,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else '',
        metadata=metadata or {},
        success=success,
        error_message=error_message
    )
