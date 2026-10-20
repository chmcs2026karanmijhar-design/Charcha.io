
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect("questions:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is already taken.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            messages.success(request, "Welcome to Charcha.io!")
            return redirect("questions:home")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("questions:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("questions:home")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        location = request.POST.get("location", "").strip()
        credentials = request.POST.get("credentials", "").strip()
        picture = request.FILES.get("profile_picture")

        if len(bio) > 300:
            messages.error(request, "Bio must be 300 characters or fewer.")
        elif len(location) > 100:
            messages.error(request, "Location must be 100 characters or fewer.")
        elif len(credentials) > 150:
            messages.error(request, "Credentials must be 150 characters or fewer.")
        elif picture and picture.size > 5 * 1024 * 1024:
            messages.error(request, "Profile picture must be smaller than 5 MB.")
        elif picture and picture.content_type not in (
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
        ):
            messages.error(
                request,
                "Please upload a JPEG, PNG, WEBP, or GIF image."
            )
        else:
            profile.bio = bio
            profile.location = location
            profile.credentials = credentials

            if picture:
                profile.profile_picture = picture

            profile.save()
            messages.success(request, "Profile updated successfully!")

            return redirect(
                "accounts:profile",
                username=request.user.username,
            )

    return render(request, "accounts/edit_profile.html", {
        "profile": profile,
    })

@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("accounts:profile", username=username)

    my_profile, created = Profile.objects.get_or_create(user=request.user)
    target_profile, created = Profile.objects.get_or_create(user=target_user)

    if my_profile.following.filter(pk=target_profile.pk).exists():
        my_profile.following.remove(target_profile)
        messages.success(request, f"You unfollowed {target_user.username}.")
    else:
        my_profile.following.add(target_profile)
        messages.success(request, f"You are now following {target_user.username}.")

    return redirect("accounts:profile", username=username)


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=profile_user)

    questions = (
        profile_user.questions
        .select_related("author")
        .prefetch_related("topics", "answers")
        .order_by("-created_at")
    )

    answers = (
        profile_user.answers
        .select_related("question")
        .order_by("-created_at")
    )

    is_following = False

    if request.user.is_authenticated:
        my_profile, created = Profile.objects.get_or_create(user=request.user)
        is_following = my_profile.following.filter(pk=profile.pk).exists()

    is_blocked = False

    if request.user.is_authenticated and request.user != profile.user:
        my_profile, _ = Profile.objects.get_or_create(
        user=request.user
    )
    is_blocked = my_profile.blocked_users.filter(
        pk=profile.pk
    ).exists()

    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "profile": profile,
        "questions": questions,
        "answers": answers,
        "is_following": is_following,
        "follower_count": profile.followers.count(),
        "following_count": profile.following.count(),
        "is_blocked": is_blocked,
    })



from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Profile


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
