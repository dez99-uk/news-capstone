"""Automated tests for the news application.

The tests in this module verify the main API and approval workflows, including
authentication, role-based permissions, notification side effects, and
internal approval logging.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, assign_group_permissions


class BaseNewsTestCase(APITestCase):
    """Provide shared test fixtures used across API and signal tests."""

    def setUp(self):
        """Create a complete baseline dataset for downstream tests.

        Returns:
            None: Test fixtures are created as a side effect.
        """
        self.User = get_user_model()
        assign_group_permissions()

        self.editor = self.User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='pass12345',
            role='editor',
        )
        self.journalist = self.User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='pass12345',
            role='journalist',
        )
        self.reader = self.User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='pass12345',
            role='reader',
        )
        self.other_reader = self.User.objects.create_user(
            username='otherreader',
            email='otherreader@example.com',
            password='pass12345',
            role='reader',
        )
        self.publisher = Publisher.objects.create(name='Daily Planet', description='Main publisher')
        self.publisher.editors.add(self.editor)
        self.publisher.journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        with patch('news_app.services.requests.post'):
            self.approved_article = Article.objects.create(
                title='Approved story',
                content='A long approved article body.',
                author=self.journalist,
                publisher=self.publisher,
                approved=True,
            )
        self.pending_article = Article.objects.create(
            title='Pending story',
            content='Draft article awaiting review.',
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )
        self.newsletter = Newsletter.objects.create(
            title='Morning Brief',
            description='Daily roundup',
            author=self.journalist,
            publisher=self.publisher,
        )
        self.newsletter.articles.add(self.approved_article)

        self.reader_token = Token.objects.create(user=self.reader)
        self.editor_token = Token.objects.create(user=self.editor)
        self.journalist_token = Token.objects.create(user=self.journalist)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', INTERNAL_API_BASE_URL='http://testserver', INTERNAL_API_KEY='test-key')
class NewsApiTests(BaseNewsTestCase):
    """Test the REST API behaviour for different user roles."""

    def test_reader_only_gets_subscribed_articles(self):
        """Ensure readers only receive approved articles matching subscriptions."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.get(reverse('news_app_api:subscribed_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], 'Approved story')

    def test_reader_cannot_create_article(self):
        """Ensure readers are blocked from article creation endpoints."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.post(reverse('news_app_api:article_list_create'), {
            'title': 'Blocked article',
            'content': 'Readers cannot post this.',
            'publisher_id': self.publisher.id,
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_journalist_can_create_article(self):
        """Ensure journalists can create a new unapproved article."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.journalist_token.key}')
        response = self.client.post(reverse('news_app_api:article_list_create'), {
            'title': 'Fresh article',
            'content': 'Created by the journalist.',
            'publisher_id': self.publisher.id,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], 'Fresh article')
        self.assertFalse(response.json()['approved'])

    @patch('news_app.signals.notify_subscribers_and_log')
    def test_editor_can_approve_and_delete_article(self, mock_notify):
        """Ensure editors can approve and then delete an article."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.editor_token.key}')
        approve_response = self.client.post(
            reverse('news_app_api:article_approve', kwargs={'pk': self.pending_article.id})
        )
        self.assertEqual(approve_response.status_code, 200)
        self.pending_article.refresh_from_db()
        self.assertTrue(self.pending_article.approved)
        delete_response = self.client.delete(
            reverse('news_app_api:article_detail', kwargs={'pk': self.pending_article.id})
        )
        self.assertEqual(delete_response.status_code, 204)
        mock_notify.assert_called_once()

    def test_subscribed_endpoint_requires_authentication(self):
        """Ensure the subscribed-articles endpoint rejects anonymous requests."""
        response = self.client.get(reverse('news_app_api:subscribed_articles'))
        self.assertEqual(response.status_code, 401)

    def test_newsletter_list_and_journalist_create(self):
        """Ensure readers can list newsletters and journalists can create them."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        list_response = self.client.get(reverse('news_app_api:newsletter_list_create'))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.journalist_token.key}')
        create_response = self.client.post(reverse('news_app_api:newsletter_list_create'), {
            'title': 'Weekend Wrap',
            'description': 'Summary for the weekend',
            'publisher_id': self.publisher.id,
            'articles': [self.approved_article.id],
        }, format='json')
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()['title'], 'Weekend Wrap')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    INTERNAL_API_BASE_URL='http://testserver',
    INTERNAL_API_KEY='test-key',
)
class ApprovalSignalTests(TestCase):
    """Test signal-driven behaviour triggered by article approval."""

    def setUp(self):
        """Create the fixtures required to test approval side effects."""
        self.User = get_user_model()
        assign_group_permissions()
        self.editor = self.User.objects.create_user(
            username='editor2',
            email='editor2@example.com',
            password='pass12345',
            role='editor',
        )
        self.journalist = self.User.objects.create_user(
            username='journo2',
            email='journo2@example.com',
            password='pass12345',
            role='journalist',
        )
        self.reader = self.User.objects.create_user(
            username='reader2',
            email='reader2@example.com',
            password='pass12345',
            role='reader',
        )
        self.publisher = Publisher.objects.create(name='Tech Wire', description='Tech publisher')
        self.publisher.editors.add(self.editor)
        self.publisher.journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

    @patch('news_app.services.requests.post')
    def test_signal_sends_email_and_posts_internal_log(self, mock_post):
        """Ensure article approval sends email and writes an internal log."""
        article = Article.objects.create(
            title='Signal story',
            content='Signal body.',
            author=self.journalist,
            publisher=self.publisher,
            approved=False,
        )
        article.approved = True
        article.save()
        article.refresh_from_db()

        self.assertTrue(article.approval_notified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Signal story', mail.outbox[0].subject)
        mock_post.assert_called_once()

    def test_internal_approved_log_endpoint_rejects_bad_key(self):
        """Ensure the internal approval log endpoint rejects invalid API keys."""
        response = self.client.post(
            reverse('news_app_api:approved_article_log'),
            data={'article': 999, 'payload': {'title': 'Bad'}},
            content_type='application/json',
            HTTP_X_INTERNAL_API_KEY='wrong-key',
        )
        self.assertEqual(response.status_code, 401)
