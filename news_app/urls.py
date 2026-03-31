from django.urls import path

from .views import (
    ApprovedArticleListView,
    ArticleApproveView,
    ArticleDetailView,
    ArticleReviewListView,
    HomeView,
    NewsletterListView,
    approve_article_quick,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('articles/', ApprovedArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('newsletters/', NewsletterListView.as_view(), name='newsletter_list'),
    path('review/', ArticleReviewListView.as_view(), name='article_review_list'),
    path('review/<int:pk>/approve/', ArticleApproveView.as_view(), name='article_approve'),
    path('review/<int:pk>/quick-approve/', approve_article_quick, name='article_quick_approve'),
]
