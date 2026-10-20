
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path(
        "profile/<str:username>/follow/",
        views.toggle_follow,
        name="toggle_follow",
    ),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path(
    "profile/<str:username>/block/",
    views.toggle_block,
    name="toggle_block",
),
]
