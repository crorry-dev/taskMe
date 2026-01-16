"""
File upload validators for proof submissions.
Security: Always validate server-side, never trust client.
"""
import magic
from django.core.exceptions import ValidationError
from django.conf import settings


# Allowed file types for proof uploads
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/webp': ['.webp'],
    'image/heic': ['.heic'],
    'image/heif': ['.heif'],
}

ALLOWED_VIDEO_TYPES = {
    'video/mp4': ['.mp4'],
    'video/quicktime': ['.mov'],
    'video/webm': ['.webm'],
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': ['.pdf'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
}

# Default size limits (can be overridden in settings)
DEFAULT_MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
DEFAULT_MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB
DEFAULT_MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB


def get_max_size(file_type: str) -> int:
    """Get maximum file size for a file type."""
    if file_type == 'image':
        return getattr(settings, 'MAX_IMAGE_UPLOAD_SIZE', DEFAULT_MAX_IMAGE_SIZE)
    elif file_type == 'video':
        return getattr(settings, 'MAX_VIDEO_UPLOAD_SIZE', DEFAULT_MAX_VIDEO_SIZE)
    elif file_type == 'document':
        return getattr(settings, 'MAX_DOCUMENT_UPLOAD_SIZE', DEFAULT_MAX_DOCUMENT_SIZE)
    return DEFAULT_MAX_DOCUMENT_SIZE


def validate_file_size(file, file_type: str):
    """Validate file size against configured limits."""
    max_size = get_max_size(file_type)
    if file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_mb:.1f} MB"
        )


def validate_file_type(file, allowed_types: dict):
    """
    Validate file type using magic bytes (not extension).
    Security: Never trust file extension alone.
    """
    # Read first 2048 bytes for magic detection
    file.seek(0)
    file_head = file.read(2048)
    file.seek(0)
    
    # Detect MIME type from content
    detected_mime = magic.from_buffer(file_head, mime=True)
    
    if detected_mime not in allowed_types:
        allowed_list = ', '.join(allowed_types.keys())
        raise ValidationError(
            f"File type '{detected_mime}' is not allowed. "
            f"Allowed types: {allowed_list}"
        )
    
    return detected_mime


def validate_image_upload(file):
    """Validate image file for proof upload."""
    validate_file_size(file, 'image')
    return validate_file_type(file, ALLOWED_IMAGE_TYPES)


def validate_video_upload(file):
    """Validate video file for proof upload."""
    validate_file_size(file, 'video')
    return validate_file_type(file, ALLOWED_VIDEO_TYPES)


def validate_document_upload(file):
    """Validate document file for proof upload."""
    validate_file_size(file, 'document')
    return validate_file_type(file, ALLOWED_DOCUMENT_TYPES)


def get_upload_path(instance, filename, subfolder='proofs'):
    """
    Generate isolated upload path per user.
    
    Security: Files are stored in user-specific directories
    to prevent cross-user access vulnerabilities.
    
    Pattern: proofs/{user_id}/{year}/{month}/{uuid}_{filename}
    """
    import uuid
    from datetime import datetime
    
    # Get user ID from the instance
    if hasattr(instance, 'contribution'):
        user_id = instance.contribution.participation.user_id
    elif hasattr(instance, 'user'):
        user_id = instance.user_id
    else:
        user_id = 'unknown'
    
    now = datetime.now()
    unique_id = uuid.uuid4().hex[:8]
    
    # Sanitize filename (keep only alphanumeric and extension)
    import re
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    return f"{subfolder}/{user_id}/{now.year}/{now.month:02d}/{unique_id}_{safe_filename}"
