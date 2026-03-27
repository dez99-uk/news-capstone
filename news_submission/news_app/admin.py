from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
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
    list_display = ('name', 'created_at')
    filter_horizontal = ('editors', 'journalists')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher')
    search_fields = ('title', 'content', 'author__username')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'created_at')
    filter_horizontal = ('articles',)


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    list_display = ('article', 'received_at')
