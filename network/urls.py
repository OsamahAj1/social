
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("users/<str:user_name>", views.users, name="users"),
    path("following", views.following, name="following"),

    # API routes
    path("post", views.post, name="post"),
    path("follow", views.follow, name="follow"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like", views.like, name="like"),
]
