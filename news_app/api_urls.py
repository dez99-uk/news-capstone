"""URL routes for the REST API portion of the news application."""

from django.urls import path

from .api_views import (
    ApprovedArticleLogCreateView,
    ArticleApproveApiView,
    ArticleDetailView,
    ArticleListCreateView,
    NewsletterDetailView,
    NewsletterListCreateView,
    PublisherListView,
    SubscribedArticleListView,
    UserListView,
    bootstrap_token,
)

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article_list_create'),
    path('articles/subscribed/', SubscribedArticleListView.as_view(), name='subscribed_articles'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/approve/', ArticleApproveApiView.as_view(), name='article_approve'),
    path('newsletters/', NewsletterListCreateView.as_view(), name='newsletter_list_create'),
    path('newsletters/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('publishers/', PublisherListView.as_view(), name='publisher_list'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('approved/', ApprovedArticleLogCreateView.as_view(), name='approved_article_log'),
    path('login/', bootstrap_token, name='api_login'),
]
