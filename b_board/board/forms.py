from django import forms
from django.forms import ModelForm

from .models import Article, Comment


class PostForm(ModelForm):
    ''' Form for creation Post '''

    class Meta:
        model = Article
        fields = ['title', 'category', 'text_body']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'text_body': forms.Textarea(attrs={'class': 'form-control'}),
        }


class EditForm(ModelForm):
    ''' Form for editing Post '''

    class Meta:
        model = Article
        fields = ['title', 'text_body', 'category']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'text_body': forms.Textarea(attrs={'class': 'form-control'}),
        }


class CommentForm(ModelForm):
    ''' Form for creation response/comment '''

    class Meta:
        model = Comment
        fields = ['comment_body', ]

        widgets = {
            'text_body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type comment text here ...'}),
        }
