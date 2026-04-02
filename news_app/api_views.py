"""REST API views for the news application.

This module exposes API endpoints for listing, creating, approving, and
managing articles and newsletters, as well as simple supporting endpoints for
users, publishers, and token bootstrap.
"""

from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions, response, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User
from .permissions import ArticlePermission, HasInternalApiKey, IsEditor, NewsletterPermission
from .serializers import (
    ApprovedArticleLogSerializer,
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
    UserSerializer,
)


class ArticleListCreateView(generics.ListCreateAPIView):
    """List articles or create a new article through the API."""

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        """Return articles visible to the current user.

        Readers only receive approved articles, while journalists and editors
        receive a wider dataset for content management.

        Returns:
            QuerySet[Article]: A role-filtered article queryset.
        """
        user = self.request.user
        queryset = Article.objects.select_related('author', 'publisher')
        if user.role == User.ROLE_READER:
            return queryset.filter(approved=True)
        return queryset


class SubscribedArticleListView(generics.ListAPIView):
    """Return approved articles relevant to the authenticated reader."""

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return approved articles from subscribed publishers or journalists.

        Returns:
            QuerySet[Article]: Approved articles for the signed-in reader, or
            an empty queryset for non-reader roles.
        """
        user = self.request.user
        if user.role != User.ROLE_READER:
            return Article.objects.none()
        return Article.objects.filter(
            approved=True,
        ).filter(
            Q(publisher__in=user.subscribed_publishers.all()) |
            Q(author__in=user.subscribed_journalists.all())
        ).distinct().select_related('author', 'publisher')


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single article through the API."""

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]
    queryset = Article.objects.select_related('author', 'publisher')


class ArticleApproveApiView(APIView):
    """Approve an article through the API for editor clients."""

    permission_classes = [IsEditor]

    def post(self, request, pk):
        """Approve the selected article and return the updated serializer data.

        Args:
            request: The REST framework request object.
            pk (int): Primary key of the article to approve.

        Returns:
            Response: JSON response containing the approved article.
        """
        article = generics.get_object_or_404(Article, pk=pk)
        article.approved = True
        article.save()
        return response.Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)


class NewsletterListCreateView(generics.ListCreateAPIView):
    """List newsletters or create a new newsletter through the API."""

    serializer_class = NewsletterSerializer
    permission_classes = [NewsletterPermission]

    def get_queryset(self):
        """Return newsletters with related records optimised for API output.

        Returns:
            QuerySet[Newsletter]: Newsletter queryset with select and prefetch
            optimisation.
        """
        return Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class NewsletterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single newsletter through the API."""

    serializer_class = NewsletterSerializer
    permission_classes = [NewsletterPermission]
    queryset = Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class PublisherListView(generics.ListAPIView):
    """List all publishers exposed by the API."""

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class UserListView(generics.ListAPIView):
    """List all users exposed by the API."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ApprovedArticleLogCreateView(generics.CreateAPIView):
    """Create an internal approved-article log entry.

    Access is protected by a shared API key so that only trusted internal
    callers can record approval events.
    """

    queryset = ApprovedArticleLog.objects.all()
    serializer_class = ApprovedArticleLogSerializer
    permission_classes = [HasInternalApiKey]
    expected_api_key = settings.INTERNAL_API_KEY


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bootstrap_token(request):
    """Return an authentication token for valid user credentials.

    Args:
        request: The REST framework request object containing username and
            password in the request body.

    Returns:
        Response: A token payload on success or an error message on failure.

    Example:
        POST /api/login/
        {
            "username": "editor",
            "password": "pass12345"
        }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return response.Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    from django.contrib.auth import authenticate

    user = authenticate(username=username, password=password)
    if not user:
        return response.Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return response.Response({'token': token.key}, status=status.HTTP_200_OK)
