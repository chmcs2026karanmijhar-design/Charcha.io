
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from questions.models import Topic
from .models import Space


def spaces_list(request):
    spaces = Space.objects.select_related(
        "creator", "topic"
    ).prefetch_related("members").all()

    return render(request, "communities/spaces.html", {
        "spaces": spaces,
    })


@login_required
def create_space(request):
    topics = Topic.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        topic_id = request.POST.get("topic", "").strip()

        if not name or not description:
            messages.error(request, "Name and description are required.")
        elif len(name) > 100 or len(description) > 500:
            messages.error(request, "Please shorten your input.")
        elif Space.objects.filter(name__iexact=name).exists():
            messages.error(request, "A Space with this name already exists.")
        else:
            topic = None
            if topic_id:
                topic = get_object_or_404(Topic, pk=topic_id)

            space = Space.objects.create(
                name=name,
                description=description,
                topic=topic,
                creator=request.user,
            )
            space.members.add(request.user)
            messages.success(request, "Your Space has been created!")
            return redirect("communities:space_detail", space_id=space.pk)

    return render(request, "communities/create_space.html", {
        "topics": topics,
    })


def space_detail(request, space_id):
    space = get_object_or_404(
        Space.objects.select_related("creator", "topic").prefetch_related("members"),
        pk=space_id,
    )

    questions = space.topic.questions.select_related("author").all() if space.topic else []
    is_member = (
        request.user.is_authenticated
        and space.members.filter(pk=request.user.pk).exists()
    )

    return render(request, "communities/space_detail.html", {
        "space": space,
        "questions": questions,
        "is_member": is_member,
    })


@login_required
@require_POST
def toggle_space_membership(request, space_id):
    space = get_object_or_404(Space, pk=space_id)

    if space.members.filter(pk=request.user.pk).exists():
        space.members.remove(request.user)
        messages.success(request, f"You left {space.name}.")
    else:
        space.members.add(request.user)
        messages.success(request, f"You joined {space.name}.")

    return redirect("communities:space_detail", space_id=space.pk)
