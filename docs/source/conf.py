"""Sphinx configuration for the news capstone project documentation."""

import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_project.sphinx_settings'
django.setup()

project = 'News Capstone Project'
author = 'Dez'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
