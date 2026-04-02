"""Admin site registrations for the news application.

This module configures how project models appear in the Django admin so that
editors and administrators can inspect and manage key content entities.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for the custom user model.

    The admin extends Django's built-in user admin to expose role and
    subscription relationships that are specific to this project.
    """

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'News application fields',
            {
                'fields': ('role', 'subscribed_publishers', 'subscribed_journalists'),
            },
        ),
    )
    list_display = ('username', 'email', 'role', 'is_staff')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for publisher records."""

    list_display = ('name', 'created_at')
    filter_horizontal = ('editors', 'journalists')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for article records."""

    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher')
    search_fields = ('title', 'content', 'author__username')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for newsletter records."""

    list_display = ('title', 'author', 'publisher', 'created_at')
    filter_horizontal = ('articles',)


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    """Admin configuration for internal approved-article log records."""

    list_display = ('article', 'received_at')
