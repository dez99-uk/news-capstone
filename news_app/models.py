"""Core data models for the news application.

The models in this module define the application's publishing workflow,
including users with custom roles, publishers, articles, newsletters, and
internal approval logs.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .managers import UserManager


class Publisher(models.Model):
    """Represent a news publisher that can employ editors and journalists.

    A publisher groups together articles, newsletters, and the users who work
    for that publishing organisation.
    """

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
        """Model metadata for publisher ordering."""

        ordering = ['name']

    def __str__(self):
        """Return the publisher name for admin and debug output.

        Returns:
            str: Human-readable publisher name.
        """
        return self.name


class User(AbstractUser):
    """Custom user model with application-specific roles and subscriptions.

    The project extends Django's built-in `AbstractUser` to support the reader,
    editor, and journalist roles, along with subscription relationships used
    for notifications and filtered content access.
    """

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
        """Model metadata defining custom permissions."""

        permissions = [
            ('can_approve_article', 'Can approve article'),
        ]

    def clean(self):
        """Validate role-based subscription rules before saving.

        Readers may subscribe only to journalist accounts, and non-reader roles
        should not retain publisher or journalist subscription data.

        Returns:
            None: Validation methods return no value.

        Raises:
            ValidationError: If role-based subscription rules are violated.
        """
        super().clean()
        if self.role == self.ROLE_READER and self.subscribed_journalists.filter(role=self.ROLE_JOURNALIST).count() != self.subscribed_journalists.count():
            raise ValidationError('Readers may only subscribe to journalist accounts.')
        if self.role != self.ROLE_READER and (self.subscribed_publishers.exists() or self.subscribed_journalists.exists()):
            raise ValidationError('Only readers should keep subscription values.')

    def save(self, *args, **kwargs):
        """Persist the user and keep role groups in sync.

        Returns:
            None: The model instance is saved as a side effect.
        """
        super().save(*args, **kwargs)
        self.sync_role_group()
        if self.role != self.ROLE_READER:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def sync_role_group(self):
        """Assign the user to the Django auth group that matches their role.

        Returns:
            None: Group membership is updated as a side effect.
        """
        role_group_map = {
            self.ROLE_READER: 'Reader',
            self.ROLE_EDITOR: 'Editor',
            self.ROLE_JOURNALIST: 'Journalist',
        }
        group_name = role_group_map[self.role]
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.set([group])

    def __str__(self):
        """Return the username for admin and debug output.

        Returns:
            str: The account username.
        """
        return self.username


class Article(models.Model):
    """Represent a publishable article written by a journalist.

    Articles may be linked to a publisher and must be approved before they
    become visible to readers.
    """

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
        """Model metadata defining article ordering and permissions."""

        ordering = ['-created_at']
        permissions = [
            ('approve_article', 'Can approve article'),
        ]

    def clean(self):
        """Validate author and publisher relationships.

        Returns:
            None: Validation methods return no value.

        Raises:
            ValidationError: If the author is not a journalist or is not
                affiliated with the selected publisher.
        """
        super().clean()
        if self.author.role != User.ROLE_JOURNALIST:
            raise ValidationError('Only journalists can author articles.')
        if self.publisher and self.author not in self.publisher.journalists.all():
            raise ValidationError('The selected journalist is not affiliated with this publisher.')

    def save(self, *args, **kwargs):
        """Save the article while maintaining approval timestamps.

        The method sets `approved_at` when an article becomes approved and
        clears it again if the article returns to an unapproved state.

        Returns:
            None: The model instance is saved as a side effect.

        Raises:
            ValidationError: Propagated from `full_clean` when model data is invalid.
        """
        if self.approved and self.approved_at is None:
            self.approved_at = timezone.now()
        if not self.approved:
            self.approved_at = None
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the article title for admin and debug output.

        Returns:
            str: Human-readable article title.
        """
        return self.title


class Newsletter(models.Model):
    """Represent a newsletter containing one or more related articles."""

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
        """Model metadata for newsletter ordering."""

        ordering = ['-created_at']

    def clean(self):
        """Validate author and publisher relationships for newsletters.

        Returns:
            None: Validation methods return no value.

        Raises:
            ValidationError: If the author is not a journalist or is not
                affiliated with the selected publisher.
        """
        super().clean()
        if self.author.role != User.ROLE_JOURNALIST:
            raise ValidationError('Only journalists can author newsletters.')
        if self.publisher and self.author not in self.publisher.journalists.all():
            raise ValidationError('The selected journalist is not affiliated with this publisher.')

    def __str__(self):
        """Return the newsletter title for admin and debug output.

        Returns:
            str: Human-readable newsletter title.
        """
        return self.title


class ApprovedArticleLog(models.Model):
    """Record payloads posted when an article approval event is triggered."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='approval_logs')
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model metadata for approval log ordering."""

        ordering = ['-received_at']

    def __str__(self):
        """Return a readable label for the approval log entry.

        Returns:
            str: Label including the related article identifier.
        """
        return f'Approval log for {self.article_id}'


def assign_group_permissions():
    """Assign model permissions to the built-in role groups.

    This function keeps the Django auth groups aligned with the application's
    expected role permissions for readers, editors, and journalists.

    Returns:
        None: Permissions are updated as a side effect.
    """
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
