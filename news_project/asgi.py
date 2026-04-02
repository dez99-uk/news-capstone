"""ASGI entry point for the news project.

This module exposes the ASGI callable used by asynchronous-capable web
servers to run the Django application.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
application = get_asgi_application()
