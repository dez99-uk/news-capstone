from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


class IsReaderEditorOrJournalist(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class ArticlePermission(BasePermission):
    message = 'You do not have permission for this article action.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return user.role == User.ROLE_JOURNALIST
        return user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return obj.approved or user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}
        if user.role == User.ROLE_EDITOR:
            return True
        if user.role == User.ROLE_JOURNALIST:
            return obj.author_id == user.id
        return False


class NewsletterPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if user.role == User.ROLE_EDITOR:
            return True
        return obj.author_id == user.id


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.ROLE_EDITOR)


class HasInternalApiKey(BasePermission):
    def has_permission(self, request, view):
        expected_key = view.expected_api_key
        return request.headers.get('X-Internal-API-Key') == expected_key
