from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from network.models import User
from .models import AuctionListing, Bid, Comment
from decimal import Decimal

class AuctionsTests(TestCase):
    def setUp(self):
        """
        This method sets up initial state for the tests by creating a user and an auction listing.
        """
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.listing = AuctionListing.objects.create(
            title='Test Listing',
            description='Test Description',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            starting_bid=Decimal('10.00'),
            category='Test Category',
            seller=self.user
        )

    def test_auction_listing_creation(self):

        """
        Tests whether an AuctionListing object can be created successfully and if its attributes are set correctly.
        """
        self.assertEqual(self.listing.title, 'Test Listing')
        self.assertEqual(self.listing.description, 'Test Description')
        self.assertEqual(self.listing.starting_bid, Decimal('10.00'))
        self.assertEqual(self.listing.category, 'Test Category')
        self.assertEqual(self.listing.seller, self.user)

    def test_bid_creation(self):
        """
        Tests whether a Bid object can be created successfully and if its attributes are set correctly.
        """
        bid = Bid.objects.create(amount=Decimal('15.00'), bidder=self.user, auction_listing=self.listing)
        self.assertEqual(bid.amount, Decimal('15.00'))
        self.assertEqual(bid.bidder, self.user)
        self.assertEqual(bid.auction_listing, self.listing)

    def test_comment_creation(self):

        """
        Tests whether a Comment object can be created successfully and if its attributes are set correctly.
        """
        comment = Comment.objects.create(content='Test Comment', commenter=self.user, auction_listing=self.listing)
        self.assertEqual(comment.content, 'Test Comment')
        self.assertEqual(comment.commenter, self.user)
        self.assertEqual(comment.auction_listing, self.listing)



