from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta

from .models import AuctionListing, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm
from network.models import User

@login_required
def auctions(request):
    active_listings = AuctionListing.objects.filter(status='active')
    return render(request, 'auctions/index.html', {'active_listings': active_listings})

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.current_price = listing.starting_bid
            # Save the uploaded image file
            listing.save()
            return redirect(reverse('auctions'))
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})

@login_required
def listing_detail(request, listing_id):
    # Retrieve the listing object from the database
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    bidform = BidForm()
    commentform = CommentForm()
    # Check if the user is signed in and perform necessary logic for watchlist, bidding, closing auction, commenting
    return render(request, 'auctions/listing_detail.html', {'listing': listing, "bidform":bidform, "commentform":commentform})


@login_required
def add_bid(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            # Get the highest bid for the current listing
            highest_bid = listing.bids.order_by('-amount').first()
            
            # Check if the bid is higher than the starting bid and the highest bid (if it exists)
            if amount > listing.starting_bid and (not highest_bid or amount > highest_bid.amount):
                bid = Bid(amount=amount, bidder=request.user, auction_listing=listing)
                bid.save()
                
                # Update current price
                listing.current_price = amount
                listing.save()
                
                messages.success(request, 'Bid placed successfully.')
            else:
                messages.error(request, 'Bid must be greater than the starting bid and any previous bids.')
            
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = BidForm()
    
    return render(request, 'auctions/add_bid.html', {'form': form, 'listing': listing})


@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            comment = Comment(content=content, commenter=request.user, auction_listing=listing)
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = CommentForm()
    return render(request, 'auctions/add_comment.html', {'form': form, 'listing': listing})


@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    user = request.user
    user.watchlist.add(listing)
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    user = request.user
    user.watchlist.remove(listing)
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def watchlist(request):
    user = request.user
    watchlist = user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    # Ensure only the seller can close the auction
    if request.user == listing.seller:
        # Close the auction and update its status
        listing.status = 'closed'
        # Perform additional logic such as determining the highest bidder
        # and declaring them as the winner
        listing.save()

        messages.success(request, "Auction closed successfully.")
    else:
        messages.error(request, "You are not authorized to close this auction.")

    return redirect('listing_detail', listing_id=listing_id)

