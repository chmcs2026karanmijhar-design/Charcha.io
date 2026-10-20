from notifications.models import Notification
from .models import (
    Question, Topic, Answer, Comment,
    AnswerVote, Bookmark, AnswerRequest, Report,
)
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.db import models

from accounts.models import Profile
from .models import Question, Topic, Answer, Comment, AnswerVote, Bookmark


def home(request):
    questions = (
        Question.objects.select_related("author")
        .prefetch_related("topics", "answers")
    )

    bookmarked_ids = set()
    unread_count = 0

    if request.user.is_authenticated:
        bookmarked_ids = set(
            Bookmark.objects.filter(user=request.user)
            .values_list("question_id", flat=True)
        )
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

    return render(request, "questions/home.html", {
        "questions": questions,
        "bookmarked_ids": bookmarked_ids,
        "unread_count": unread_count,
    })


@login_required
def following_feed(request):
    my_profile, created = Profile.objects.get_or_create(user=request.user)

    followed_user_ids = my_profile.following.values_list(
        "user_id", flat=True
    )

    questions = (
        Question.objects.filter(author_id__in=followed_user_ids)
        .select_related("author")
        .prefetch_related("topics", "answers")
        .order_by("-created_at")
    )

    bookmarked_ids = set(
        Bookmark.objects.filter(user=request.user)
        .values_list("question_id", flat=True)
    )

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return render(request, "questions/following.html", {
        "questions": questions,
        "bookmarked_ids": bookmarked_ids,
        "unread_count": unread_count,
    })


def search_questions(request):
    query = request.GET.get("q", "").strip()

    questions = Question.objects.select_related("author").prefetch_related(
        "topics", "answers"
    )

    if query:
        questions = questions.filter(
            models.Q(title__icontains=query)
            | models.Q(body__icontains=query)
        ).distinct()
    else:
        questions = questions.none()

    bookmarked_ids = set()
    unread_count = 0

    if request.user.is_authenticated:
        bookmarked_ids = set(
            Bookmark.objects.filter(user=request.user)
            .values_list("question_id", flat=True)
        )
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

    return render(request, "questions/search.html", {
        "questions": questions,
        "query": query,
        "bookmarked_ids": bookmarked_ids,
        "unread_count": unread_count,
    })


def topics_list(request):
    topics = Topic.objects.all().order_by("name")
    followed_topic_ids = set()

    if request.user.is_authenticated:
        followed_topic_ids = set(
            Topic.objects.filter(followers=request.user)
            .values_list("id", flat=True)
        )

    return render(request, "questions/topics.html", {
        "topics": topics,
        "followed_topic_ids": followed_topic_ids,
    })


def topic_detail(request, slug):
    topic = get_object_or_404(Topic, slug=slug)

    questions = (
        topic.questions.select_related("author")
        .prefetch_related("topics", "answers")
        .order_by("-created_at")
    )

    is_following = (
        request.user.is_authenticated
        and topic.followers.filter(pk=request.user.pk).exists()
    )

    return render(request, "questions/topic_detail.html", {
        "topic": topic,
        "questions": questions,
        "is_following": is_following,
        "follower_count": topic.followers.count(),
    })


@login_required
def ask_question(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        image = request.FILES.get("image")
        selected_topics = request.POST.get("topics", "").split(",")

        if not title or not body:
            messages.error(request, "Please fill in both fields.")

        elif len(title) > 250:
            messages.error(
                request,
                "Title must be 250 characters or fewer.",
            )

        elif image and image.size > 5 * 1024 * 1024:
            messages.error(
                request,
                "Image must be smaller than 5 MB.",
            )

        else:
            question = Question.objects.create(
                author=request.user,
                title=title,
                body=body,
                image=image,
            )

            for name in selected_topics:
                name = name.strip()

                if name:
                    topic, _ = Topic.objects.get_or_create(
                        name=name,
                        defaults={"slug": slugify(name) or "topic"},
                    )
                    question.topics.add(topic)

            messages.success(
                request,
                "Your question has been published!",
            )
            return redirect("questions:home")

    return render(request, "questions/ask_question.html")


def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related("author").prefetch_related(
            "topics",
            "answers__author",
            "answers__comments__author",
            "answers__votes",
        ),
        pk=question_id,
    )

    for answer in question.answers.all():
        answer.upvote_count = answer.votes.filter(
            value=AnswerVote.UPVOTE
        ).count()

        answer.downvote_count = answer.votes.filter(
            value=AnswerVote.DOWNVOTE
        ).count()

        answer.score = answer.upvote_count - answer.downvote_count
        answer.user_vote = None

        if request.user.is_authenticated:
            vote = answer.votes.filter(user=request.user).first()
            if vote:
                answer.user_vote = vote.value

    is_bookmarked = False
    is_following_question = False

    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            question=question,
        ).exists()

        is_following_question = question.followers.filter(
            pk=request.user.pk
        ).exists()



    requestable_users = User.objects.exclude(
    pk=request.user.pk
)   if request.user.is_authenticated else User.objects.none()

    return render(request, "questions/question_detail.html", {
        "question": question,
        "is_bookmarked": is_bookmarked,
        "is_following_question": is_following_question,
        "question_follower_count": question.followers.count(),
        "requestable_users": requestable_users,
    })


def notify_question_followers(
    question,
    actor,
    message,
    exclude_user_ids=None,
):
    excluded_ids = set(exclude_user_ids or [])
    excluded_ids.add(actor.pk)
    excluded_ids.add(question.author_id)

    recipient_ids = set(
        question.followers.exclude(pk__in=excluded_ids)
        .values_list("pk", flat=True)
    )

    Notification.objects.bulk_create([
        Notification(
            recipient_id=recipient_id,
            actor=actor,
            message=message,
            question=question,
        )
        for recipient_id in recipient_ids
    ])


@login_required
@require_POST
def post_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    body = request.POST.get("body", "").strip()

    if body:
        Answer.objects.create(
            question=question,
            author=request.user,
            body=body,
        )

        if question.author_id != request.user.id:
            Notification.objects.create(
                recipient=question.author,
                actor=request.user,
                message="answered your question",
                question=question,
            )

        notify_question_followers(
            question,
            request.user,
            "posted a new answer to a question you follow",
        )

        messages.success(request, "Your answer has been posted!")
    else:
        messages.error(request, "Answer cannot be empty.")

    return redirect("questions:detail", question_id=question.pk)


@login_required
@require_POST
def post_comment(request, answer_id):
    answer = get_object_or_404(
        Answer.objects.select_related("author", "question"),
        pk=answer_id,
    )

    body = request.POST.get("body", "").strip()

    if body and len(body) <= 1000:
        Comment.objects.create(
            answer=answer,
            author=request.user,
            body=body,
        )

        if answer.author_id != request.user.id:
            Notification.objects.create(
                recipient=answer.author,
                actor=request.user,
                message="commented on your answer",
                question=answer.question,
            )

        notify_question_followers(
            answer.question,
            request.user,
            "commented on an answer to a question you follow",
            exclude_user_ids=[answer.author_id],
        )

        messages.success(request, "Your comment has been added!")
    else:
        messages.error(
            request,
            "Enter a comment of up to 1000 characters.",
        )

    return redirect(
        "questions:detail",
        question_id=answer.question_id,
    )


@login_required
@require_POST
def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)

    try:
        value = int(request.POST.get("value", "0"))
    except (TypeError, ValueError):
        value = 0

    if value not in (AnswerVote.UPVOTE, AnswerVote.DOWNVOTE):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Invalid vote."}, status=400)

        messages.error(request, "Invalid vote.")
        return redirect(
            "questions:detail",
            question_id=answer.question_id,
        )

    vote, created = AnswerVote.objects.get_or_create(
        answer=answer,
        user=request.user,
        defaults={"value": value},
    )

    if not created:
        if vote.value == value:
            vote.delete()
        else:
            vote.value = value
            vote.save(update_fields=["value"])

    upvotes = answer.votes.filter(value=AnswerVote.UPVOTE).count()
    downvotes = answer.votes.filter(value=AnswerVote.DOWNVOTE).count()

    user_vote = answer.votes.filter(
        user=request.user
    ).values_list("value", flat=True).first()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "upvotes": upvotes,
            "downvotes": downvotes,
            "score": upvotes - downvotes,
            "user_vote": user_vote,
        })

    return redirect(
        "questions:detail",
        question_id=answer.question_id,
    )


@login_required
@require_POST
def toggle_bookmark(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        question=question,
    )

    if created:
        message = "Question added to your bookmarks."
        bookmarked = True
    else:
        bookmark.delete()
        message = "Question removed from your bookmarks."
        bookmarked = False

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "bookmarked": bookmarked,
            "message": message,
        })

    messages.success(request, message)
    return redirect("questions:detail", question_id=question.pk)


@login_required
def bookmarks(request):
    saved_questions = (
        Question.objects.filter(bookmarks__user=request.user)
        .select_related("author")
        .prefetch_related("topics")
        .order_by("-bookmarks__created_at")
    )

    return render(request, "questions/bookmarks.html", {
        "questions": saved_questions,
    })


@login_required
def edit_content(request, content_type, content_id):
    model_map = {
        "question": Question,
        "answer": Answer,
        "comment": Comment,
    }

    model = model_map.get(content_type)

    if model is None:
        return redirect("questions:home")

    item = get_object_or_404(model, pk=content_id)

    if item.author_id != request.user.id:
        messages.error(request, "You can only edit your own content.")
        return redirect_to_content(content_type, item)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        title = request.POST.get("title", "").strip()

        if content_type == "question":
            if not title or not body:
                messages.error(request, "Title and body are required.")
            elif len(title) > 250:
                messages.error(
                    request,
                    "Title must be 250 characters or fewer.",
                )
            else:
                item.title = title
                item.body = body
                item.save()
                messages.success(request, "Question updated!")
                return redirect_to_content(content_type, item)
        else:
            if not body:
                messages.error(request, "Content cannot be empty.")
            elif content_type == "comment" and len(body) > 1000:
                messages.error(
                    request,
                    "Comments must be 1000 characters or fewer.",
                )
            else:
                item.body = body
                item.save()
                messages.success(request, "Content updated!")
                return redirect_to_content(content_type, item)

    return render(request, "questions/edit_content.html", {
        "item": item,
        "content_type": content_type,
    })


@login_required
def delete_content(request, content_type, content_id):
    model_map = {
        "question": Question,
        "answer": Answer,
        "comment": Comment,
    }

    model = model_map.get(content_type)

    if model is None:
        return redirect("questions:home")

    item = get_object_or_404(model, pk=content_id)

    if item.author_id != request.user.id:
        messages.error(request, "You can only delete your own content.")
        return redirect_to_content(content_type, item)

    if request.method == "POST":
        if content_type == "question":
            destination = redirect("questions:home")
        else:
            question_id = (
                item.question_id
                if content_type == "answer"
                else item.answer.question_id
            )
            destination = redirect(
                "questions:detail",
                question_id=question_id,
            )

        item.delete()
        messages.success(request, "Content deleted.")
        return destination

    return render(request, "questions/delete_content.html", {
        "item": item,
        "content_type": content_type,
    })


def redirect_to_content(content_type, item):
    if content_type == "question":
        return redirect("questions:detail", question_id=item.pk)

    if content_type == "answer":
        return redirect(
            "questions:detail",
            question_id=item.question_id,
        )

    return redirect(
        "questions:detail",
        question_id=item.answer.question_id,
    )


@login_required
@require_POST
def toggle_topic_follow(request, slug):
    topic = get_object_or_404(Topic, slug=slug)

    if topic.followers.filter(pk=request.user.pk).exists():
        topic.followers.remove(request.user)
        messages.success(request, f"You unfollowed {topic.name}.")
    else:
        topic.followers.add(request.user)
        messages.success(request, f"You are now following {topic.name}.")

    return redirect("questions:topic_detail", slug=slug)


@login_required
@require_POST
def toggle_question_follow(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.author_id == request.user.id:
        messages.info(request, "You already own this question.")
    elif question.followers.filter(pk=request.user.pk).exists():
        question.followers.remove(request.user)
        messages.success(request, "You unfollowed this question.")
    else:
        question.followers.add(request.user)
        messages.success(request, "You are now following this question.")

    return redirect("questions:detail", question_id=question.pk)




@login_required
@require_POST
def request_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    recipient_id = request.POST.get("recipient_id")

    try:
        recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        messages.error(request, "Please select a valid user.")
        return redirect("questions:detail", question_id=question.pk)

    recipient = get_object_or_404(User, pk=recipient_id)

    if recipient == request.user:
        messages.error(request, "You cannot request an answer from yourself.")
    elif AnswerRequest.objects.filter(
        requester=request.user,
        recipient=recipient,
        question=question,
    ).exists():
        messages.info(request, "You have already requested this user.")
    else:
        AnswerRequest.objects.create(
            requester=request.user,
            recipient=recipient,
            question=question,
        )

        Notification.objects.create(
            recipient=recipient,
            actor=request.user,
            message=f"requested you to answer: {question.title}",
            question=question,
        )

        messages.success(
            request,
            f"Answer request sent to {recipient.username}!",
        )

    return redirect("questions:detail", question_id=question.pk)




@login_required
def search_users(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"users": []})

    users = (
        User.objects.filter(username__icontains=query)
        .exclude(pk=request.user.pk)
        .order_by("username")[:10]
    )

    return JsonResponse({
        "users": [
            {"id": user.id, "username": user.username}
            for user in users
        ]
    })



@login_required
@require_POST
def report_content(request, content_type, content_id):
    if content_type == "question":
        question = get_object_or_404(Question, pk=content_id)
        answer = None
    elif content_type == "answer":
        answer = get_object_or_404(Answer, pk=content_id)
        question = None
    else:
        messages.error(request, "Invalid content type.")
        return redirect("questions:home")

    reason = request.POST.get("reason", "").strip()

    if not reason or len(reason) > 500:
        messages.error(request, "Enter a reason of up to 500 characters.")
    else:
        Report.objects.create(
            reporter=request.user,
            question=question,
            answer=answer,
            reason=reason,
        )
        messages.success(request, "Your report has been submitted.")

    if content_type == "question":
        return redirect("questions:detail", question_id=content_id)

    return redirect("questions:detail", question_id=answer.question_id)



@login_required
@require_POST
def toggle_block(request, username):
    target = get_object_or_404(User, username=username)

    if target == request.user:
        messages.error(request, "You cannot block yourself.")
        return redirect("accounts:profile", username=username)

    my_profile, _ = Profile.objects.get_or_create(user=request.user)
    target_profile, _ = Profile.objects.get_or_create(user=target)

    if my_profile.blocked_users.filter(pk=target_profile.pk).exists():
        my_profile.blocked_users.remove(target_profile)
        messages.success(request, f"You unblocked {username}.")
    else:
        my_profile.blocked_users.add(target_profile)
        messages.success(request, f"You blocked {username}.")

    return redirect("accounts:profile", username=username)
