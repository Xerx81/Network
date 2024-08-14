from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writer")
    content = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Posted by {self.user} at {self.time.strftime('%d-%b-%Y, %H:%M')}"

class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.user} is followed by {self.follower}"
    
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_liked")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="liked_post")

    def __str__(self):
        return f"{self.user} liked {self.post}"