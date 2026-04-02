"""REST framework serializers for the news application.

Serializers in this module convert model instances to API-friendly
representations and validate incoming payloads for create and update actions.
"""

from rest_framework import serializers

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher details for read-only and list API responses."""

    class Meta:
        """Serializer metadata for publisher output."""

        model = Publisher
        fields = ['id', 'name', 'description', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serialize lightweight user information for nested API responses."""

    class Meta:
        """Serializer metadata for user output."""

        model = User
        fields = ['id', 'username', 'email', 'role']


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize article objects for list, detail, create, and update endpoints.

    The serializer presents nested author and publisher information for read
    operations while still accepting primary keys for write operations.
    """

    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        source='author',
        queryset=User.objects.filter(role=User.ROLE_JOURNALIST),
        write_only=True,
        required=False,
    )
    publisher = PublisherSerializer(read_only=True)
    publisher_id = serializers.PrimaryKeyRelatedField(
        source='publisher',
        queryset=Publisher.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        """Serializer metadata for article output and validation."""

        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'author_id', 'publisher', 'publisher_id',
            'created_at', 'updated_at', 'approved', 'approved_at',
        ]
        read_only_fields = ['approved', 'approved_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create a new article owned by the authenticated user.

        Args:
            validated_data (dict): Validated serializer input.

        Returns:
            Article: The newly created article instance.
        """
        request = self.context['request']
        validated_data['author'] = request.user
        validated_data['approved'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update an article while protecting author and approval fields.

        Args:
            instance (Article): The existing article instance.
            validated_data (dict): Validated serializer input.

        Returns:
            Article: The updated article instance.
        """
        validated_data.pop('author', None)
        validated_data.pop('approved', None)
        return super().update(instance, validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletter objects for API responses and edits."""

    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        source='author',
        queryset=User.objects.filter(role=User.ROLE_JOURNALIST),
        write_only=True,
        required=False,
    )
    articles = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all(), many=True)
    publisher = PublisherSerializer(read_only=True)
    publisher_id = serializers.PrimaryKeyRelatedField(
        source='publisher',
        queryset=Publisher.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        """Serializer metadata for newsletter output and validation."""

        model = Newsletter
        fields = [
            'id', 'title', 'description', 'created_at', 'updated_at',
            'author', 'author_id', 'publisher', 'publisher_id', 'articles',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """Create a newsletter and attach the supplied article list.

        Args:
            validated_data (dict): Validated serializer input.

        Returns:
            Newsletter: The newly created newsletter instance.
        """
        articles = validated_data.pop('articles', [])
        request = self.context['request']
        validated_data['author'] = request.user if request.user.role == User.ROLE_JOURNALIST else validated_data['author']
        newsletter = super().create(validated_data)
        newsletter.articles.set(articles)
        return newsletter

    def update(self, instance, validated_data):
        """Update a newsletter and replace its article list when provided.

        Args:
            instance (Newsletter): The existing newsletter instance.
            validated_data (dict): Validated serializer input.

        Returns:
            Newsletter: The updated newsletter instance.
        """
        articles = validated_data.pop('articles', None)
        newsletter = super().update(instance, validated_data)
        if articles is not None:
            newsletter.articles.set(articles)
        return newsletter


class ApprovedArticleLogSerializer(serializers.ModelSerializer):
    """Serialize internal approved-article log entries."""

    class Meta:
        """Serializer metadata for approved article logs."""

        model = ApprovedArticleLog
        fields = ['id', 'article', 'payload', 'received_at']
        read_only_fields = ['id', 'received_at']
