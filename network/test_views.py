from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Post, Like, UserProfile, Comment
from datetime import datetime
from django.urls import reverse
import json


User = get_user_model()


class NetworkClientTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client = Client()
        self.client.force_login(self.user)

    def test_index_view(self):
        """
        Test the index view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Send a POST request to the index view
        response = self.client.post(reverse('index'), {'content': 'Test post content'})

        # Check if the post was successfully created
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your post was successfully posted!')

    def test_load_posts_view(self):
        """
        Test the load_posts view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Send a GET request to the load_posts view for all users
        response = self.client.get(reverse('load_posts') + '?user=all')

        # Check if the response contains posts data
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.json())

        # Send a GET request to the load_posts view for following users
        response = self.client.get(reverse('load_posts') + '?user=following')

        # Check if the response contains posts data
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.json())

        # Send a GET request to the load_posts view for a specific user
        response = self.client.get(reverse('load_posts') + f'?user={self.user.username}')

        # Check if the response contains posts data
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.json())

    def test_get_comments(self):
        """
        Test the GET method for the comments view.
        """
        # Create a post
        post = Post.objects.create(user=self.user, content='Test post content')
        
        # Create comments for the post
        Comment.objects.create(user=self.user, post=post, content='Comment 1')
        Comment.objects.create(user=self.user, post=post, content='Comment 2')
        
        # Send a GET request to the comments view
        response = self.client.get(reverse('comments') + f'?post_id={post.id}')
        
        # Check if the response contains comments data
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.json())
        self.assertEqual(len(response.json()['comments']), 2)  # Check if there are two comments

    def test_post_comment(self):
        """
        Test the POST method for posting a comment.
        """
        # Create a post
        post = Post.objects.create(user=self.user, content='Test post content')

        # Send a POST request to post a comment
        data = {'post_id': post.id, 'comment_content': 'Test comment'}
        response = self.client.post(reverse('comments'), data=json.dumps(data), content_type='application/json')

        # Check if the comment was successfully posted
        self.assertEqual(response.status_code, 201)
        
        # Check if the comment count is incremented
        comments_count = Comment.objects.filter(post=post).count()
        self.assertEqual(comments_count, 1)

    def test_likes_view(self):
        """
        Test the likes view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Create a post
        post_response = self.client.post(reverse('index'), {'content': 'Test post content'})

        # Send a POST request to the likes view
        like_response = self.client.post(reverse('likes'), {'post_id': post_response.context["post_id"]})

        # Check if the like was successfully added
        self.assertIn(like_response.status_code, [200, 201])

    def test_profile_view(self):
        """
        Test the profile view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Send a GET request to the profile view
        response = self.client.get(reverse('profile', args=[self.user.username]))

        # Check if the response contains user profile data
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_profile', response.context)

    def test_following_view(self):
        """
        Test the following view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Send a GET request to the following view
        response = self.client.get(reverse('following', args=[self.user.username]))

        # Check if the response contains user profile data
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_profile', response.context)

    def test_follow_view(self):
        """
        Test the follow view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Create another user
        user2 = User.objects.create_user(username='test_user2', password='password')

        # Send a POST request to the follow view
        follow_response = self.client.post(reverse('follow', args=[user2.username]))

        # Check if the user was successfully followed
        self.assertEqual(follow_response.status_code, 302)  # Redirect status code

    def test_unfollow_view(self):
        """
        Test the unfollow view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Create another user
        user2 = User.objects.create_user(username='test_user2', password='password')

        # Follow the other user
        self.client.post(reverse('follow', args=[user2.username]))

        # Send a POST request to the unfollow view
        unfollow_response = self.client.post(reverse('unfollow', args=[user2.username]))

        # Check if the user was successfully unfollowed
        self.assertEqual(unfollow_response.status_code, 302)  # Redirect status code

    def test_login_view(self):
        """
        Test the login view.
        """
        # Send a POST request to the login view
        response = self.client.post(reverse('login'), {'username': 'test_user', 'password': 'password'})

        # Check if the user is redirected to the index page after login
        self.assertRedirects(response, reverse('index'))

    def test_logout_view(self):
        """
        Test the logout view.
        """
        # Log in the user
        self.client.force_login(self.user)

        # Send a POST request to the logout view
        response = self.client.post(reverse('logout'))

        # Check if the user is redirected to the index page after logout
        self.assertRedirects(response, reverse('index'))

    def test_register_view(self):
        """
        Test the register view.
        """
        # Send a POST request to the register view
        response = self.client.post(reverse('register'), {'username': 'test_user2', 'email': 'test@example.com', 'password': 'password', 'confirmation': 'password'})

        # Check if the user is redirected to the index page after registration
        self.assertRedirects(response, reverse('index'))

