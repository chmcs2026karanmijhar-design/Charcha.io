
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = (
        Notification.objects
        .filter(recipient=request.user)
        .select_related("actor", "question")
    )

    return render(request, "notifications/list.html", {
        "notifications": notifications,
        "unread_count": notifications.filter(is_read=False).count(),
    })


@login_required
@require_POST
def mark_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    if notification.question_id:
        return redirect(
            "questions:detail",
            question_id=notification.question_id,
        )

    return redirect("notifications:list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(is_read=True)

    return redirect("notifications:list")
