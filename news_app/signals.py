"""Signal handlers for the news application.

This module reacts to model and migration events in order to initialise role
groups and trigger notification workflows when articles are approved.
"""

from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Article, assign_group_permissions
from .services import notify_subscribers_and_log


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    """Create the core role groups after migrations for this app.

    Args:
        sender: The app configuration sending the signal.
        **kwargs: Additional signal keyword arguments.

    Returns:
        None: Groups and permissions are created as a side effect.
    """
    if sender.name != 'news_app':
        return
    for name in ['Reader', 'Editor', 'Journalist']:
        Group.objects.get_or_create(name=name)
    assign_group_permissions()


@receiver(post_save, sender=Article)
def article_approved_handler(sender, instance, created, **kwargs):
    """Notify subscribers when an article is approved for the first time.

    Args:
        sender: The model class sending the signal.
        instance (Article): The saved article instance.
        created (bool): Whether the save created the object.
        **kwargs: Additional signal keyword arguments.

    Returns:
        None: Notification behaviour occurs as a side effect.
    """
    if instance.approved and not instance.approval_notified:
        notify_subscribers_and_log(instance)
        Article.objects.filter(pk=instance.pk).update(approval_notified=True)
