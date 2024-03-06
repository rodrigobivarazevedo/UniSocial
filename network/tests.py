from django.test import Client,TestCase
from django.contrib.auth import get_user_model
from .models import Post, Like, UserProfile, Comment
from datetime import datetime
import threading

User = get_user_model()

class NetworkTests(TestCase):
    def setUp(self):
        """
        This method is used to set up any initial state needed for the tests. In this case, we're creating two users.
        """
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user5 = User.objects.create_user(username='user5', password='password')

    def test_post_creation(self):

        """
        This method tests whether a Post object can be created successfully.
        """
        post = Post.objects.create(user=self.user1, content="Test content")
        self.assertEqual(post.user, self.user1)
        self.assertEqual(post.content, "Test content")
        self.assertTrue(isinstance(post.created_at, datetime))

    def test_like_creation(self):

        """
        This method tests whether a Like object can be created successfully.
        """
        post = Post.objects.create(user=self.user1, content="Test content")
        like = Like.objects.create(user=self.user2, post=post)
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.post, post)

    def test_user_profile_creation(self):
        """
        This method tests whether a UserProfile object can be created successfully.
        """
        user_profile = UserProfile.objects.create(user=self.user1)
        self.assertEqual(user_profile.user, self.user1)

    def test_comment_creation(self):

        """
        This method tests whether a Comment object can be created successfully.
        """
        post = Post.objects.create(user=self.user1, content="Test content")
        comment = Comment.objects.create(user=self.user2, post=post, content="Test comment")
        self.assertEqual(comment.user, self.user2)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.content, "Test comment")

    def test_concurrent_like_creation(self):
        """
        Test whether multiple users can like a post concurrently.
        """
        post = Post.objects.create(user=self.user1, content="Test content")

        def like_post(user):
            Like.objects.create(user=user, post=post)

        # Create threads for liking the post
        threads = []
        for user in [self.user1, self.user2]:  # Example users
            thread = threading.Thread(target=like_post, args=(user,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check if all likes are created
        likes_count = Like.objects.filter(post=post).count()
        self.assertEqual(likes_count, 2)  # Assuming three users liked the post concurrently

    def test_concurrent_like_creation_without_thread(self):
        """
        Test whether multiple users can like a post concurrently without thread.
        """
        post = Post.objects.create(user=self.user1, content="Test content")

        # Simulate concurrent like creation by executing operations sequentially
        for user in [self.user1, self.user2, self.user5]:  # Example users
            Like.objects.create(user=user, post=post)

        # Check if all likes are created
        likes_count = Like.objects.filter(post=post).count()
        self.assertEqual(likes_count, 3)

