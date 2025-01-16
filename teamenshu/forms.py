from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["recipient", "message"]  # 'receiver'を'recipient'に変更


class CommentForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "コメントを入力...",
            }
        ),
        max_length=500,
    )
