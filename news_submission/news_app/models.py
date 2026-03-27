from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .managers import UserManager


class Publisher(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='managed_publishers',
        blank=True,
    )
    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='publisher_affiliations',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_READER = 'reader'
    ROLE_EDITOR = 'editor'
    ROLE_JOURNALIST = 'journalist'
    ROLE_CHOICES = [
        (ROLE_READER, 'Reader'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_JOURNALIST, 'Journalist'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_READER)
    subscribed_publishers = models.ManyToManyField(Publisher, related_name='subscribers', blank=True)
    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='journalist_subscribers',
        blank=True,
    )

    objects = UserManager()

    REQUIRED_FIELDS = ['email']

    class Meta:
        permissions = [
            ('can_approve_article', 'Can approve article'),
        ]

    def clean(self):
        super().clean()
        if self.role == self.ROLE_READER and self.subscribed_journalists.filter(role=self.ROLE_JOURNALIST).count() != self.subscribed_journalists.count():
            raise ValidationError('Readers may only subscribe to journalist accounts.')
        if self.role != self.ROLE_READER and (self.subscribed_publishers.exists() or self.subscribed_journalists.exists()):
            raise ValidationError('Only readers should keep subscription values.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_role_group()
        if self.role != self.ROLE_READER:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def sync_role_group(self):
        role_group_map = {
            self.ROLE_READER: 'Reader',
            self.ROLE_EDITOR: 'Editor',
            self.ROLE_JOURNALIST: 'Journalist',
        }
        group_name = role_group_map[self.role]
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.set([group])

    def __str__(self):
        return self.username


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        limit_choices_to={'role': User.ROLE_JOURNALIST},
    )
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('approve_article', 'Can approve article'),
        ]

    def clean(self):
        super().clean()
        if self.author.role != User.ROLE_JOURNALIST:
            raise ValidationError('Only journalists can author articles.')
        if self.publisher and self.author not in self.publisher.journalists.all():
            raise ValidationError('The selected journalist is not affiliated with this publisher.')

    def save(self, *args, **kwargs):
        if self.approved and self.approved_at is None:
            self.approved_at = timezone.now()
        if not self.approved:
            self.approved_at = None
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsletters',
        limit_choices_to={'role': User.ROLE_JOURNALIST},
    )
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='newsletters')
    articles = models.ManyToManyField(Article, related_name='newsletters', blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.author.role != User.ROLE_JOURNALIST:
            raise ValidationError('Only journalists can author newsletters.')
        if self.publisher and self.author not in self.publisher.journalists.all():
            raise ValidationError('The selected journalist is not affiliated with this publisher.')

    def __str__(self):
        return self.title


class ApprovedArticleLog(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='approval_logs')
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f'Approval log for {self.article_id}'


def assign_group_permissions():
    group_permissions = {
        'Reader': [
            'view_article',
            'view_newsletter',
            'view_publisher',
            'view_user',
        ],
        'Editor': [
            'view_article', 'change_article', 'delete_article', 'approve_article',
            'view_newsletter', 'change_newsletter', 'delete_newsletter',
            'view_publisher', 'view_user',
        ],
        'Journalist': [
            'add_article', 'view_article', 'change_article', 'delete_article',
            'add_newsletter', 'view_newsletter', 'change_newsletter', 'delete_newsletter',
            'view_publisher', 'view_user',
        ],
    }
    for group_name, codename_list in group_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(codename__in=codename_list)
        group.permissions.set(permissions)
