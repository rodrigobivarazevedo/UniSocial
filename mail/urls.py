from django.urls import path

from . import views

urlpatterns = [
    path("", views.mail, name="mail"),
    # API Routes
    path("emails", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox")
]
