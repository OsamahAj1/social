from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass


class Posts(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts_poster")
    text = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "text": self.text,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "likes": str(self.likes),
        }

    def __str__(self):
        return f"poster: {self.poster} date: {self.date}"

class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follwers_user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_follower")

class Likes(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="likes_post")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_user")
