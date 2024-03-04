from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Like, UserProfile, User

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(UserProfile)