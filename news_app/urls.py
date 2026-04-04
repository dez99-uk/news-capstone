"""URL routes for the HTML interface of the news application.

The URL configuration in this module connects browser-facing routes to the
class-based and function-based views defined in `news_app.views`.
"""

from django.urls import path

from .views import (
    ApprovedArticleListView,
    ArticleApproveView,
    ArticleDetailView,
    ArticleReviewListView,
    HomeView,
    NewsletterListView,
    RegisterView,
    approve_article_quick,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('articles/', ApprovedArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('newsletters/', NewsletterListView.as_view(), name='newsletter_list'),
    path('review/', ArticleReviewListView.as_view(), name='article_review_list'),
    path('review/<int:pk>/approve/', ArticleApproveView.as_view(), name='article_approve'),
    path('review/<int:pk>/quick-approve/', approve_article_quick, name='article_quick_approve'),
]