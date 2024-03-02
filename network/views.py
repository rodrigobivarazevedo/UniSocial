from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count
import json
from django.contrib.auth.decorators import login_required




from .forms import PostForm
from .models import User, Post, Comment, Like, UserProfile

    
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
        
        # Annotate the likes count and prefetch related comments for each post
        posts = Post.objects.prefetch_related('comment_set').annotate(
            likes_count=Count('like')).order_by('-created_at')[start:end]

        serialized_posts = []
        for post in posts:
            # Fetch the precalculated likes count
            likes_count = getattr(post, 'likes_count', 0)

            serialized_post = {
                'id': post.id,
                'content': post.content,
                'created_at': post.created_at,
                'username': post.user.username,
                'likes_count': likes_count,  # Use precalculated likes count
                'comments_count': post.comment_set.count()  # Recalculate comments count
            }
            serialized_posts.append(serialized_post)

        data = {
            'posts': serialized_posts,
        }
        return JsonResponse(data, safe=True)
    



@login_required
def comments(request):
    
    data = {}
    if request.method == "GET":
        post_id = int(request.GET.get("post_id"))
        comments = Comment.objects.filter(post=post_id)
        serialized_comments = []
        for comment in comments:
            serialized_comment = {
                'id': comment.id,
                'user': comment.user.username,
                'content': comment.content, 
                'time': comment.created_at,
            }
            serialized_comments.append(serialized_comment)

        data['comments'] = serialized_comments  # Add serialized comments to the response

        return JsonResponse(data, safe=True)

    elif request.method == "POST":
        # Handle the case where posting a comment
        data = json.loads(request.body)
        post_id = data.get('post_id')
        content = data.get('comment_content')
        if post_id and content:
            post = Post.objects.get(pk=post_id)
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            # Increment like count
            comments_count = Comment.objects.filter(post=post).count()
            return JsonResponse({'message': 'comment added successfully', 'comments_count': comments_count}, status=201)
        
        else:
            return JsonResponse({'error': 'Invalid request: No post_id or comment_content provided'}, status=400)
        
   
@login_required
# This view is CSRF protected by default
def likes(request):
    if request.method == 'POST':
        # Parse JSON request body
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            if post_id:
                post = Post.objects.get(pk=post_id)
                like, created = Like.objects.get_or_create(user=request.user, post=post)
                if created:
                    # Increment like count
                    likes_count = Like.objects.filter(post=post).count()
                    return JsonResponse({'message': 'Like added successfully', 'likes_count': likes_count}, status=201)
                else:
                    # Like already exists
                    return JsonResponse({'message': 'Like already exists'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid request: No post_id provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
    
    elif request.method == 'GET':
        # Handle GET requests if needed
        pass

@login_required
def profile(request, username):
    # Get the user profile based on the username
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)

    # Fetch all posts by the user
    posts = Post.objects.filter(user=user).order_by('-created_at')

    for post in posts:
            post.likes_count = Like.objects.filter(post=post).count()  # Count the number of likes for each post
            post.comments = Comment.objects.filter(post=post)
      

    is_following = False
    can_follow = False

    if request.user.is_authenticated:
        # Check if the user is visiting their own profile
        if request.user == user:
            can_follow = False  # Prevent user from following themselves
        else:
            can_follow = True
            # Determine if the current user is following this profile user
            is_following = request.user in user_profile.followers.all()

    context = {
        'user_profile': user_profile,
        'user_posts': posts,
        'is_following': is_following,
        'can_follow': can_follow,
    }
    return render(request, 'network/profile.html', context)

@login_required
def follow(request, username):
    # Get the user profile to follow
    user_to_follow = get_object_or_404(UserProfile, user__username=username)

    # Add the current user to the followers of the user_to_follow
    user_to_follow.followers.add(request.user)

    return redirect('profile', username=username)

@login_required
def unfollow(request, username):
    # Get the user profile to unfollow
    user_to_unfollow = get_object_or_404(UserProfile, user__username=username)

    # Remove the current user from the followers of the user_to_unfollow
    user_to_unfollow.followers.remove(request.user)

    return redirect('profile', username=username)


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
            # Create the user profile
            user_profile = UserProfile.objects.create(user=user)
            login(request, user)
            return redirect("index")
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
    else:
        return render(request, "network/register.html")



