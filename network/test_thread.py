from django.test import TransactionTestCase
from django.db import connection
from django.contrib.auth import get_user_model
from .models import Post, Like, UserProfile, Comment
from datetime import datetime


User = get_user_model()
import threading

class ConcurrentLikeCreationTestCase(TransactionTestCase):
    def setUp(self):
        # Create example users
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

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
        self.assertEqual(likes_count, 2)  # Assuming two users liked the post concurrently
