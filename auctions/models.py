from django.db import models
from django.conf import settings
from django.utils import timezone
from network.models import User


class AuctionListing(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    )
 
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add current_price field
    category = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings') 
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return f"Bid of {self.amount} on {self.auction_listing}"


class Comment(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.auction_listing}"