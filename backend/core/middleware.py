"""
Middleware for request tracking and security.
"""
import uuid
import logging

from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that assigns a unique ID to each request for tracing.
    
    The request ID is available as:
    - request.request_id (UUID object)
    - X-Request-ID response header
    """
    
    def process_request(self, request):
        # Check for incoming request ID from reverse proxy
        incoming_id = request.META.get('HTTP_X_REQUEST_ID')
        if incoming_id:
            try:
                request.request_id = uuid.UUID(incoming_id)
            except ValueError:
                request.request_id = uuid.uuid4()
        else:
            request.request_id = uuid.uuid4()
    
    def process_response(self, request, response):
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = str(request.request_id)
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Additional security headers not covered by Django's SecurityMiddleware.
    """
    
    def process_response(self, request, response):
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            'accelerometer=(), '
            'camera=(), '
            'geolocation=(), '
            'gyroscope=(), '
            'magnetometer=(), '
            'microphone=(), '
            'payment=(), '
            'usb=()'
        )
        
        return response
