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
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        user = self.request.user
        queryset = Article.objects.select_related('author', 'publisher')
        if user.role == User.ROLE_READER:
            return queryset.filter(approved=True)
        return queryset


class SubscribedArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
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
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]
    queryset = Article.objects.select_related('author', 'publisher')


class ArticleApproveApiView(APIView):
    permission_classes = [IsEditor]

    def post(self, request, pk):
        article = generics.get_object_or_404(Article, pk=pk)
        article.approved = True
        article.save()
        return response.Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)


class NewsletterListCreateView(generics.ListCreateAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [NewsletterPermission]

    def get_queryset(self):
        return Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class NewsletterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [NewsletterPermission]
    queryset = Newsletter.objects.select_related('author', 'publisher').prefetch_related('articles')


class PublisherListView(generics.ListAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ApprovedArticleLogCreateView(generics.CreateAPIView):
    queryset = ApprovedArticleLog.objects.all()
    serializer_class = ApprovedArticleLogSerializer
    permission_classes = [HasInternalApiKey]
    expected_api_key = settings.INTERNAL_API_KEY


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bootstrap_token(request):
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
