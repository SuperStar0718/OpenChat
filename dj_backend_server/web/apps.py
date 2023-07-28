from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'
    models_module = 'web.models.models'
    
    def ready(self):
        import signals  # Replace 'your_app_name' with your actual app name