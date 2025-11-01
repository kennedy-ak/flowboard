from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        """
        Import signals when the app is ready.
        This ensures that signal handlers are registered.
        """
        import tasks.signals
