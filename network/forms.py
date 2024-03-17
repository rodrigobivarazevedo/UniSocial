from django import forms
from .models import Post, UserProfile
from django.core.validators import MaxLengthValidator
from django.forms import FileInput

from django.forms import Textarea, FileInput

class PostForm(forms.ModelForm):
    hashtags = forms.CharField(max_length=255, required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hashtags separated by spaces'}))

    class Meta:
        model = Post
        fields = ['content', 'hashtags']
        labels = {
            'content': '',  # Empty string to remove the label
            'hashtags': '',  # Empty string to remove the label
        }
        widgets = {
            'content': Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your post content'}),
        }

class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your bio'}),
                           validators=[MaxLengthValidator(300)])

    class Meta:
        model = UserProfile
        fields = ['bio', 'picture']
        labels = {
            'bio': '',  # Empty string to remove the label
            'picture': '',  # Empty string to remove the label
        }
        widgets = {
            'picture': FileInput(attrs={'class': 'form-control-file'}),
        }

