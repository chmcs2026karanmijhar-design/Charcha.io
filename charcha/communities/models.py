
from django.db import models
from django.contrib.auth.models import User


class Space(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    topic = models.ForeignKey(
        "questions.Topic",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spaces",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_spaces",
    )
    members = models.ManyToManyField(
        User,
        blank=True,
        related_name="joined_spaces",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
