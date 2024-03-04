from django import forms
from .models import AuctionListing, Bid, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 300px;'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 300px;', 'placeholder': 'Enter your bid'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 300px;', 'placeholder': 'Write your comment here'}),
        }

