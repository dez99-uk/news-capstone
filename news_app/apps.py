"""Application configuration for the news app.

This module defines the Django application configuration used to register the
application and load signal handlers during startup.
"""

from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    """Configure the Django application for the news app.

    The app configuration ensures that the `news_app` package is registered
    correctly and that signal handlers are imported once Django finishes
    loading installed applications.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_app'

    def ready(self):
        """Import signal handlers when the application is ready.

        Returns:
            None: This hook performs import side effects only.

        Example:
            Django calls this method automatically during application startup.
        """
        import news_app.signals  # noqa: F401
