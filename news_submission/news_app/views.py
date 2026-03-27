from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from .forms import ArticleApprovalForm
from .models import Article, Newsletter, User


class HomeView(TemplateView):
    template_name = 'news_app/home.html'


class ApprovedArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news_app/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(approved=True).select_related('author', 'publisher')


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    template_name = 'news_app/newsletter_list.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        return Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'news_app/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        user = self.request.user
        queryset = Article.objects.select_related('author', 'publisher')
        if user.role == User.ROLE_READER:
            return queryset.filter(approved=True)
        return queryset


class EditorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.ROLE_EDITOR


class ArticleReviewListView(LoginRequiredMixin, EditorRequiredMixin, ListView):
    model = Article
    template_name = 'news_app/article_review_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(approved=False).select_related('author', 'publisher')


class ArticleApproveView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleApprovalForm
    template_name = 'news_app/article_approve.html'

    def form_valid(self, form):
        form.instance.approved = True
        messages.success(self.request, 'Article approved successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next') or '/review/'


def approve_article_quick(request, pk):
    if not request.user.is_authenticated or request.user.role != User.ROLE_EDITOR:
        messages.error(request, 'Only editors can approve articles.')
        return redirect('news_app:home')
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()
    messages.success(request, f'Approved: {article.title}')
    return redirect('news_app:article_review_list')
