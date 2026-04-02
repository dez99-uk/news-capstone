"""Form classes used by the server-rendered news application views.

The forms in this module provide validation and presentation logic for common
workflows such as approving articles from the editor interface.
"""

from django import forms

from .models import Article


class ArticleApprovalForm(forms.ModelForm):
    """Form used by editors to mark an article as approved or not approved.

    The form intentionally exposes only the `approved` field because the view
    that uses it is focused on editorial review rather than full article editing.
    """

    class Meta:
        """Metadata for the article approval form."""

        model = Article
        fields = ['approved']
