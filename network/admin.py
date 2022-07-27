from django.contrib import admin
from .models import User, Posts, Followers, Likes

# Register your models here.


class PostsAdmin(admin.ModelAdmin):
    list_display = ("id", "poster", "text", "date", "likes")


class FollowersAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "follower")


class LikesAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user")


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")


admin.site.register(Posts, PostsAdmin)
admin.site.register(Followers, FollowersAdmin)
admin.site.register(Likes, LikesAdmin)
admin.site.register(User, UserAdmin)
