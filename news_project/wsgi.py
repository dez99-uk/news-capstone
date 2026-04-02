"""WSGI entry point for the news project.

This module exposes the WSGI callable used by traditional Python web servers
to run the Django application.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
application = get_wsgi_application()
