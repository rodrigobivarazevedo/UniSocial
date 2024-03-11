from django import forms
from .models import Post, UserProfile
from django.core.validators import MaxLengthValidator
from django.forms import FileInput

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
                           validators=[MaxLengthValidator(300)])

    class Meta:
        model = UserProfile
        fields = ['bio', 'picture']
        widgets = {
            'picture': FileInput(attrs={'class': 'form-control-file'}),
        }