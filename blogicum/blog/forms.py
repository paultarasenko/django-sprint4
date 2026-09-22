from django import forms

from .models import Comment, Post
from .moderation import is_toxic

MODERATION_ERROR = (
    'Комментарий не проходит модерацию. '
    'Пожалуйста, сформулируйте мысль корректнее.'
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Поле автора здесь намеренно не указано: оно назначается
        # в представлении из request.user.
        fields = (
            'title', 'text', 'pub_date', 'category', 'location', 'image',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': '3'}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if is_toxic(text):
            raise forms.ValidationError(MODERATION_ERROR)
        return text
