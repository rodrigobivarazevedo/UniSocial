from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count
import json
from django.contrib.auth.decorators import login_required
#from django.views.decorators.cache import cache_page
from django.templatetags.static import static
from django.utils.timesince import timesince
from django.utils.timezone import now
from django.db.models import Q


from .forms import PostForm, UserProfileForm
from .models import Post, Comment, Like, UserProfile, User

    
def index(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Your post was successfully posted!')
            request.session['messages'] = []

            post_id = post.id  # Assign the post ID
        return render(request, 'network/index.html', {'post_id': post_id})
    return render(request, "network/index.html")


@login_required
def load_posts(request):
    if request.method == "GET" and request.GET.get("user") == "all":
        start = int(request.GET.get("start") or 0)
        end = int(request.GET.get("end") or (start + 9))
        
        # Annotate the likes count and prefetch related comments for each post
        posts = Post.objects.prefetch_related('comment_set').annotate(
            likes_count=Count('like')).order_by('-created_at')[start:end]

        serialized_posts = []
        for post in posts:
            # Fetch the precalculated likes count
            likes_count = getattr(post, 'likes_count', 0)
            time_difference = timesince(post.created_at, now())
            serialized_post = {
                'id': post.id,
                'content': post.content,
                'created_at': time_difference,
                'username': post.user.username,
                'profile_pic': post.user.userprofile.picture.url if post.user.userprofile.picture else static('network/profile_placeholder.png'),
                'likes_count': likes_count,  # Use precalculated likes count
                'comments_count': post.comment_set.count()  # Recalculate comments count
            }
            serialized_posts.append(serialized_post)

        data = {
            'posts': serialized_posts,
        }
        return JsonResponse(data, safe=True, status=200)
    
    elif request.method == "GET" and request.GET.get("user") == "following":
        start = int(request.GET.get("start") or 0)
        end = int(request.GET.get("end") or (start + 9))

        # Get the current user
        user_profile = get_object_or_404(UserProfile, user=request.user)
    
        # Get the users that the current user is following
        following_users = user_profile.following.all()
    
        # Annotate the likes count and prefetch related comments for the posts of the following users
        posts = Post.objects.filter(user__in=following_users).prefetch_related('comment_set').annotate(
            likes_count=Count('like')).order_by('-created_at')[start:end]

        serialized_posts = []
        for post in posts:
            # Fetch the precalculated likes count
            likes_count = getattr(post, 'likes_count', 0)
            time_difference = timesince(post.created_at, now())
            serialized_post = {
                'id': post.id,
                'content': post.content,
                'created_at': time_difference,
                'username': post.user.username,
                'profile_pic': post.user.userprofile.picture.url if post.user.userprofile.picture else static('network/profile_placeholder.png'),
                'likes_count': likes_count,  # Use precalculated likes count
                'comments_count': post.comment_set.count()  # Recalculate comments count
            }
            serialized_posts.append(serialized_post)

        data = {
            'posts': serialized_posts,
        }
        return JsonResponse(data, safe=True, status=200)
    
    
    elif request.method == "GET" and request.GET.get("user") != "all" and request.GET.get("user") != "following":
        start = int(request.GET.get("start") or 0)
        end = int(request.GET.get("end") or (start + 9))

        username = request.GET.get("user")
        user = get_object_or_404(User, username=username)  # Fetch the User object

        # Annotate the likes count and prefetch related comments for each post
        posts = Post.objects.filter(user=user).prefetch_related('comment_set').annotate(
            likes_count=Count('like')).order_by('-created_at')[start:end]

        serialized_posts = []
        for post in posts:
            # Fetch the precalculated likes count
            likes_count = getattr(post, 'likes_count', 0)
            time_difference = timesince(post.created_at, now())
            serialized_post = {
                'id': post.id,
                'content': post.content,
                'created_at': time_difference,
                'username': post.user.username,
                'likes_count': likes_count,  # Use precalculated likes count
                'comments_count': post.comment_set.count()  # Recalculate comments count
            }
            serialized_posts.append(serialized_post)

        data = {
            'posts': serialized_posts,
        }
        return JsonResponse(data, safe=True, status=200)
    

@login_required
def comments(request):
    
    data = {}
    if request.method == "GET":
        post_id = int(request.GET.get("post_id"))
        comments = Comment.objects.filter(post=post_id)
        serialized_comments = []
        for comment in comments:
            time_difference = timesince(comment.created_at, now())
            serialized_comment = {
                'id': comment.id,
                'user': comment.user.username,
                'content': comment.content, 
                'time': time_difference,
            }
            serialized_comments.append(serialized_comment)

        data['comments'] = serialized_comments  # Add serialized comments to the response

        return JsonResponse(data, safe=True, status=200)

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

#@cache_page(60 * 5)  # Cache for 5 minutes
@login_required
def profile(request, username):
    # Get the user profile based on the username
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    
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
        'is_following': is_following,
        'can_follow': can_follow,
    }
    return render(request, 'network/profile.html', context)

#@cache_page(60 * 5)  # Cache for 5 minutes
def following(request, username):
    # Get the user profile based on the username
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    # If it's a GET request
    if request.method == 'GET':
        # Check if the request is for following or followers
        if 'usersfollowing' in request.GET:
            # Query the users that the current user is following
            following_users = UserProfile.objects.filter(followers=user_profile.user)
            following_data = []
            for profile in following_users:
                following_data.append({
                    'username': profile.user.username,
                    'profile_pic': profile.picture.url if profile.picture else static('network/profile_placeholder.png') # Include profile picture URL if available
                })
            return JsonResponse({'following_users': following_data})
        elif 'usersfollowers' in request.GET:
            # Query the users who are following the current user
            followers = UserProfile.objects.filter(following=user_profile.user)
            followers_data = []
            for profile in followers:
                followers_data.append({
                    'username': profile.user.username,
                    'profile_pic': profile.picture.url if profile.picture else static('network/profile_placeholder.png')  # Include profile picture URL if available
                })
            return JsonResponse({'followers': followers_data})
        else:
            # If it's not a valid request, render the HTML template
            context = {
                'user_profile': user_profile,
            }
            return render(request, 'network/following.html', context)
    else:
        # Handle other HTTP methods if needed
        return HttpResponseNotAllowed(['GET'])

    

@login_required
def follow(request, username):
    # Get the user to follow
    user_to_follow = get_object_or_404(User, username=username)
    # Get the current user's UserProfile instance
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Add the current user to the followers of the user_to_follow
    user_to_follow_profile = UserProfile.objects.get(user=user_to_follow)
    user_to_follow_profile.followers.add(request.user)
    
    # Add the user_to_follow to the current user's following list
    user_profile.following.add(user_to_follow)

    return redirect('profile', username=username)

@login_required
def unfollow(request, username):
    # Get the user to unfollow
    user_to_unfollow = get_object_or_404(User, username=username)
    # Get the current user's UserProfile instance
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Remove the current user from the followers of the user_to_unfollow
    user_to_unfollow_profile = UserProfile.objects.get(user=user_to_unfollow)
    user_to_unfollow_profile.followers.remove(request.user)
    
    # Remove the user_to_unfollow from the current user's following list
    user_profile.following.remove(user_to_unfollow)

    return redirect('profile', username=username)

def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)  # Redirect to profile page after editing
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'network/edit_profile.html', {'form': form})



def search_users(request):
    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET.get('query', '')
        if query:
        
            # Filter users based on username starting with the query
            users = User.objects.filter(username__startswith=query)
            # Filter user profiles based on the associated user objects
            user_profiles = UserProfile.objects.filter(user__in=users)
            # Serialize the users' data
            serialized_users = [{'username': profile.user.username,
                                'profile_pic': profile.picture.url if profile.picture else static('network/profile_placeholder.png')}
                                for profile in user_profiles]
            # Return the serialized data as JSON response
            return JsonResponse({'users': serialized_users})
        else: 
            return JsonResponse({'users': ""})
    else:
        # If the request method is not GET or query parameter is missing, return an error response
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

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
            messages.error(request, 'Invalid username and/or password.')
            request.session['messages'] = []

            return render(request, "network/login.html")
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
            messages.error(request, 'Passwords must match.')
            request.session['messages'] = []

            return render(request, "network/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            # Create the user profile
            user_profile = UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created')
            request.session['messages'] = []

            return redirect("index")
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            request.session['messages'] = []

            return render(request, "network/register.html")
    else:
        return render(request, "network/register.html")



