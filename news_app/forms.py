"""Form classes used by the server-rendered news application views.

The forms in this module provide validation and presentation logic for common
workflows such as approving articles from the editor interface and registering
new user accounts for the application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, User


class ArticleApprovalForm(forms.ModelForm):
    """Form used by editors to mark an article as approved or not approved.

    The form intentionally exposes only the `approved` field because the view
    that uses it is focused on editorial review rather than full article editing.
    """

    class Meta:
        """Metadata for the article approval form."""

        model = Article
        fields = ['approved']


class UserRegistrationForm(UserCreationForm):
    """Form used to register a new user account for the application.

    The form allows a new user to create an account with a username, email
    address, role, and password. It provides a visible registration path so
    users and assessors can create an account before logging in.
    """

    class Meta:
        """Metadata for the user registration form."""

        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']