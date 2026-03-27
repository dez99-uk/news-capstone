from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

import requests

from .models import Article, User


logger = logging.getLogger(__name__)


def get_article_subscribers(article: Article):
    readers = User.objects.filter(role=User.ROLE_READER)
    if article.publisher_id:
        readers = readers.filter(subscribed_publishers=article.publisher)
    journalist_readers = User.objects.filter(role=User.ROLE_READER, subscribed_journalists=article.author)
    return (readers | journalist_readers).distinct()


def notify_subscribers_and_log(article: Article) -> None:
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
