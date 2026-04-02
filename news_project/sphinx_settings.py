"""Alternate Django settings used when building Sphinx documentation.

The documentation build uses SQLite so that Sphinx can import Django models
without requiring a local MariaDB/MySQL service to be running.
"""

from .settings import *  # noqa: F403,F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "sphinx_docs.sqlite3",  # noqa: F405
    }
}
