"""
Core app - shared models, utilities, and middleware.

Note: Import models directly from core.models to avoid circular imports:
    from core.models import AuditLog, TimeStampedModel
"""
default_app_config = 'core.apps.CoreConfig'
