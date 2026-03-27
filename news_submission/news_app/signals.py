from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Article, assign_group_permissions
from .services import notify_subscribers_and_log


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    if sender.name != 'news_app':
        return
    for name in ['Reader', 'Editor', 'Journalist']:
        Group.objects.get_or_create(name=name)
    assign_group_permissions()


@receiver(post_save, sender=Article)
def article_approved_handler(sender, instance, created, **kwargs):
    if instance.approved and not instance.approval_notified:
        notify_subscribers_and_log(instance)
        Article.objects.filter(pk=instance.pk).update(approval_notified=True)
