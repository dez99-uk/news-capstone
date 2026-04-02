"""Class-based and function-based HTML views for the news application.

The views in this module power the browser-facing part of the project. They
provide list, detail, review, and approval screens for the article and
newsletter workflows used by readers, journalists, and editors.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from .forms import ArticleApprovalForm
from .models import Article, Newsletter, User


class HomeView(TemplateView):
    """Render the landing page for the application."""

    template_name = 'news_app/home.html'


class ApprovedArticleListView(LoginRequiredMixin, ListView):
    """Display approved articles to authenticated users.

    Readers should only see content that has been approved by an editor, and
    this view enforces that rule at the queryset level.
    """

    model = Article
    template_name = 'news_app/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        """Return approved articles with related author and publisher data.

        Returns:
            QuerySet[Article]: Approved articles ordered by model defaults.
        """
        return Article.objects.filter(approved=True).select_related('author', 'publisher')


class NewsletterListView(LoginRequiredMixin, ListView):
    """Display newsletters available to authenticated users."""

    model = Newsletter
    template_name = 'news_app/newsletter_list.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        """Return newsletters with related author, publisher, and articles.

        Returns:
            QuerySet[Newsletter]: Optimised queryset for newsletter listing.
        """
        return Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """Display the details of a single article.

    Readers are limited to approved content, while journalists and editors may
    access a wider set of article objects according to their role.
    """

    model = Article
    template_name = 'news_app/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        """Restrict visible articles according to the requesting user's role.

        Returns:
            QuerySet[Article]: A queryset filtered for the current role.
        """
        user = self.request.user
        queryset = Article.objects.select_related('author', 'publisher')
        if user.role == User.ROLE_READER:
            return queryset.filter(approved=True)
        return queryset


class EditorRequiredMixin(UserPassesTestMixin):
    """Require the current user to be an authenticated editor."""

    def test_func(self):
        """Return `True` only when the current user has the editor role.

        Returns:
            bool: Whether the request is made by an authenticated editor.
        """
        return self.request.user.is_authenticated and self.request.user.role == User.ROLE_EDITOR


class ArticleReviewListView(LoginRequiredMixin, EditorRequiredMixin, ListView):
    """Display unapproved articles for editorial review."""

    model = Article
    template_name = 'news_app/article_review_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        """Return pending articles for the editor review screen.

        Returns:
            QuerySet[Article]: Articles that have not yet been approved.
        """
        return Article.objects.filter(approved=False).select_related('author', 'publisher')


class ArticleApproveView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    """Allow editors to approve an article using a confirmation form."""

    model = Article
    form_class = ArticleApprovalForm
    template_name = 'news_app/article_approve.html'

    def form_valid(self, form):
        """Mark the article as approved before saving the form.

        Args:
            form (ArticleApprovalForm): The validated approval form.

        Returns:
            HttpResponse: The response returned by the parent update view.
        """
        form.instance.approved = True
        messages.success(self.request, 'Article approved successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        """Return the redirect target after a successful approval action.

        Returns:
            str: A `next` URL when supplied, otherwise the review list URL.
        """
        return self.request.GET.get('next') or '/review/'


def approve_article_quick(request, pk):
    """Approve an article immediately without rendering the update form.

    This shortcut supports a faster editor workflow from the review list page.

    Args:
        request: Django HTTP request object.
        pk (int): Primary key of the article to approve.

    Returns:
        HttpResponseRedirect: Redirect to the review list or home page.

    Raises:
        Http404: Raised if the supplied article does not exist.
    """
    if not request.user.is_authenticated or request.user.role != User.ROLE_EDITOR:
        messages.error(request, 'Only editors can approve articles.')
        return redirect('news_app:home')
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()
    messages.success(request, f'Approved: {article.title}')
    return redirect('news_app:article_review_list')
