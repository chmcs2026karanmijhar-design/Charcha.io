
from django.urls import path
from . import views

app_name = "communities"

urlpatterns = [
    path("spaces/", views.spaces_list, name="spaces"),
    path("spaces/create/", views.create_space, name="create_space"),
    path(
        "spaces/<int:space_id>/",
        views.space_detail,
        name="space_detail",
    ),
    path(
        "spaces/<int:space_id>/join/",
        views.toggle_space_membership,
        name="toggle_space_membership",
    ),
]
