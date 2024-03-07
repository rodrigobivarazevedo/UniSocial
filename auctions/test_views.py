from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import AuctionListing, Bid, Comment


User = get_user_model()

class AuctionsAppTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client = Client()
        self.client.force_login(self.user)

        self.listing = AuctionListing.objects.create(title='Test Listing', seller=self.user, starting_bid=100)

    def test_auctions_view(self):
        """Test auctions view"""
        response = self.client.get(reverse('auctions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/index.html')
        self.assertIn(self.listing, response.context['active_listings'])

    def test_create_listing_view_get(self):
        """Test create listing view for GET request"""
        response = self.client.get(reverse('create_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/create_listing.html')

    def test_create_listing_view_post(self):
        """Test create listing view for POST request"""
        data = {'title': 'New Listing', 'starting_bid': 200}
        response = self.client.post(reverse('create_listing'), data)
        self.assertEqual(response.status_code, 302)  # Redirects to auctions page after successful creation
        self.assertTrue(AuctionListing.objects.filter(title='New Listing').exists())

    def test_listing_detail_view(self):
        """Test listing detail view"""
        response = self.client.get(reverse('listing_detail', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing_detail.html')
        self.assertEqual(response.context['listing'], self.listing)

    def test_add_bid_view(self):
        """Test add bid view"""
        response = self.client.get(reverse('add_bid', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/add_bid.html')

        data = {'amount': 150}  # Assuming this bid is higher than the starting bid
        response = self.client.post(reverse('add_bid', args=[self.listing.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after successful bid
        self.assertTrue(Bid.objects.filter(auction_listing=self.listing, amount=150).exists())

    def test_add_comment_view(self):
        """Test add comment view"""
        response = self.client.get(reverse('add_comment', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/add_comment.html')

        data = {'content': 'Test comment'}
        response = self.client.post(reverse('add_comment', args=[self.listing.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after successful comment
        self.assertTrue(Comment.objects.filter(auction_listing=self.listing, content='Test comment').exists())

    def test_add_to_watchlist_view(self):
        """Test add to watchlist view"""
        response = self.client.post(reverse('add_to_watchlist', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after adding to watchlist
        self.assertIn(self.listing, self.user.watchlist.all())

    def test_remove_from_watchlist_view(self):
        """Test remove from watchlist view"""
        self.user.watchlist.add(self.listing)
        response = self.client.post(reverse('remove_from_watchlist', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after removing from watchlist
        self.assertNotIn(self.listing, self.user.watchlist.all())

    def test_watchlist_view(self):
        """Test watchlist view"""
        self.user.watchlist.add(self.listing)
        response = self.client.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/watchlist.html')
        self.assertIn(self.listing, response.context['watchlist'])

    def test_close_auction_view(self):
        """Test close auction view"""
        response = self.client.post(reverse('close_auction', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after closing auction
        self.assertEqual(self.listing.status, 'closed')

        # Test that only the seller can close the auction
        self.client.logout()
        buyer = User.objects.create_user(username='test_buyer', password='password')
        self.client.login(username='test_buyer', password='password')
        response = self.client.post(reverse('close_auction', args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to listing detail page after unauthorized attempt
        self.assertNotEqual(self.listing.status, 'closed')
