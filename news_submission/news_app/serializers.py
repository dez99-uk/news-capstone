from rest_framework import serializers

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class ArticleSerializer(serializers.ModelSerializer):
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
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'author_id', 'publisher', 'publisher_id',
            'created_at', 'updated_at', 'approved', 'approved_at',
        ]
        read_only_fields = ['approved', 'approved_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['author'] = request.user
        validated_data['approved'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('author', None)
        validated_data.pop('approved', None)
        return super().update(instance, validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
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
        model = Newsletter
        fields = [
            'id', 'title', 'description', 'created_at', 'updated_at',
            'author', 'author_id', 'publisher', 'publisher_id', 'articles',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        articles = validated_data.pop('articles', [])
        request = self.context['request']
        validated_data['author'] = request.user if request.user.role == User.ROLE_JOURNALIST else validated_data['author']
        newsletter = super().create(validated_data)
        newsletter.articles.set(articles)
        return newsletter

    def update(self, instance, validated_data):
        articles = validated_data.pop('articles', None)
        newsletter = super().update(instance, validated_data)
        if articles is not None:
            newsletter.articles.set(articles)
        return newsletter


class ApprovedArticleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedArticleLog
        fields = ['id', 'article', 'payload', 'received_at']
        read_only_fields = ['id', 'received_at']
