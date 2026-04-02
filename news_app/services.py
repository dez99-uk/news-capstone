"""Service-layer utilities for notifications and integration tasks.

This module groups logic that should not live directly inside models or views,
such as selecting article subscribers, sending emails, and posting internal
approval events to another endpoint.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

import requests

from .models import Article, User


logger = logging.getLogger(__name__)


def get_article_subscribers(article: Article):
    """Return readers who should be notified about an approved article.

    Readers are included if they subscribe to the article's publisher, the
    article's author, or both.

    Args:
        article (Article): The approved article whose audience is being resolved.

    Returns:
        QuerySet[User]: A distinct queryset of reader accounts to notify.
    """
    readers = User.objects.filter(role=User.ROLE_READER)
    if article.publisher_id:
        readers = readers.filter(subscribed_publishers=article.publisher)
    journalist_readers = User.objects.filter(role=User.ROLE_READER, subscribed_journalists=article.author)
    return (readers | journalist_readers).distinct()


def notify_subscribers_and_log(article: Article) -> None:
    """Send subscriber notifications and create an internal approval log entry.

    The function first emails subscribed readers when recipient addresses are
    available. It then posts a JSON payload to the internal approved-article
    endpoint so that the event is recorded centrally.

    Args:
        article (Article): The article that has just been approved.

    Returns:
        None: The function performs side effects only.

    Raises:
        django.core.mail.BadHeaderError: May be raised by Django's mail
            utilities if invalid headers are generated.
    """
    subscribers = get_article_subscribers(article)
    recipient_list = [user.email for user in subscribers if user.email]
    if recipient_list:
        send_mail(
            subject=f'Approved article: {article.title}',
            message=(
                f'The article "{article.title}" has been approved.\n\n'
                f'Author: {article.author.username}\n'
                f'Publisher: {article.publisher.name if article.publisher else "Independent"}\n\n'
                f'{article.content}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

    url = f"{settings.INTERNAL_API_BASE_URL}{reverse('news_app_api:approved_article_log')}"
    payload = {
        'article': article.id,
        'payload': {
            'title': article.title,
            'author': article.author.username,
            'publisher': article.publisher.name if article.publisher else None,
            'approved_at': article.approved_at.isoformat() if article.approved_at else None,
        },
    }
    try:
        requests.post(
            url,
            json=payload,
            headers={'X-Internal-API-Key': settings.INTERNAL_API_KEY},
            timeout=5,
        )
    except requests.RequestException as exc:
        logger.warning('Unable to post approved article log: %s', exc)
