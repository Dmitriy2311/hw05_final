from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма добавления поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 7}),
            'group': forms.Select(attrs={'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    """Форма добавления комментария."""
    
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 7}),
        }
        