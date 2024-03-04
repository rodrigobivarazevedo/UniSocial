from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

#app_name = 'auctions'

urlpatterns = [
    path("", views.auctions, name="auctions"),
    path('create/', views.create_listing, name='create_listing'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:listing_id>/add_bid/", views.add_bid, name="add_bid"),
    path("listing/<int:listing_id>/add_comment/", views.add_comment, name="add_comment"),
    path('listing/<int:listing_id>/close_auction', views.close_auction, name='close_auction'),
    path("listing/<int:listing_id>/add_to_watchlist/", views.add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:listing_id>/remove_from_watchlist/", views.remove_from_watchlist, name="remove_from_watchlist")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
