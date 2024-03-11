
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),


    # API routes
    path('posts/', views.load_posts, name='load_posts'),
    path('posts/comments', views.comments, name='comments'),
    path('posts/likes', views.likes, name='likes'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('following/<str:username>/', views.following, name='following'),
    path('edit_profile/', views.edit_profile, name='edit_profile')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
