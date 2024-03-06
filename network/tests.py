from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post, Like, UserProfile, Comment
from datetime import datetime

User = get_user_model()

class NetworkTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_post_creation(self):
        post = Post.objects.create(user=self.user1, content="Test content")
        self.assertEqual(post.user, self.user1)
        self.assertEqual(post.content, "Test content")
        self.assertTrue(isinstance(post.created_at, datetime))

    def test_like_creation(self):
        post = Post.objects.create(user=self.user1, content="Test content")
        like = Like.objects.create(user=self.user2, post=post)
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.post, post)

    def test_user_profile_creation(self):
        user_profile = UserProfile.objects.create(user=self.user1)
        self.assertEqual(user_profile.user, self.user1)

    def test_comment_creation(self):
        post = Post.objects.create(user=self.user1, content="Test content")
        comment = Comment.objects.create(user=self.user2, post=post, content="Test comment")
        self.assertEqual(comment.user, self.user2)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.content, "Test comment")


"""
setUp: This method is used to set up any initial state needed for the tests. In this case, we're creating two users.

test_post_creation: This method tests whether a Post object can be created successfully.

test_like_creation: This method tests whether a Like object can be created successfully.

test_user_profile_creation: This method tests whether a UserProfile object can be created successfully.

test_comment_creation: This method tests whether a Comment object can be created successfully.
"""