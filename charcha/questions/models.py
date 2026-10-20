from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    followers = models.ManyToManyField(
        User,
        blank=True,
        related_name="followed_topics",
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    title = models.CharField(max_length=250)
    body = models.TextField()
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name="questions",
    )
    image = models.ImageField(
        upload_to="question_images/",
        blank=True,
        null=True,
    )
    followers = models.ManyToManyField(
        User,
        blank=True,
        related_name="followed_questions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Answer by {self.author.username}"


class Comment(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username}"


class AnswerVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = [
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
    ]

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_votes",
    )
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "user"],
                name="unique_vote_per_user_answer",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username}: {self.value} "
            f"on answer {self.answer_id}"
        )


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"],
                name="unique_bookmark_per_user_question",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} bookmarked: "
            f"{self.question.title}"
        )



class AnswerRequest(models.Model):
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_answer_requests",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_answer_requests",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answer_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["requester", "recipient", "question"],
                name="unique_answer_request",
            ),
        ]

    def __str__(self):
        return (
            f"{self.requester.username} requested "
            f"{self.recipient.username} to answer "
            f"{self.question.title}"
        )




class Report(models.Model):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (REVIEWED, "Reviewed"),
        (DISMISSED, "Dismissed"),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_reports",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports",
    )
    reason = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.pk} — {self.status}"
