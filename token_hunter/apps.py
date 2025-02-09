from django.apps import AppConfig


class TokenHunterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "token_hunter"
    
    def ready(self):
        from . import signals
