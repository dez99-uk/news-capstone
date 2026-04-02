"""Custom REST framework permission classes for the news application.

These permission classes enforce role-based access control for article,
newsletter, and internal API operations.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


class IsReaderEditorOrJournalist(BasePermission):
    """Allow access only to authenticated application users.

    This simple helper permission is useful where any signed-in user should
    be allowed to continue, regardless of their specific role.
    """

    def has_permission(self, request, view):
        """Check whether the incoming request is authenticated.

        Args:
            request: The REST framework request object.
            view: The view being protected.

        Returns:
            bool: `True` when the request has an authenticated user.
        """
        return bool(request.user and request.user.is_authenticated)


class ArticlePermission(BasePermission):
    """Enforce role-based access rules for article endpoints.

    Readers may view approved content, journalists may create content and edit
    their own articles, and editors may manage any article.
    """

    message = 'You do not have permission for this article action.'

    def has_permission(self, request, view):
        """Check permission before an article object is resolved.

        Args:
            request: The REST framework request object.
            view: The view being protected.

        Returns:
            bool: `True` if the user has permission for the request method.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return user.role == User.ROLE_JOURNALIST
        return user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}

    def has_object_permission(self, request, view, obj):
        """Check permission against a specific article instance.

        Args:
            request: The REST framework request object.
            view: The view being protected.
            obj (Article): The article instance being accessed.

        Returns:
            bool: `True` if the user may act on the supplied article.
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return obj.approved or user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}
        if user.role == User.ROLE_EDITOR:
            return True
        if user.role == User.ROLE_JOURNALIST:
            return obj.author_id == user.id
        return False


class NewsletterPermission(BasePermission):
    """Enforce role-based access rules for newsletter endpoints."""

    def has_permission(self, request, view):
        """Check permission before a newsletter object is resolved.

        Args:
            request: The REST framework request object.
            view: The view being protected.

        Returns:
            bool: `True` when the user may proceed with the request.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.role in {User.ROLE_EDITOR, User.ROLE_JOURNALIST}

    def has_object_permission(self, request, view, obj):
        """Check permission against a specific newsletter instance.

        Args:
            request: The REST framework request object.
            view: The view being protected.
            obj (Newsletter): The newsletter instance being accessed.

        Returns:
            bool: `True` when the object-level action is allowed.
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if user.role == User.ROLE_EDITOR:
            return True
        return obj.author_id == user.id


class IsEditor(BasePermission):
    """Allow access only to authenticated users with the editor role."""

    def has_permission(self, request, view):
        """Determine whether the current user is an authenticated editor.

        Args:
            request: The REST framework request object.
            view: The view being protected.

        Returns:
            bool: `True` if the user is an editor.
        """
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.ROLE_EDITOR)


class HasInternalApiKey(BasePermission):
    """Protect internal endpoints with a shared API key header.

    The permission checks the `X-Internal-API-Key` header against the value
    configured on the view.
    """

    def has_permission(self, request, view):
        """Validate the internal API key supplied by the client.

        Args:
            request: The REST framework request object.
            view: The view containing `expected_api_key`.

        Returns:
            bool: `True` when the header matches the expected key.
        """
        expected_key = view.expected_api_key
        return request.headers.get('X-Internal-API-Key') == expected_key
