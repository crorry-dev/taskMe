from django.apps import AppConfig


class RewardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rewards'
    
    def ready(self):
        # Import signals to register them
        import rewards.signals  # noqa: F401
