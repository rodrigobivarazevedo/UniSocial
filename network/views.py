from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timezone
import time

from django.db.models import Count


from .forms import PostForm
from .models import User, Post

def time_since(time):
    """
    Convert a timestamp into a human-readable format like Django's timesince filter.
    """
    utc_time = time.astimezone(timezone.utc)  # Convert to UTC
    now = datetime.now()
    time_diff = now - utc_time

    if time_diff.days > 7:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    elif time_diff.days:
        return f"{time_diff.days} days ago"
    elif time_diff.seconds >= 3600:
        hours = time_diff.seconds // 3600
        return f"{hours} hours ago"
    elif time_diff.seconds >= 60:
        minutes = time_diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"

    
def index(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Your post was successfully posted!')
        return render(request, 'network/index.html')
    return render(request, "network/index.html")

def load_posts(request):
    if request.method == "GET":
        start = int(request.GET.get("start") or 0)
        end = int(request.GET.get("end") or (start + 9))
        print(start)
        print(end)
        posts = Post.objects.prefetch_related('comment_set').annotate(
            likes_count=Count('like')).order_by('-created_at')[start:end]

        serialized_posts = []
        for post in posts:
            comments = list(post.comment_set.all().values())
            serialized_post = {
                'id': post.id,
                'content': post.content,
                'created_at': post.created_at,
                'username': post.user.username,
                'likes_count': post.likes_count,
                'comments': comments,
            }
            serialized_posts.append(serialized_post)

        data = {
            'posts': serialized_posts,
        }
        time.sleep(0.5)
        return JsonResponse(data, safe=True)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



