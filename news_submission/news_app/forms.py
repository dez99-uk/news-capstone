from django import forms

from .models import Article


class ArticleApprovalForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['approved']
