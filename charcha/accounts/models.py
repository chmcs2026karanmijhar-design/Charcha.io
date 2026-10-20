
from django.db import models
from django.contrib.auth.models import User


def profile_picture_path(instance, filename):
    return f"profile_pictures/user_{instance.user.id}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.CharField(max_length=300, blank=True)
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        blank=True,
        null=True,
    )
    
    location = models.CharField(max_length=100, blank=True)
    credentials = models.CharField(max_length=150, blank=True)

    

    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )
    
    blocked_users = models.ManyToManyField(
    "self",
    symmetrical=False,
    related_name="blocked_by",
    blank=True,
)


    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()
