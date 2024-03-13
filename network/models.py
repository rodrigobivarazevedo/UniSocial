from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timesince import timesince
from datetime import datetime

class User(AbstractUser):
    watchlist = models.ManyToManyField('auctions.AuctionListing', related_name='watchlist_users')


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def humanized_timestamp(self):
        return timesince(self.created_at, datetime.now())

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='followers')
    following = models.ManyToManyField(User, related_name='following')
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='profile_pics/', blank=True)
    
   
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)